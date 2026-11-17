"""Paper trades page and the shared 'record a paper trade' helper used by Analyze, Scanner and Strategy backtest."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .data import load_bars
from .paper import OPEN_STATES, PaperPlan, check_recordable, evaluate, ledger_stats
from .paper_store import PaperStore, database_url
from .providers import fetch_daily

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = dict(stop_atr=2.0, reward_risk=2.0, max_hold=20)


@st.cache_resource(show_spinner=False)
def get_store():
    url, label = database_url(ROOT)
    return PaperStore(url), label


def current_ledger() -> str:
    return (st.session_state.get("paper_ledger") or "default").strip()[:60] or "default"


def record(plan_values: dict, last_bar_date: str, replay: bool = False) -> tuple[bool, str]:
    """Validate timing, build the frozen plan, store it. Returns (ok, message)."""
    problem = check_recordable(plan_values["signal_date"], last_bar_date, replay=replay)
    if problem:
        return False, problem
    try:
        plan = PaperPlan(**{**plan_values, "ledger": current_ledger()})
    except ValueError as exc:
        return False, str(exc)
    store, _ = get_store()
    if not store.add(plan):
        return False, f"{plan.symbol} for {plan.signal_date} is already in the '{plan.ledger}' ledger."
    return True, f"Recorded {plan.symbol}: enters at the next open after {plan.signal_date}. Track it under Paper trades."


def record_form(key: str, plan_values: dict, last_bar_date: str, replay: bool = False, costs: tuple = (10.0, 5.0)):
    """Small form with rule inputs; used on the Analyze page."""
    with st.form(f"paper_form_{key}"):
        st.markdown("**Record as a paper trade**")
        c1, c2, c3 = st.columns(3)
        stop = c1.number_input("Stop (× ATR14)", 0.5, 6.0, DEFAULTS["stop_atr"], 0.25, key=f"{key}_stop")
        rr = c2.number_input("Target (× risk)", 0.5, 6.0, DEFAULTS["reward_risk"], 0.25, key=f"{key}_rr")
        hold = c3.number_input("Max holding (sessions)", 1, 120, DEFAULTS["max_hold"], key=f"{key}_hold")
        note = st.text_input("Note (optional)", key=f"{key}_note", max_chars=300)
        submitted = st.form_submit_button("Record paper trade", icon=":material/bookmark_add:")
    st.caption(f"Ledger: **{current_ledger()}** · enters at the next session's open · plan is frozen once recorded. "
               "Change the ledger name on the Paper trades page.")
    if submitted:
        ok, message = record({**plan_values, "stop_atr": float(stop), "reward_risk": float(rr), "max_hold": int(hold),
                              "fee_bps": costs[0], "slippage_bps": costs[1], "note": note}, last_bar_date, replay)
        (st.success if ok else st.warning)(message)


@st.cache_data(ttl=1800, show_spinner=False)
def _bars(provider_symbol: str):
    fetched = fetch_daily(provider_symbol, "As typed", "1 year")
    return load_bars(fetched.csv_bytes, f"{provider_symbol}.csv").bars


def refresh_outcomes(store, frame: pd.DataFrame, everything: bool = False) -> tuple[int, list]:
    """Re-evaluate active trades (or all) from freshly fetched completed bars."""
    updated, errors = 0, []
    for _, row in frame.iterrows():
        if row.voided or (not everything and row.status not in (None, *OPEN_STATES) and pd.notna(row.status)):
            continue
        try:
            result = evaluate(store.plan(row), _bars(row.provider_symbol))
        except Exception as exc:  # one failed fetch must not stop the rest
            errors.append(f"{row.symbol}: {exc}")
            continue
        store.save_evaluation(row.id, result)
        updated += 1
    return updated, errors


def _r(x):
    return None if x is None or pd.isna(x) else round(float(x), 2)


def render_paper_trades():
    st.title("Paper trades")
    st.caption("Setups recorded on the day they appear, then checked against the sessions that follow: did they hit the "
               "target, the stop, or run out of time? Unlike a backtest, nothing here can be tuned to the past.")
    store, label = get_store()
    top = st.columns([2, 3])
    st.session_state.setdefault("paper_ledger", "default")
    top[0].text_input("Ledger", key="paper_ledger", persist_state="session", max_chars=60,
                      help="Separate lists by name (e.g. your own name, or one per strategy). Anyone using the same app can open a ledger by name.")
    if label.startswith("Local"):
        top[1].warning("Saved in a local file. On the hosted site this resets whenever the app restarts or updates. "
                       "Connect a hosted database (DATABASE_URL secret) to keep history.", icon=":material/warning:")
    else:
        top[1].caption(f":material/database: {label}")
    frame = store.load(current_ledger())
    if frame.empty:
        st.info("No paper trades in this ledger yet. Record one from **Analyze → Trade plan & report**, from a row in the "
                "**Scanner**, or from today's signals on the **Strategy backtest** page.", icon=":material/bookmark_add:")
        return
    b1, b2, _ = st.columns([1.3, 1.3, 3])
    if b1.button("Update outcomes", type="primary", icon=":material/refresh:"):
        with st.spinner("Fetching the latest completed sessions…"):
            n, errors = refresh_outcomes(store, frame)
        st.toast(f"Updated {n} trade(s).")
        for e in errors:
            st.warning(e)
        frame = store.load(current_ledger())
    if b2.button("Re-check all", help="Re-evaluate closed trades too (results should not change; useful after data corrections)."):
        with st.spinner("Re-checking every trade…"):
            refresh_outcomes(store, frame, everything=True)
        frame = store.load(current_ledger())

    stats = ledger_stats(frame)
    m = st.columns(6)
    m[0].metric("Recorded", stats["recorded"])
    m[1].metric("Waiting / open", f"{stats['waiting']} / {stats['open']}")
    m[2].metric("Closed", stats["closed"])
    m[3].metric("Win rate", "—" if stats["win_rate"] is None else f"{100 * stats['win_rate']:.0f}%")
    m[4].metric("Avg result (R)", "—" if stats["avg_r"] is None else f"{stats['avg_r']:+.2f}")
    m[5].metric("Total (R)", f"{stats['total_r']:+.1f}")
    if stats["closed"] and stats["closed"] < 30:
        st.caption(f"Only {stats['closed']} closed trade(s): far too few to judge a method. Results become informative after dozens.")

    live = frame.loc[~frame.voided.fillna(False).astype(bool)]
    closed = live.loc[live.r_multiple.notna()].sort_values("exit_date")
    if len(closed) >= 2:
        fig = go.Figure(go.Scatter(x=closed.exit_date, y=closed.r_multiple.cumsum(), mode="lines+markers",
                                   line=dict(color="#36d6a4", width=2), hovertext=closed.symbol))
        fig.add_hline(y=0, line_color="#576579")
        fig.update_layout(template="plotly_dark", height=260, paper_bgcolor="#101a2b", plot_bgcolor="#101a2b",
                          margin=dict(l=10, r=10, t=30, b=10), title="Cumulative result of closed trades (R)", yaxis_title="R")
        st.plotly_chart(fig, width="stretch")

    view = pd.DataFrame({
        "Symbol": frame.symbol, "Source": frame.source, "Pattern / note": frame.pattern.fillna("") + frame.note.fillna("").map(lambda n: f" · {n}" if n else ""),
        "Signal date": frame.signal_date, "Status": frame.status.fillna("Not checked yet").where(~frame.voided.fillna(False).astype(bool), "Voided"),
        "Entry": frame.entry_date, "Entry ₹": frame.entry_price, "Stop ₹": frame.stop, "Target ₹": frame.target,
        "Exit": frame.exit_date, "Result (R)": frame.r_multiple.map(_r), "Open P/L (R)": frame.unrealized_r.map(_r),
        "Best (R)": frame.mfe_r.map(_r), "Worst (R)": frame.mae_r.map(_r), "Sessions": frame.sessions,
        "Checked through": frame.checked_through, "Context at signal": frame.snapshot.map(lambda s: s.get("verdict", "") if isinstance(s, dict) else ""),
        "Recorded at": frame.created_at, "id": frame.id})
    for column in ("Entry ₹", "Stop ₹", "Target ₹", "Result (R)", "Open P/L (R)", "Best (R)", "Worst (R)", "Sessions"):
        view[column] = pd.to_numeric(view[column], errors="coerce")
    for column in ("Entry", "Exit", "Checked through"):
        view[column] = view[column].fillna("")
    st.dataframe(view, hide_index=True, width="stretch", column_config={
        c: st.column_config.NumberColumn(format="%.2f") for c in ("Entry ₹", "Stop ₹", "Target ₹")} | {"id": None})
    if len(closed):
        by = closed.groupby("source").r_multiple.agg(["count", "mean", "sum"]).reset_index()
        by.columns = ["Source", "Closed trades", "Avg R", "Total R"]
        st.dataframe(by, hide_index=True, column_config={"Avg R": st.column_config.NumberColumn(format="%+.2f"),
                                                          "Total R": st.column_config.NumberColumn(format="%+.1f")})
    st.download_button("Download ledger (CSV)", frame.drop(columns=["snapshot"]).to_csv(index=False),
                       f"paper-trades-{current_ledger()}.csv", "text/csv")
    with st.expander("Void a trade"):
        st.caption("Plans can't be edited. Voiding keeps the record but removes it from the statistics; the reason is saved.")
        active = frame.loc[~frame.voided.fillna(False).astype(bool)]
        if active.empty:
            st.caption("Nothing to void.")
        else:
            choice = st.selectbox("Trade", active.id, format_func=lambda i: f"{active.set_index('id').loc[i, 'symbol']} · "
                                  f"{active.set_index('id').loc[i, 'signal_date']} · {active.set_index('id').loc[i, 'source']}", key="paper_void_id")
            reason = st.text_input("Reason (required)", key="paper_void_reason")
            if st.button("Void trade", disabled=not reason.strip()):
                store.void(choice, reason)
                st.rerun()
    with st.expander("How outcomes are judged"):
        st.markdown("- **Entry:** the open of the first session after the signal date (plus slippage).\n"
                    "- **Stop / target:** set from that entry: stop = entry − (stop × ATR14 at the signal); target = entry + (target × stop distance).\n"
                    "- **Exit:** first of stop, target or holding limit, using completed daily candles. An opening gap through the stop exits at the open; "
                    "if one candle touches both, the stop is assumed first (conservative).\n"
                    "- **R:** profit or loss after costs ÷ planned loss at the stop. Best/Worst are the largest favourable and adverse moves while open.\n"
                    "- **No hindsight:** a trade can only be recorded on the latest completed session, within a few days of it, and never during Replay.")
