"""Paper trading: record a plan now, judge it later only against sessions that came after it.

A plan is frozen when recorded. Its rules mirror the backtests: entry at the open of the first
session after the signal (plus slippage), stop = entry - stop_atr x ATR14 (ATR known at the
signal close), target = entry + reward_risk x stop distance, holding limit in sessions, costs per
side. Evaluation is a pure function of the plan and later daily bars, so re-running it can
never change what a past session decided, and it cannot see anything before the plan existed.
"""
from __future__ import annotations

import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

IST = ZoneInfo("Asia/Kolkata")
MAX_RECORDING_LAG_DAYS = 4  # a Friday signal can still be recorded over the weekend
OPEN_STATES = ("Waiting for entry", "Open")


@dataclass(frozen=True)
class PaperPlan:
    symbol: str
    provider_symbol: str
    exchange: str
    signal_date: str          # last completed session used for the decision (YYYY-MM-DD)
    signal_close: float
    atr: float
    stop_atr: float = 2.0
    reward_risk: float = 2.0
    max_hold: int = 20
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    source: str = "Manual"    # Analyze / Scanner / Strategy backtest / Manual
    pattern: str = ""
    ledger: str = "default"
    note: str = ""
    snapshot: dict = field(default_factory=dict)  # context at recording (verdict, alignment, RSI...)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(IST).isoformat(timespec="seconds"))

    def __post_init__(self):
        checks = [(bool(self.symbol and self.provider_symbol), "Symbol required."),
                  (math.isfinite(self.atr) and self.atr > 0, "ATR must be positive."),
                  (math.isfinite(self.signal_close) and self.signal_close > 0, "Signal close must be positive."),
                  (0.25 <= self.stop_atr <= 10, "Stop must be 0.25–10 ATR."),
                  (0.25 <= self.reward_risk <= 10, "Reward/risk must be 0.25–10."),
                  (1 <= self.max_hold <= 252, "Holding limit must be 1–252 sessions."),
                  (self.stop_atr * self.atr < self.signal_close, "Stop distance exceeds the price.")]
        for ok, message in checks:
            if not ok:
                raise ValueError(message)
        pd.Timestamp(self.signal_date)  # raises on a malformed date

    def as_row(self) -> dict:
        row = asdict(self)
        row["snapshot"] = dict(self.snapshot)
        return row


def check_recordable(signal_date: str, last_bar_date: str, today: date | None = None, replay: bool = False) -> str | None:
    """Return a reason the plan may NOT be recorded, or None. Prevents hindsight 'paper trades'."""
    today = today or datetime.now(IST).date()
    if replay:
        return "Replay is active. Paper trades can only be recorded on the latest session, not a past one."
    if signal_date != last_bar_date:
        return "Paper trades are recorded on the latest completed session only."
    lag = (today - pd.Timestamp(signal_date).date()).days
    if lag > MAX_RECORDING_LAG_DAYS:
        return (f"The latest session in this data is {signal_date}, {lag} days ago. Recording it now would be "
                "hindsight. Refresh the data and record on the newest session.")
    if lag < 0:
        return "Signal date is in the future."
    return None


def evaluate(plan: PaperPlan, bars: pd.DataFrame) -> dict:
    """Outcome so far, using only completed daily bars dated after the signal."""
    fee, slip = plan.fee_bps / 10_000, plan.slippage_bps / 10_000
    after = bars.loc[bars.index > pd.Timestamp(plan.signal_date)].sort_index()
    base = {"status": "Waiting for entry", "entry_date": None, "entry_price": None, "stop": None, "target": None,
            "exit_date": None, "exit_price": None, "reason": None, "r_multiple": None, "unrealized_r": None,
            "mfe_r": None, "mae_r": None, "sessions": 0,
            "checked_through": bars.index[-1].date().isoformat() if len(bars) else None}
    if after.empty:
        return base
    first = after.iloc[0]
    entry = float(first.open) * (1 + slip)
    distance = plan.stop_atr * plan.atr
    stop, target = entry - distance, entry + plan.reward_risk * distance
    if stop <= 0:
        return {**base, "status": "Invalid", "reason": "Stop at or below zero"}
    planned_loss = entry * (1 + fee) - stop * (1 - slip) * (1 - fee)

    def r_of(price):
        return (price * (1 - slip) * (1 - fee) - entry * (1 + fee)) / planned_loss

    out = {**base, "status": "Open", "entry_date": after.index[0].date().isoformat(), "entry_price": entry,
           "stop": stop, "target": target}
    best = worst = entry
    for k, (day, bar) in enumerate(after.iterrows()):
        o, h, l, c = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
        price = reason = None
        if k > 0 and o <= stop:
            price, reason = o, "Gap through stop"
        elif k > 0 and o >= target:
            price, reason = o, "Gap above target"
        elif l <= stop:
            price, reason = stop, "Stop (both touched; stop first)" if h >= target else "Stop"
        elif h >= target:
            price, reason = target, "Target"
        elif k + 1 >= plan.max_hold:
            price, reason = c, "Holding limit"
        # Excursions: the bar's range, but on the exit bar only up to the exit (the trade ended there).
        if reason in ("Gap through stop", "Gap above target"):
            best, worst = max(best, o), min(worst, o)
        elif reason is not None and reason != "Holding limit":
            best, worst = max(best, min(h, target)), min(worst, max(l, stop))
        else:
            best, worst = max(best, h), min(worst, l)
        out["sessions"] = k + 1
        out["mfe_r"], out["mae_r"] = (best - entry) / distance, (worst - entry) / distance
        if price is not None:
            label = {"Target": "Target hit", "Gap above target": "Target hit", "Holding limit": "Expired"}.get(reason, "Stopped out")
            return {**out, "status": label, "exit_date": day.date().isoformat(), "exit_price": price * (1 - slip),
                    "reason": reason, "r_multiple": r_of(price)}
        out["unrealized_r"] = r_of(c)
    return out


def ledger_stats(rows: pd.DataFrame) -> dict:
    """Summary of a ledger (rows = plans joined with their latest evaluation). Voided trades excluded."""
    if rows.empty:
        return {"recorded": 0}
    live = rows.loc[~rows.get("voided", pd.Series(False, index=rows.index)).fillna(False).astype(bool)]
    closed = live.loc[live.r_multiple.notna()]
    r = closed.r_multiple.astype(float)
    return {"recorded": int(len(live)), "voided": int(len(rows) - len(live)),
            "waiting": int(live.status.eq("Waiting for entry").sum()), "open": int(live.status.eq("Open").sum()),
            "closed": int(len(closed)), "wins": int((r > 0).sum()),
            "win_rate": float((r > 0).mean()) if len(r) else None,
            "avg_r": float(r.mean()) if len(r) else None, "total_r": float(r.sum()) if len(r) else 0.0,
            "median_sessions": float(closed.sessions.median()) if len(closed) else None}
