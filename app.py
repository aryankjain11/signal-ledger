"""Run with: python -m streamlit run app.py"""
from dataclasses import asdict
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from quant_engine.analysis import analyze, json_safe, report_markdown, run_evidence
from quant_engine.charts import price_chart
from quant_engine.data import load_bars
from quant_engine.models import Settings
from quant_engine.strategy import backtest
from learning.pages import render_education, render_build_journal
from quant_engine.datasets import Instrument, attach_passport
from quant_engine.data_ui import report_import, render_passport

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Signal Ledger · Quant research", page_icon="◈", layout="wide")
st.markdown("""<style>
 .block-container {padding-top:4rem; max-width:1500px}
 h1 {letter-spacing:-1.5px; font-weight:650!important}
 .eyebrow {color:#36d6a4;font-size:12px;letter-spacing:2px;font-weight:700}
 .subtitle {color:#97a7bf;font-size:17px;margin-bottom:22px}
 [data-testid="stMetric"] {background:#101a2b;border:1px solid #253248;border-radius:12px;padding:16px}
 [data-testid="stMetricLabel"] {color:#97a7bf}
 [data-testid="stSidebar"] {border-right:1px solid #253248}
 .stTabs [data-baseweb="tab-list"] {gap:24px;border-bottom:1px solid #253248}
 </style>""", unsafe_allow_html=True)

PAGES = {"Research dashboard": "research", "Education and Concepts": "education", "Build checklist & log": "build"}
requested_page = st.query_params.get("page", "research")
page_names = list(PAGES)
page_index = list(PAGES.values()).index(requested_page) if requested_page in PAGES.values() else 0
workspace = st.sidebar.selectbox("Workspace", page_names, index=page_index, key="workspace_page")
st.query_params["page"] = PAGES[workspace]
if workspace == "Education and Concepts":
    render_education(ROOT)
    st.stop()
if workspace == "Build checklist & log":
    render_build_journal(ROOT)
    st.stop()

with st.sidebar:
    st.markdown("### ◈ Signal Ledger")
    st.caption("TECHNICAL RESEARCH WORKBENCH · v0.1")
    st.divider()
    source = st.radio("Data source", ["Synthetic walkthrough", "Upload daily data", "Synthetic NSE report walkthrough", "Import NSE daily reports"])
    upload = None
    report_uploads = None
    is_reports = source in {"Synthetic NSE report walkthrough", "Import NSE daily reports"}
    if source == "Upload daily data":
        upload = st.file_uploader("OHLCV file", type=["csv", "xlsx"])
    elif source == "Import NSE daily reports":
        report_uploads = st.file_uploader("Daily UDiFF reports (preview)", type=["csv", "zip"], accept_multiple_files=True, key="nse_reports")
    symbol = st.text_input("Research label", "SYNTHETIC" if source.startswith("Synthetic") else "NSE / YOUR SYMBOL", max_chars=40)
    declared_provider, declared_exchange = "User-supplied file; provider not stated", "Unknown"
    if not is_reports:
        adjustment = st.selectbox("Price adjustment basis", ["Unknown / unverified", "Consistently adjusted OHLC", "Unadjusted OHLC"])
        if source == "Upload daily data":
            with st.expander("Data source declaration"):
                declared_provider = st.text_input("Provider/source label", value=declared_provider, key="declared_provider")
                declared_exchange = st.selectbox("Exchange declaration", ["Unknown", "NSE", "BSE"], key="declared_exchange")
    else:
        adjustment = "Synthetic example" if source.startswith("Synthetic") else "Unadjusted OHLC"
        st.caption("UDiFF preview: select the security from report fields after upload. Prices remain as quoted; adjustments and origin are not independently verified.")
    complete = True
    if source in {"Upload daily data", "Import NSE daily reports"}:
        complete = st.checkbox("Every row is a completed daily session bar", value=False)
    st.divider()
    st.markdown("**Research assumptions**")
    capital = st.number_input("Account capital (INR)", min_value=100.0, value=100_000.0, step=1000.0)
    risk = st.slider("Risk budget per trade (%)", 0.1, 5.0, 1.0, 0.1)
    fees = st.number_input("Estimated total charges per side (bps)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    slip = st.number_input("Slippage per side (bps)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)
    st.caption("1 basis point = 0.01%. Enter estimated brokerage, STT, exchange charges, GST, SEBI charges and stamp duty as a blended per-side rate. Actual charges can differ by side and transaction type; no statutory schedule is built in.")
    bands = st.checkbox("Show Bollinger bands")
    st.caption("Indian equities · swing research · INR-denominated uploads · daily bars · no live orders")

st.markdown('<div class="eyebrow">OBSERVE / EXPLAIN / TEST</div>', unsafe_allow_html=True)
st.title("Price structure, with evidence.")
st.markdown('<div class="subtitle">A transparent starting point for technical research. Every observation traces back to your data.</div>', unsafe_allow_html=True)

if is_reports:
    if source == "Import NSE daily reports" and report_uploads and not complete:
        st.warning("Confirm that all uploaded rows are completed daily bars before running analysis.")
        st.stop()
    files = [(f.name, f.getvalue()) for f in report_uploads] if report_uploads else []
    data = report_import(files, is_synthetic=source.startswith("Synthetic"))
    symbol = data.metadata["instrument"]["symbol"]
    filename = f"{len(data.metadata['source_files'])} report input file(s)"
    adjustment = data.metadata["adjustment_basis"]
elif source.startswith("Synthetic"):
    content = (ROOT / "data" / "synthetic_daily.csv").read_bytes()
    filename = "synthetic_daily.csv"
    st.info("SYNTHETIC DATA · Generated solely to demonstrate the application. This is not a stock or evidence of trading performance.")
else:
    if upload is None:
        st.info("Upload one symbol's daily file. Required columns: date, open, high, low, close, volume. CSV dates: YYYY-MM-DD.")
        st.download_button("Download example format (synthetic)", (ROOT / "data" / "synthetic_daily.csv").read_bytes(), "synthetic_daily.csv", "text/csv")
        st.stop()
    if not complete:
        st.warning("Confirm that all uploaded rows are completed daily bars before running analysis.")
        st.stop()
    content, filename = upload.getvalue(), upload.name

if not is_reports:
    try:
        data = load_bars(content, filename)
        file_symbol = data.metadata.get("file_symbol")
        instrument_symbol = file_symbol or symbol
        data = attach_passport(data, instrument=Instrument("Synthetic" if source.startswith("Synthetic") else declared_exchange, instrument_symbol),
                               provider="Synthetic project fixture" if source.startswith("Synthetic") else declared_provider.strip() or "Provider not stated",
                               input_format="Standard OHLCV CSV/XLSX", adjustment="Synthetic example" if source.startswith("Synthetic") else adjustment,
                               sources=[{"name": Path(filename).name, "sha256": data.source_hash, "bytes": len(content)}],
                               is_synthetic=source.startswith("Synthetic"))
        if file_symbol:
            symbol = file_symbol
    except Exception as exc:
        st.error(f"Data could not be analyzed: {exc}")
        st.stop()

if adjustment == "Unknown / unverified":
    st.warning("Adjustment status is unverified. Splits and dividends can distort indicators, patterns and backtest results.")
elif adjustment == "Unadjusted OHLC":
    st.warning("Quoted/unadjusted prices: splits and other corporate actions have not been reconciled. Interpret long-horizon indicators and backtests accordingly.")
options = [d.date().isoformat() for d in data.bars.index]
as_of = st.select_slider("Replay through session · analysis uses only rows through this date", options=options, value=options[-1])
data.bars = data.bars.loc[:as_of]
if len(data.bars) < 3:
    st.info("Select at least three observations to begin analysis.")
    st.stop()
settings = Settings(capital=capital, risk_fraction=risk / 100, fee_bps=fees, slippage_bps=slip)

@st.cache_data(show_spinner=False)
def compute(content_hash, bars, settings_dict):
    from quant_engine.models import ValidatedData
    return analyze(ValidatedData(bars, [], content_hash), Settings(**settings_dict))

analysis = compute(data.source_hash, data.bars, asdict(settings))
analysis.warnings = data.warnings + analysis.warnings
frame, last = analysis.frame, analysis.frame.iloc[-1]
columns = st.columns(4)
columns[0].metric("Last close", f"{last.close:,.2f}", f"{(last.close / frame.close.iloc[-2] - 1) * 100:+.2f}%")
columns[1].metric("Confirmed structure", analysis.trend.replace(" structure", ""))
columns[2].metric("RSI · 14 sessions", f"{last.rsi_14:.1f}" if pd.notna(last.rsi_14) else "Warming up")
columns[3].metric("Relative volume", f"{last.relative_volume:.2f}×" if pd.notna(last.relative_volume) else "Warming up")
st.caption("New to these terms? Open Education and Concepts from the Workspace menu for RSI, MACD, ATR, candlestick patterns, worked examples and practice labs.")
st.caption(f"{symbol} · {len(frame):,} sessions · as of {as_of} · daily exchange session dates · INR assumed; no currency conversion")

chart_tab, report_tab, backtest_tab, quality_tab = st.tabs(["Chart & structure", "Evidence & trade plan", "Backtest lab", "Data & exports"])
with chart_tab:
    st.plotly_chart(price_chart(analysis, bands), width="stretch")
    st.caption("Latest 250 sessions shown. Pivots are plotted at formation; hover shows when they became knowable. Shaded zones describe this as-of snapshot, not historical signals.")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### What the data says")
        for item in analysis.evidence:
            st.write(f"• {item}")
        st.caption(f"Weekly context: {analysis.weekly['context']}. Most recent calendar week excluded.")
    with right:
        st.markdown("#### Support & resistance zones")
        if analysis.zones:
            zones = pd.DataFrame(analysis.zones)[["role", "low", "high", "pivot_count"]]
            zones.columns = ["Role", "Lower boundary", "Upper boundary", "Confirmed pivots"]
            st.dataframe(zones, hide_index=True, width="stretch", column_config={
                "Lower boundary": st.column_config.NumberColumn(format="%.2f"),
                "Upper boundary": st.column_config.NumberColumn(format="%.2f")})
        else:
            st.caption("Not enough clustered confirmed pivots to define zones.")
        st.caption("Zones cluster nearby pivots using 0.5 ATR tolerance. Pivot count is not a probability or count of independent tests.")
    st.markdown("#### Observation log")
    if analysis.events:
        visible = [{k: e.get(k) for k in ("name", "status", "formed_at", "detected_at", "price", "evidence")}
                   for e in sorted(analysis.events, key=lambda e: e["detected_at"], reverse=True)[:40]]
        observations = pd.DataFrame(visible)
        observations.columns = ["Observation", "Status", "Formed on", "Knowable on", "Price", "Evidence"]
        st.dataframe(observations, hide_index=True, width="stretch")
    else:
        st.caption("No supported geometries detected.")

with report_tab:
    st.subheader(analysis.setup["status"])
    if "reference_entry" in analysis.setup:
        st.caption(analysis.setup["note"])
        entry, stop, target, quantity = st.columns(4)
        entry.metric("Reference entry", f"₹{analysis.setup['reference_entry']:,.2f}")
        stop.metric("Reference stop", f"₹{analysis.setup['reference_stop']:,.2f}")
        target.metric("Reference target", f"₹{analysis.setup['reference_target']:,.2f}")
        quantity.metric("Reference shares", analysis.setup["quantity"])
    else:
        st.write(analysis.setup.get("reason", "No executable baseline setup."))
    st.info("Success probability: unavailable. There is no calibrated model or validated pattern-performance database in this release.")
    st.markdown(report_markdown(analysis, symbol, adjustment))

with backtest_tab:
    st.subheader("A testable hypothesis, not a forecast")
    st.write("Enter at the next session's open after a close above the prior 20 highs, above EMA50, with relative volume ≥ 1.2. Fix a 2 ATR stop and 2R target at entry; hold at most 10 sessions.")
    st.caption("One long position; no leverage. Size is capped by cash, risk budget and 1% of prior-session volume. Slippage and fees apply on both sides. If stop and target touch in one bar, stop wins. Gaps can exceed the risk budget. Open positions close at the end of the dataset.")
    if st.button("Run exploratory backtest", type="primary"):
        result = backtest(frame, settings)
        metrics = result.metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Completed trades", metrics["trades"])
        c2.metric("Net return", f"{metrics['total_return']:.2%}")
        c3.metric("Maximum drawdown", f"{metrics['max_drawdown']:.2%}")
        c4.metric("Historical win rate", f"{metrics['historical_win_fraction']:.1%}" if metrics["trades"] else "Unavailable")
        st.line_chart(result.equity[["equity"]])
        st.caption(f"Gross close-to-close buy & hold comparison: {metrics['gross_buy_hold_return']:.2%}; excludes costs and uses different exposure. Equity includes estimated liquidation costs while a position is open.")
        if not result.trades.empty:
            st.dataframe(result.trades, hide_index=True, width="stretch")
            st.download_button("Download trade ledger", result.trades.to_csv(index=False), "trades.csv", "text/csv")
        st.download_button("Download backtest record", json.dumps(json_safe({
            "analysis": run_evidence(analysis, data, settings, symbol, adjustment),
            "metrics": metrics, "trades": result.trades.to_dict("records"),
            "equity": result.equity.reset_index().to_dict("records")}), indent=2, allow_nan=False),
            "backtest.json", "application/json")
        st.warning(metrics["validation"])

with quality_tab:
    st.subheader("Source and limitations")
    st.write(f"Input: {filename} · source hash: `{data.source_hash}`")
    st.write(f"Adjustment declaration: {adjustment}. No adjustment is applied automatically.")
    render_passport(data)
    for warning in analysis.warnings:
        st.write(f"• {warning}")
    st.dataframe(frame.tail(100), width="stretch")
    evidence = run_evidence(analysis, data, settings, symbol, adjustment)
    st.download_button("Download analysis evidence", json.dumps(evidence, indent=2, allow_nan=False), "analysis.json", "application/json")
    st.download_button("Download research report", report_markdown(analysis, symbol, adjustment), "research-report.md", "text/markdown")
    st.download_button("Download calculated features", frame.to_csv(), "features.csv", "text/csv")

st.divider()
st.caption("Research and decision support only. No live orders, predictive guarantees, or calibrated success estimates. Screenshot analysis, other chart patterns, intraday data, ML and broker integrations are future work.")
