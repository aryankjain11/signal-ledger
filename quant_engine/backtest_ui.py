"""Retain immutable baseline results in the session and label changed-input snapshots."""
import json

import pandas as pd
import streamlit as st

from .saved_backtest import backtest_identity, save_backtest


def render_backtest(analysis, data, settings, symbol, adjustment):
    restriction = data.metadata.get("execution_restriction")
    st.subheader("A testable hypothesis, not a forecast")
    st.write("Fixed baseline · enter at the next observed open after a close above the prior 20 highs, above EMA50, with relative volume ≥1.2. Fix a 2 ATR stop and 2R target at entry; hold at most 10 observations.")
    st.caption("The breakout/retest observation controls do not change this strategy. Capital, risk budget, fees and slippage in the sidebar affect its simulation. One long position, no leverage; cash/risk/prior-volume caps apply. Stop wins if both barriers touch; gaps can exceed planned risk. Open positions close at dataset end.")
    if restriction:
        st.warning(restriction)
    if st.button("Run exploratory backtest", type="primary", key="run_baseline", disabled=bool(restriction)):
        st.session_state["saved_baseline_run"] = save_backtest(analysis, data, settings, symbol, adjustment)
    saved = st.session_state.get("saved_baseline_run")
    if saved is None:
        st.caption("Run the baseline to create a session record. Overlay changes and navigation retain the result; download it to keep a permanent copy.")
        return
    record = json.loads(saved.record_json)
    old = record["analysis"]
    current = saved.request_id == backtest_identity(analysis, data, settings, symbol, adjustment)
    if current:
        st.success("Saved baseline result matches the current data, replay and strategy settings.")
    else:
        st.warning("Saved baseline result is out of date for the current inputs. The previous run is retained below for reference; rerun to evaluate the current data/settings. Downloads belong to the saved run.")
    st.write(f"**Saved run:** {old['symbol']} · through {old['as_of'][:10]} · {old['rows']} observations · {old['adjustment_status']}")
    cfg = old["settings"]
    st.caption(f"Saved assumptions: capital ₹{cfg['capital']:,.0f}; risk {cfg['risk_fraction']:.1%}; charges {cfg['fee_bps']:g} bps/side; slippage {cfg['slippage_bps']:g} bps/side. Session memory only; no history database.")
    metrics = record["metrics"]
    a, b, c, d = st.columns(4)
    a.metric("Completed trades", metrics["trades"])
    b.metric("Net return", f"{metrics['total_return']:.2%}")
    c.metric("Maximum drawdown", f"{metrics['max_drawdown']:.2%}")
    d.metric("Historical win rate", f"{metrics['historical_win_fraction']:.1%}" if metrics["trades"] else "Unavailable")
    equity = pd.DataFrame(record["equity"])
    equity["date"] = pd.to_datetime(equity.date)
    st.line_chart(equity.set_index("date")[["equity"]])
    st.caption(f"Gross close-to-close buy & hold: {metrics['gross_buy_hold_return']:.2%}; different exposure and no costs. Equity includes estimated liquidation costs while a position is open.")
    if record["trades"]:
        trades=pd.DataFrame(record["trades"])
        shown=[c for c in ("entry_date","exit_date","quantity","pnl","reason","entry","stop","target","planned_risk","holding_sessions","signal_date") if c in trades]
        st.dataframe(trades[shown].rename(columns={"signal_date":"Signal close","entry_date":"Entry date","exit_date":"Exit date",
            "entry":"Entry fill","stop":"Stop threshold","target":"Target threshold","quantity":"Shares",
            "planned_risk":"Planned loss (INR)","pnl":"Net P&L (INR)","holding_sessions":"Holding observations","reason":"Exit reason"}), hide_index=True, width="stretch")
        st.download_button("Download trade ledger", saved.trades_csv, "trades.csv", "text/csv", key="saved_trades_download")
    else:
        st.info("No completed trades in this saved run. Review history and the exact baseline conditions; unavailable context is not a negative trade outcome.")
    st.download_button("Download backtest record", saved.record_json, "backtest.json", "application/json", key="saved_backtest_download")
    with st.expander("Saved strategy and calculation identity"):
        st.json({"strategy": record["strategy_version"], "request_id": saved.request_id, "recorded_at_utc": record["recorded_at_utc"], "settings": cfg})
    st.warning(metrics["validation"])
