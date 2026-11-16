"""Strategy backtest page: pick a pattern on training years, trade it across the watchlist, check held-out years."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from .event_study import StudyRules
from .event_study_ui import cohort_label
from .pooled_study import pooled_study
from .pooled_ui import PRESETS, load_universe
from .portfolio import (PortfolioRules, equal_weight_benchmark, percentile_vs_random, random_entry_control,
                        run_portfolio, split_date)
from .providers import EXCHANGE_SUFFIX
from .scanner import parse_watchlist


@st.cache_data(ttl=3600, show_spinner=False)
def _training_study(symbols, exchange, period, end, horizon):
    stocks, _ = load_universe(symbols, exchange, period)
    return pooled_study(stocks, StudyRules(horizons=(horizon,), end=end)).summary


@st.cache_data(ttl=3600, show_spinner=False)
def _backtests(symbols, exchange, period, cohort, rule_values, split):
    stocks, _ = load_universe(symbols, exchange, period)
    train_end = (pd.Timestamp(split) - pd.Timedelta(days=1)).date().isoformat()
    train_rules, test_rules = PortfolioRules(**rule_values, end=train_end), PortfolioRules(**rule_values, start=split)
    train = run_portfolio(stocks, [cohort], train_rules)
    test = run_portfolio(stocks, [cohort], test_rules)
    train.metrics["control"] = random_entry_control(stocks, train_rules, train.metrics.get("signals", 0), draws=40)
    test.metrics["control"] = random_entry_control(stocks, test_rules, test.metrics.get("signals", 0), draws=40)
    first = min(f.index[0] for f, *_ in stocks.values())
    last = max(f.index[-1] for f, *_ in stocks.values())
    bench = {"train": equal_weight_benchmark(stocks, first, pd.Timestamp(train_end)),
             "test": equal_weight_benchmark(stocks, pd.Timestamp(split), last)}
    return train, test, bench


def verdict(train, test):
    """Judge against random entries with identical rules, not against zero (a rising market lifts any long strategy)."""
    tr, te = train.metrics, test.metrics
    if not te.get("trades"):
        return "No trades in the test period", "Not enough signals after the split to judge."
    p_train = percentile_vs_random(tr.get("expectancy_r"), tr.get("control", {}))
    p_test = percentile_vs_random(te.get("expectancy_r"), te.get("control", {}))
    small = f" Only {te['trades']} test trades, so read this loosely." if te["trades"] < 20 else ""
    if p_train is None or p_test is None:
        return "Not enough data to compare", "Random-entry comparison unavailable." + small
    te_r, rnd = te["expectancy_r"], te["control"]["median_r"]
    if p_train < 80:
        return ("No clear edge, even in training",
                f"In the years it was chosen from, it beat only {p_train:.0f}% of random-entry runs with the same rules. "
                "Any profit there is mostly the market rising, not the pattern." + small)
    if p_test >= 80:
        return ("Held up out of sample",
                f"On unseen years it beat {p_test:.0f}% of random-entry runs ({te_r:+.2f}R per trade vs {rnd:+.2f}R typical for random entries). "
                "Worth re-testing on other stocks and periods before trusting it." + small)
    if te_r > rnd:
        return ("Weakened out of sample",
                f"Better than typical random entries on unseen years ({te_r:+.2f}R vs {rnd:+.2f}R) but only beat {p_test:.0f}% of them: "
                "within the range luck produces." + small)
    return ("Failed out of sample",
            f"Beat {p_train:.0f}% of random entries in training but only {p_test:.0f}% on unseen years ({te_r:+.2f}R vs {rnd:+.2f}R). "
            "Typical of a pattern that fit past noise." + small)


def _fmt(metrics):
    def pct(x, d=1):
        return "—" if x is None else f"{100 * x:+.{d}f}%"
    def num(x, f="{:.2f}"):
        return "—" if x is None else f.format(x)
    return {"Period": f"{metrics.get('start', '—')} → {metrics.get('end', '—')}",
            "Trades": metrics.get("trades", 0), "Signals skipped (slots full / held)": metrics.get("skipped", 0),
            "Total return": pct(metrics.get("total_return")), "Annualized (CAGR)": pct(metrics.get("cagr")),
            "Max drawdown": pct(metrics.get("max_drawdown")), "Sharpe (daily, annualized)": num(metrics.get("sharpe")),
            "Win rate": "—" if metrics.get("win_rate") is None else f"{100 * metrics['win_rate']:.0f}%",
            "Profit factor": num(metrics.get("profit_factor")), "Avg result per trade (R)": num(metrics.get("expectancy_r"), "{:+.2f}"),
            "Avg holding (sessions)": num(metrics.get("avg_sessions"), "{:.1f}"),
            "Time invested": "—" if metrics.get("exposure") is None else f"{100 * metrics['exposure']:.0f}% of days",
            "Random entries, same rules (R/trade)": _control_text(metrics.get("control", {})),
            "Beats random entries": "—" if percentile_vs_random(metrics.get("expectancy_r"), metrics.get("control", {})) is None
                                     else f"{percentile_vs_random(metrics.get('expectancy_r'), metrics['control']):.0f}% of runs"}


def _control_text(c):
    if not c.get("draws"):
        return "—"
    return f"{c['median_r']:+.2f} typical ({c['low_r']:+.2f} to {c['high_r']:+.2f})"


def equity_figure(train, test, bench, capital):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Training years (pattern chosen here)", "Test years (unseen)"), horizontal_spacing=0.06)
    for col, (result, b) in enumerate(((train, bench["train"]), (test, bench["test"])), start=1):
        if not result.equity.empty:
            fig.add_trace(go.Scatter(x=result.equity.index, y=result.equity.equity / capital, name="Strategy",
                                     line=dict(color="#36d6a4", width=2), showlegend=col == 1), row=1, col=col)
        if len(b):
            fig.add_trace(go.Scatter(x=b.index, y=b, name="Equal-weight buy & hold (gross)",
                                     line=dict(color="#8fa3c0", width=1.3, dash="dot"), showlegend=col == 1), row=1, col=col)
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="#101a2b", plot_bgcolor="#101a2b",
                      margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.12))
    fig.update_yaxes(title_text="Growth of 1", row=1, col=1)
    return fig


def render_portfolio_backtest():
    st.title("Strategy backtest")
    st.caption("Trade one pattern across a whole watchlist with entries, stops, targets, position limits and costs. "
               "The pattern is chosen using only the older **training** years; the recent **test** years are kept unseen "
               "to check whether the edge survives on data it was not picked from.")
    preset = st.segmented_control("Watchlist", list(PRESETS), default=list(PRESETS)[0], key="bt_preset",
                                  persist_state="session") or list(PRESETS)[0]
    default_text = ", ".join(PRESETS[preset]) if preset != "Custom list" else st.session_state.get(
        "bt_custom", "RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, SBIN, LT, ITC")
    with st.form("bt_universe_form"):
        text = st.text_area("Symbols (max 100)", default_text, height=70, key=f"bt_text_{preset}", disabled=preset != "Custom list")
        c1, c2, c3 = st.columns(3)
        exchange = c1.selectbox("Exchange", list(EXCHANGE_SUFFIX), key="bt_exchange")
        period = c2.selectbox("History", ["5 years", "10 years"], key="bt_period",
                              help="Longer history leaves more training years and a longer unseen test.")
        test_share = c3.slider("Test years: last … of history", 20, 50, 30, 5, format="%d%%", key="bt_test_share")
        load = st.form_submit_button("Load watchlist", type="primary", icon=":material/download:")
    if preset == "Custom list":
        st.session_state["bt_custom"] = text
    symbols = tuple(parse_watchlist(text))
    if load:
        st.session_state["bt_universe"] = (symbols, exchange, period, test_share)
    universe = st.session_state.get("bt_universe")
    if not universe:
        st.info("Load a watchlist to begin. The NIFTY 50 with 5 years takes about a minute the first time "
                "(it is shared with Pattern research, so it is instant if you ran that already).", icon=":material/download:")
        return
    symbols, exchange, period, test_share = universe
    with st.spinner(f"Loading {len(symbols)} stocks…"):
        stocks, failures = load_universe(symbols, exchange, period)
    if not stocks:
        st.error("No stock could be loaded. Check the symbols or your connection.")
        return
    split = split_date(stocks, test_share / 100)
    st.success(f"{len(stocks)} stocks loaded · training before **{split}** · test from **{split}**"
               + (f" · {len(failures)} could not be fetched" if failures else ""), icon=":material/check_circle:")

    st.markdown("### 1 · Choose a pattern, using training years only")
    horizon = st.segmented_control("Judge patterns over", [5, 10, 20], default=10, key="bt_horizon",
                                   format_func=lambda h: f"{h} sessions") or 10
    train_study_end = (pd.Timestamp(split) - pd.Timedelta(days=int(horizon * 1.6) + 5)).date().isoformat()
    with st.spinner("Measuring patterns in the training years…"):
        summary = _training_study(symbols, exchange, period, train_study_end, horizon)
    longs = summary.loc[summary.cohort.str.endswith("+1") & summary.difference_from_baseline.notna()].copy()
    if longs.empty:
        st.warning("No bullish pattern had enough training-period events. Load more stocks or more history.")
        return
    longs["has_range"] = longs.difference_low.notna()
    longs = longs.sort_values(["has_range", "difference_from_baseline"], ascending=[False, False])
    st.caption(f"Bullish patterns only (long trades). Training outcomes measured up to {train_study_end}, so no "
               "training measurement reaches into the test years. Ranked by edge over ordinary days.")
    st.dataframe(pd.DataFrame({
        "Pattern": longs.cohort.map(cohort_label), "Training events": longs.events, "Stocks": longs.stocks,
        f"Mean move % ({horizon}s)": longs.mean_return * 100, "vs ordinary days (pp)": longs.difference_from_baseline * 100,
        "90% range": [f"{lo * 100:+.2f} to {hi * 100:+.2f}" if pd.notna(lo) else "too few" for lo, hi in zip(longs.difference_low, longs.difference_high)],
        "Note": longs.sample_note}), hide_index=True, width="stretch", height=280,
        column_config={c: st.column_config.NumberColumn(format="%+.2f") for c in (f"Mean move % ({horizon}s)", "vs ordinary days (pp)")})
    options = longs.cohort.tolist()
    cohort = st.selectbox("Pattern to trade", options, format_func=cohort_label, key="bt_cohort",
                          help="Defaults to the pattern with the best training-period edge that has a range.")

    st.markdown("### 2 · Trading rules")
    with st.form("bt_rules_form"):
        r1, r2, r3, r4 = st.columns(4)
        capital = r1.number_input("Starting capital (₹)", 100_000, 100_000_000, 1_000_000, 100_000, key="bt_capital")
        risk = r2.number_input("Risk per trade (% of equity)", 0.1, 5.0, 0.5, 0.1, key="bt_risk")
        slots = r3.number_input("Max open positions", 1, 50, 5, key="bt_slots")
        cap = r4.number_input("Max per position (% of equity)", 5.0, 100.0, 25.0, 5.0, key="bt_cap")
        r5, r6, r7, r8 = st.columns(4)
        stop_atr = r5.number_input("Stop (× ATR14 below entry)", 0.5, 6.0, 2.0, 0.25, key="bt_stop")
        rr = r6.number_input("Target (× stop distance)", 0.5, 6.0, 2.0, 0.25, key="bt_rr")
        hold = r7.number_input("Max holding (sessions)", 1, 120, int(horizon * 2), key="bt_hold")
        fees = r8.number_input("Costs per side (bps, fees + slippage)", 0.0, 100.0, 15.0, 1.0, key="bt_costs",
                               help="Split as 2/3 charges, 1/3 slippage. 15 bps per side ≈ 0.3% round trip.")
        go_run = st.form_submit_button("Run backtest on training and test years", type="primary", icon=":material/play_arrow:")
    rule_values = dict(capital=float(capital), risk_pct=float(risk), max_positions=int(slots), max_position_pct=float(cap),
                       stop_atr=float(stop_atr), reward_risk=float(rr), max_hold=int(hold),
                       fee_bps=float(fees) * 2 / 3, slippage_bps=float(fees) / 3)
    if go_run:
        st.session_state["bt_last"] = (cohort, rule_values, split, universe)
    last = st.session_state.get("bt_last")
    if not last or last[3] != universe:
        st.caption("Set the rules and run. Entry is the next open after the pattern is known; exits use stop, target or the holding limit.")
        return
    cohort, rule_values, split, _ = last
    with st.spinner("Simulating trades…"):
        train, test, bench = _backtests(symbols, exchange, period, cohort, rule_values, split)

    st.markdown(f"### 3 · Result: {cohort_label(cohort)}")
    title, detail = verdict(train, test)
    tone = st.success if title.startswith("Held") else st.warning if title.startswith(("Weakened", "No trades")) else st.error
    tone(f"**{title}.** {detail}")
    table = pd.DataFrame({"Training years": _fmt(train.metrics), "Test years (unseen)": _fmt(test.metrics)})
    st.dataframe(table, width="stretch", height=528)
    st.plotly_chart(equity_figure(train, test, bench, rule_values["capital"]), width="stretch")
    st.caption("**The test that matters is 'Beats random entries'**: the same stocks, rules, costs and number of signals, "
               "but entered on random days (40 runs). Beating zero is not enough in a rising market. Strategy equity is "
               "after costs; the dotted line is gross equal-weight buy-and-hold for context. R = profit or loss ÷ planned loss at the stop.")
    tabs = st.tabs(["Test-year trades", "Training-year trades", "Skipped signals"])
    for tab, frame in zip(tabs, (test.trades, train.trades, pd.concat([train.skipped, test.skipped], ignore_index=True))):
        with tab:
            if frame.empty:
                st.caption("None.")
            else:
                st.dataframe(frame.drop(columns=[c for c in ("proceeds", "cohort") if c in frame]), hide_index=True, width="stretch",
                             column_config={c: st.column_config.NumberColumn(format="%.2f") for c in ("entry", "exit", "stop", "target", "pnl", "r_multiple", "return_pct", "rvol") if c in frame})
    st.download_button("Download test-year trades (CSV)", test.trades.to_csv(index=False), "signal-ledger-test-trades.csv", "text/csv")
    with st.expander("Rules, assumptions and limits"):
        st.markdown(
            "- **Entry:** next session's open after the pattern's knowledge close, plus slippage. **Long only.**\n"
            "- **Exit:** stop (ATR multiple below entry), target (multiple of the stop distance), or close of the last holding session. "
            "An opening gap through the stop exits at the open; if a bar touches both, the stop is assumed first.\n"
            "- **Sizing:** risk % of current equity ÷ (entry − stop, with costs), capped by position % and cash; one position per stock.\n"
            "- **When slots are full:** signals are taken in order of relative volume at the signal close (known in advance); the rest are listed as skipped.\n"
            "- **Out-of-sample:** the pattern table uses outcomes measured only up to the training cut-off; the test years are never used to choose. "
            "If you change the pattern or rules after looking at the test result, the test years stop being unseen. Treat repeated tweaking as fitting.\n"
            "- **Not modelled:** dividends, taxes, intraday order-book liquidity, circuit limits, and stocks that left the index (today's list applied to the past flatters results).")
