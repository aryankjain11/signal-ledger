"""Portfolio backtest of one pattern type across a watchlist, with an out-of-sample split.

Conventions match the single-stock backtest (`strategy.backtest`):
- the pattern is known at the close of its knowledge bar; entry is the NEXT session's open
  plus slippage; costs are charged per side;
- stop = entry - k x ATR14 (ATR known at the signal close); target = entry + R x stop distance;
- an adverse opening gap exits at the open; when one bar touches both stop and target the
  stop is assumed first; otherwise exit at the holding limit's close;
- open positions are valued at close net of exit slippage and charges.

Portfolio rules added here:
- long only (cash equities; shorting overnight is not generally available);
- risk per trade is a % of current equity; position value is capped as a % of equity and by
  available cash; at most N positions at once; one position per stock;
- when more signals arrive than free slots, they are taken in a fixed, pre-known order
  (higher relative volume at the signal close first, then symbol) and the rest are recorded
  as skipped, never silently dropped.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .event_study import occurrence_ledger


@dataclass(frozen=True)
class PortfolioRules:
    capital: float = 1_000_000.0
    risk_pct: float = 0.5          # % of equity at risk per trade
    max_positions: int = 5
    max_position_pct: float = 25.0  # % of equity per position
    stop_atr: float = 2.0
    reward_risk: float = 2.0
    max_hold: int = 20
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    start: str | None = None        # first signal date considered (YYYY-MM-DD)
    end: str | None = None          # last signal date considered

    def __post_init__(self):
        checks = [(self.capital > 0, "Capital must be positive."),
                  (0 < self.risk_pct <= 5, "Risk per trade must be 0–5% of equity."),
                  (1 <= self.max_positions <= 50, "Max positions must be 1–50."),
                  (0 < self.max_position_pct <= 100, "Position cap must be 0–100% of equity."),
                  (0.25 <= self.stop_atr <= 10, "Stop distance must be 0.25–10 ATR."),
                  (0.25 <= self.reward_risk <= 10, "Reward/risk must be 0.25–10."),
                  (1 <= self.max_hold <= 252, "Holding limit must be 1–252 sessions."),
                  (0 <= self.fee_bps <= 200 and 0 <= self.slippage_bps <= 200, "Costs must be 0–200 bps per side.")]
        for ok, message in checks:
            if not ok:
                raise ValueError(message)


@dataclass
class PortfolioResult:
    trades: pd.DataFrame
    equity: pd.DataFrame
    skipped: pd.DataFrame
    metrics: dict
    rules: dict


def collect_signals(stocks: dict, cohorts) -> pd.DataFrame:
    """Eligible, long-direction occurrences of the chosen cohorts, one per stock per knowledge date."""
    rows = []
    for symbol, (frame, events, *_rest) in stocks.items():
        ledger = occurrence_ledger(frame, events)
        chosen = ledger.loc[ledger.eligible & ledger.cohort.isin(cohorts) & ledger.direction.eq(1)]
        for index in sorted(set(chosen["index"])):
            if index + 1 >= len(frame):
                continue  # knowable on the last bar: no next open to trade yet
            atr = float(frame.atr_14.iloc[index])
            if not math.isfinite(atr) or atr <= 0:
                continue
            rvol = frame.relative_volume.iloc[index]
            rows.append({"symbol": symbol, "signal_date": frame.index[index], "entry_date": frame.index[index + 1],
                         "signal_index": index, "atr": atr, "rvol": float(rvol) if pd.notna(rvol) else -1.0,
                         "cohort": chosen.loc[chosen["index"].eq(index), "cohort"].iloc[0]})
    columns = ["symbol", "signal_date", "entry_date", "signal_index", "atr", "rvol", "cohort"]
    return pd.DataFrame(rows, columns=columns).sort_values(["entry_date", "rvol", "symbol"], ascending=[True, False, True]).reset_index(drop=True)


def run_portfolio(stocks: dict, cohorts, rules: PortfolioRules | None = None, signals: pd.DataFrame | None = None) -> PortfolioResult:
    rules = rules or PortfolioRules()
    fee, slip = rules.fee_bps / 10_000, rules.slippage_bps / 10_000
    signals = collect_signals(stocks, tuple(cohorts)) if signals is None else signals
    # Priority is enforced here, whatever the source of the signals.
    signals = signals.sort_values(["entry_date", "rvol", "symbol"], ascending=[True, False, True], kind="stable")
    if rules.start:
        signals = signals.loc[signals.signal_date >= pd.Timestamp(rules.start)]
    if rules.end:
        signals = signals.loc[signals.signal_date <= pd.Timestamp(rules.end)]
    frames = {s: v[0] for s, v in stocks.items()}
    bars = {s: dict(zip(f.index, zip(f.open.to_numpy(float), f.high.to_numpy(float), f.low.to_numpy(float), f.close.to_numpy(float))))
            for s, f in frames.items()}
    lo = pd.Timestamp(rules.start) if rules.start else min(f.index[0] for f in frames.values())
    hi = pd.Timestamp(rules.end) + pd.Timedelta(days=int(rules.max_hold * 1.6) + 10) if rules.end else None
    calendar = sorted({d for f in frames.values() for d in f.index if d >= lo and (hi is None or d <= hi)})
    by_date = {d: list(g.itertuples(index=False)) for d, g in signals.groupby("entry_date")}
    cash, open_pos, trades, skipped, curve = rules.capital, {}, [], [], []
    last_close = {}
    for day in calendar:
        # 1. exits for positions already held (entry-day exits are handled after entry below)
        for symbol in list(open_pos):
            _maybe_exit(open_pos, symbol, bars[symbol], day, rules, fee, slip, trades, entry_day=False)
            if symbol not in open_pos:
                cash += trades[-1]["proceeds"]
        # 2. entries at today's open from yesterday's (pre-known) signals
        equity_now = cash + sum(p["quantity"] * last_close.get(s, p["entry"]) * (1 - slip) * (1 - fee) for s, p in open_pos.items())
        for sig in by_date.get(day, ()):
            symbol = sig.symbol
            if symbol in open_pos:
                skipped.append({**_sig(sig), "reason": "Already holding this stock"})
                continue
            if len(open_pos) >= rules.max_positions:
                skipped.append({**_sig(sig), "reason": "All position slots full"})
                continue
            entry = bars[symbol][day][0] * (1 + slip)
            distance = rules.stop_atr * sig.atr
            stop, target = entry - distance, entry + rules.reward_risk * distance
            if stop <= 0:
                skipped.append({**_sig(sig), "reason": "Stop below zero"})
                continue
            risk_budget = equity_now * rules.risk_pct / 100
            per_share_loss = entry * (1 + fee) - stop * (1 - slip) * (1 - fee)
            qty = math.floor(min(risk_budget / per_share_loss,
                                 equity_now * rules.max_position_pct / 100 / (entry * (1 + fee)),
                                 cash / (entry * (1 + fee))))
            if qty < 1:
                skipped.append({**_sig(sig), "reason": "Not enough cash for one share"})
                continue
            cash -= qty * entry * (1 + fee)
            open_pos[symbol] = {"symbol": symbol, "cohort": sig.cohort, "signal_date": sig.signal_date, "entry_date": day,
                                "entry": entry, "stop": stop, "target": target, "quantity": qty, "held": 0,
                                "planned_loss": qty * per_share_loss, "risk_per_share": distance}
            _maybe_exit(open_pos, symbol, bars[symbol], day, rules, fee, slip, trades, entry_day=True)
            if symbol not in open_pos:
                cash += trades[-1]["proceeds"]
        # 3. mark to market
        for symbol, table in bars.items():
            bar = table.get(day)
            if bar is not None:
                last_close[symbol] = bar[3]
        value = sum(p["quantity"] * last_close[s] * (1 - slip) * (1 - fee) for s, p in open_pos.items())
        curve.append({"date": day, "equity": cash + value, "positions": len(open_pos), "invested": value})
    for symbol in list(open_pos):  # end of data: close at the last known close, labelled
        p, price = open_pos.pop(symbol), last_close[symbol]
        _record(trades, p, calendar[-1], price * (1 - slip), "End of data", fee)
        cash += trades[-1]["proceeds"]
    equity = pd.DataFrame(curve).set_index("date") if curve else pd.DataFrame(columns=["equity"])
    trade_frame = pd.DataFrame(trades)
    return PortfolioResult(trade_frame, equity, pd.DataFrame(skipped), _metrics(trade_frame, equity, rules, len(signals), len(skipped)), asdict(rules))


def _sig(sig):
    return {"symbol": sig.symbol, "signal_date": sig.signal_date, "entry_date": sig.entry_date, "rvol": sig.rvol}


def _maybe_exit(open_pos, symbol, table, day, rules, fee, slip, trades, entry_day):
    bar = table.get(day)
    if bar is None:
        return  # no bar for this stock today (holiday/suspension): nothing happens
    p = open_pos[symbol]
    o, h, l, c = bar
    p["held"] += 0 if entry_day else 1
    price = reason = None
    if not entry_day and o <= p["stop"]:
        price, reason = o, "Gap through stop"
    elif not entry_day and o >= p["target"]:
        price, reason = o, "Gap above target"
    elif l <= p["stop"]:
        price, reason = p["stop"], "Stop (both touched; stop first)" if h >= p["target"] else "Stop"
    elif h >= p["target"]:
        price, reason = p["target"], "Target"
    elif p["held"] + 1 >= rules.max_hold:
        price, reason = c, "Holding limit"
    if price is not None:
        open_pos.pop(symbol)
        _record(trades, p, day, price * (1 - slip), reason, fee)


def _record(trades, p, day, exit_fill, reason, fee):
    proceeds = p["quantity"] * exit_fill * (1 - fee)
    cost = p["quantity"] * p["entry"] * (1 + fee)
    pnl = proceeds - cost
    trades.append({"symbol": p["symbol"], "cohort": p["cohort"], "signal_date": p["signal_date"].date().isoformat(),
                   "entry_date": p["entry_date"].date().isoformat(), "exit_date": day.date().isoformat(),
                   "entry": p["entry"], "exit": exit_fill, "stop": p["stop"], "target": p["target"],
                   "quantity": p["quantity"], "pnl": pnl, "proceeds": proceeds,
                   "r_multiple": pnl / p["planned_loss"] if p["planned_loss"] > 0 else np.nan,
                   "return_pct": 100 * pnl / cost, "sessions": p["held"] + 1, "reason": reason})


def _metrics(trades, equity, rules, signals, skipped):
    if equity.empty:
        return {"trades": 0, "signals": signals, "skipped": skipped}
    eq = equity.equity
    peak = eq.cummax().clip(lower=rules.capital)
    dd = eq / peak - 1
    daily = eq.pct_change().dropna()
    years = max((eq.index[-1] - eq.index[0]).days / 365.25, 1e-9)
    total = eq.iloc[-1] / rules.capital - 1
    pnl = trades.pnl if not trades.empty else pd.Series(dtype=float)
    losses = -pnl[pnl < 0].sum()
    sharpe = float(daily.mean() / daily.std() * np.sqrt(252)) if len(daily) > 20 and daily.std() > 0 else None
    return {
        "trades": int(len(trades)), "signals": int(signals), "skipped": int(skipped),
        "final_equity": float(eq.iloc[-1]), "total_return": float(total),
        "cagr": float((1 + total) ** (1 / years) - 1) if years >= 0.5 and total > -1 else None,
        "max_drawdown": float(dd.min()), "sharpe": sharpe,
        "win_rate": float((pnl > 0).mean()) if len(pnl) else None,
        "profit_factor": float(pnl[pnl > 0].sum() / losses) if losses > 0 else None,
        "expectancy_r": float(trades.r_multiple.mean()) if len(pnl) else None,
        "avg_sessions": float(trades.sessions.mean()) if len(pnl) else None,
        "exposure": float((equity.positions > 0).mean()),
        "avg_invested_pct": float((equity.invested / eq).mean() * 100),
        "start": eq.index[0].date().isoformat(), "end": eq.index[-1].date().isoformat(),
    }


def equal_weight_benchmark(stocks: dict, start, end) -> pd.Series:
    """Gross equal-weight buy-and-hold of the same stocks over the same window (no costs, no rebalancing)."""
    series = []
    for frame, *_ in stocks.values():
        closes = frame.close.loc[(frame.index >= start) & (frame.index <= end)]
        if len(closes) > 1:
            series.append(closes / closes.iloc[0])
    if not series:
        return pd.Series(dtype=float)
    return pd.concat(series, axis=1).ffill().mean(axis=1)


def split_date(stocks: dict, test_fraction: float = 0.3) -> str:
    """Default boundary: the last `test_fraction` of the common calendar is held out."""
    days = sorted({d for f, *_ in stocks.values() for d in f.index})
    return days[int(len(days) * (1 - test_fraction))].date().isoformat()


def random_entry_control(stocks: dict, rules: PortfolioRules, n_signals: int, draws: int = 30, seed: int = 11) -> dict:
    """Same rules, same number of signals, but entry dates drawn at random from the same stocks and period.

    Answers "is this pattern better than entering at random?", which separates a pattern's edge from
    simply being long in a rising market. Signals are drawn uniformly over all (stock, session) pairs
    with a valid ATR inside the period; one draw = one full portfolio simulation.
    """
    pool = []
    for symbol, (frame, *_rest) in stocks.items():
        atr = frame.atr_14.to_numpy(float)
        dates = frame.index
        for i in range(len(frame) - 1):
            if not np.isfinite(atr[i]) or atr[i] <= 0:
                continue
            if rules.start and dates[i] < pd.Timestamp(rules.start):
                continue
            if rules.end and dates[i] > pd.Timestamp(rules.end):
                continue
            pool.append((symbol, dates[i], dates[i + 1], i, float(atr[i])))
    if n_signals < 1 or len(pool) < n_signals:
        return {"draws": 0}
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(draws):
        picks = rng.choice(len(pool), size=n_signals, replace=False)
        sigs = pd.DataFrame([{"symbol": pool[k][0], "signal_date": pool[k][1], "entry_date": pool[k][2],
                              "signal_index": pool[k][3], "atr": pool[k][4], "rvol": float(rng.random()), "cohort": "random"}
                             for k in picks])
        m = run_portfolio(stocks, ["random"], rules, sigs).metrics
        results.append((m.get("expectancy_r"), m.get("total_return")))
    r = np.array([x for x, _ in results if x is not None], float)
    ret = np.array([y for _, y in results if y is not None], float)
    return {"draws": len(r), "median_r": float(np.median(r)), "low_r": float(np.quantile(r, 0.1)), "high_r": float(np.quantile(r, 0.9)),
            "median_return": float(np.median(ret)), "r_values": r.tolist()}


def percentile_vs_random(value, control) -> float | None:
    if value is None or not control.get("draws"):
        return None
    values = np.array(control["r_values"])
    return float((values < value).mean() * 100)
