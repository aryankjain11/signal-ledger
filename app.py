"""Run with: python -m streamlit run app.py"""
from dataclasses import asdict
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from quant_engine.analysis import analyze, json_safe, report_markdown, run_evidence
from quant_engine.charts import price_chart, chart_window_caption
from quant_engine.data import load_bars
from quant_engine.models import Settings
from learning.pages import render_education, render_build_journal
from quant_engine.datasets import Instrument, attach_passport
from quant_engine.data_ui import report_import, render_passport
from quant_engine.actions_ui import action_controls, render_action_audit
from quant_engine.corporate_actions import apply_actions
from quant_engine.datasets import canonical_bars_bytes
from quant_engine.models import ResearchRules
from quant_engine.research_ui import research_controls, render_research
from quant_engine.comparison_ui import render_comparison
from quant_engine.event_study_ui import render_event_study
from quant_engine.readiness import render_readiness
from quant_engine.backtest_ui import render_backtest
from quant_engine.retest_ui import render_retest_lab
from quant_engine.workflow_ui import PAGES, navigate, render_navigation, render_reference_links
from quant_engine.ui_state import (retained_upload, completed_confirmation,
    date_control, reset_dates, workspace_tabs, preserve_tab_state)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Signal Ledger · Quant research", page_icon="◈", layout="wide")
st.markdown("""<style>
 .block-container {padding-top:2.6rem; max-width:1500px}
 h1 {letter-spacing:-1.5px; font-weight:650!important}
 .eyebrow {color:#36d6a4;font-size:12px;letter-spacing:2px;font-weight:700}
 .subtitle {color:#97a7bf;font-size:17px;margin-bottom:22px}
 [data-testid="stMetric"] {background:#101a2b;border:1px solid #253248;border-radius:12px;padding:16px}
 [data-testid="stMetricLabel"] {color:#97a7bf}
 [data-testid="stSidebar"] {border-right:1px solid #253248}
 .stTabs [data-baseweb="tab-list"] {gap:24px;border-bottom:1px solid #253248}
 </style>""", unsafe_allow_html=True)

requested_page = st.query_params.get("page", "research")
preserve_tab_state()
page_names = list(PAGES)
page_index = list(PAGES.values()).index(requested_page) if requested_page in PAGES.values() else 0
workspace = st.sidebar.selectbox("Workspace", page_names, index=page_index, key="workspace_page")
st.query_params["page"] = PAGES[workspace]
render_navigation(workspace)
with st.sidebar:
    st.markdown("### ◈ Signal Ledger")
    st.caption("TECHNICAL RESEARCH WORKBENCH · v0.1")
    st.divider()
    source = st.radio("Data source", ["Synthetic walkthrough", "Upload daily data", "Synthetic NSE report walkthrough", "Import NSE daily reports"],key="data_source",persist_state="session")
    upload = None
    report_uploads = None
    is_reports = source in {"Synthetic NSE report walkthrough", "Import NSE daily reports"}
    if source == "Upload daily data":
        upload = retained_upload("OHLCV file", type=["csv", "xlsx"], key="research_upload")
        st.caption("NSE stock-history downloads work directly: keep the original CSV, columns and filename. Dates and Indian comma formatting are recognized automatically.")
    elif source == "Import NSE daily reports":
        report_uploads = retained_upload("Daily UDiFF reports (preview)", type=["csv", "zip"], accept_multiple_files=True, key="nse_reports")
    symbol = st.text_input("Research label", "SYNTHETIC" if source.startswith("Synthetic") else "NSE / YOUR SYMBOL", max_chars=40,
        help="A label for the current file, not a quote lookup. The app does not fetch stock data when you type a symbol.")
    declared_provider, declared_exchange = "User-supplied file; provider not stated", "Unknown"
    if not is_reports:
        adjustment = "Synthetic example" if source.startswith("Synthetic") else st.selectbox("Price adjustment basis", ["Unknown / unverified", "Consistently adjusted OHLC", "Unadjusted OHLC"])
        if source == "Upload daily data":
            with st.expander("Data source declaration"):
                declared_provider = st.text_input("Provider/source label", value=declared_provider, key="declared_provider")
                declared_exchange = st.selectbox("Exchange declaration", ["Unknown", "NSE", "BSE"], key="declared_exchange")
    else:
        adjustment = "Synthetic example" if source.startswith("Synthetic") else "Unadjusted OHLC"
        st.caption("UDiFF preview: select the security from report fields after upload. Prices remain as quoted; adjustments and origin are not independently verified.")
    complete = True
    if source in {"Upload daily data", "Import NSE daily reports"}:
        complete = completed_confirmation("Every row is a completed daily session bar", upload if source == "Upload daily data" else report_uploads, key="research_complete")
    st.divider()
    with st.expander("Simulation capital, risk and costs"):
        st.caption("These inputs affect both strategy simulations. Historical outcome studies and stock comparisons do not use them.")
        capital = st.number_input("Account capital (INR)", min_value=100.0, value=100_000.0, step=1000.0, key="simulation_capital", persist_state="session")
        risk = st.slider("Risk budget per trade (%)", 0.1, 5.0, 1.0, 0.1, key="simulation_risk", persist_state="session")
        fees = st.number_input("Estimated total charges per side (bps)", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key="simulation_fees", persist_state="session")
        slip = st.number_input("Slippage per side (bps)", min_value=0.0, max_value=100.0, value=5.0, step=1.0, key="simulation_slippage", persist_state="session")
        st.caption("1 basis point = 0.01%. Enter brokerage, taxes and other charges as a blended per-side estimate. Actual charges can differ by side and transaction; no statutory schedule is built in.")
    st.caption(f"Simulation: ₹{capital:,.0f} · risk {risk:g}% · charges {fees:g} + slippage {slip:g} bps/side")
    bands = st.checkbox("Show Bollinger bands")
    st.caption("Indian equities · swing research · INR-denominated uploads · daily bars · no live orders")

# Render research inputs on every workspace so Streamlit retains their widget state,
# including the local file handle. Reference/checklist pages still need no data.
if workspace == "Compare two stocks":
    st.caption("The sidebar retains your single-stock research context. Choose the two comparison datasets below; baseline capital and costs do not affect comparison statistics.")
    render_comparison()
    st.stop()
if workspace == "Education and Concepts":
    render_education(ROOT)
    st.stop()
if workspace == "Build checklist & log":
    render_build_journal(ROOT)
    st.stop()

st.markdown('<div class="eyebrow">OBSERVE / EXPLAIN / TEST</div>', unsafe_allow_html=True)
st.title("After the pattern" if workspace == "After the pattern" else "Price structure, with evidence.")
st.caption("Use your daily file or explore the demo. Inspect the chart, study historical outcomes, then test a strategy under explicit costs and risk assumptions.")

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
        st.info("Upload one symbol's daily file: an original NSE stock-history CSV, or a standard date/open/high/low/close/volume CSV/XLSX. NSE downloads need no manual editing.")
        st.download_button("Download example format (synthetic)", (ROOT / "data" / "synthetic_daily.csv").read_bytes(), "synthetic_daily.csv", "text/csv")
        st.stop()
    if not complete:
        st.warning("Confirm that all uploaded rows are completed daily bars before running analysis.")
        st.stop()
    content, filename = upload.getvalue(), upload.name

if not is_reports:
    try:
        data = load_bars(content, filename)
        input_metadata = dict(data.metadata)
        is_nse_quote = input_metadata.get("detected_nse_quote", False)
        file_symbol = data.metadata.get("file_symbol")
        instrument_symbol = file_symbol or symbol
        data = attach_passport(data, instrument=Instrument("Synthetic" if source.startswith("Synthetic") else "NSE" if is_nse_quote else declared_exchange, instrument_symbol, input_metadata.get("file_series", "")),
                               provider="Synthetic project fixture" if source.startswith("Synthetic") else "User-supplied NSE security-history export" if is_nse_quote else declared_provider.strip() or "Provider not stated",
                               input_format=input_metadata.get("input_format", "Standard OHLCV CSV/XLSX"), adjustment="Synthetic example" if source.startswith("Synthetic") else adjustment,
                               sources=[{"name": Path(filename).name, "sha256": data.source_hash, "bytes": len(content)}],
                               is_synthetic=source.startswith("Synthetic"),
                               normalization={**input_metadata.get("normalization", {}), "symbol_basis": input_metadata["symbol_basis"]} if is_nse_quote else None)
        if file_symbol:
            symbol = file_symbol
        if is_nse_quote:
            st.success(f"NSE stock-history format detected · {symbol} · {len(data.bars)} sessions. Dates, number formatting and row order handled automatically.")
            st.caption(input_metadata["symbol_basis"] + ". CLOSE and VOLUME used; extra fields ignored. Adjustment declaration is still unverified.")
    except Exception as exc:
        st.error(f"Data could not be analyzed: {exc}")
        st.stop()

if data.metadata.get("is_synthetic"):
    adjustment = "Synthetic example"
if adjustment == "Unknown / unverified":
    st.warning("Adjustment status is unverified. Splits and dividends can distort indicators, patterns and backtest results.")
elif adjustment == "Unadjusted OHLC":
    st.warning("Quoted/unadjusted prices: splits and other corporate actions have not been reconciled. Interpret long-horizon indicators and backtests accordingly.")
with st.sidebar:
    action_ledger, use_adjusted = action_controls(data)
    research_rules = research_controls()
options = [d.date().isoformat() for d in data.bars.index]
as_of = date_control("Replay through session · analysis uses only rows through this date", options, key="research_cutoff", context=data.source_hash)
if as_of != options[-1]:
    st.caption("Historical replay is active. Later uploaded observations are excluded from this analysis.")
    st.button("Use latest uploaded bar", key="latest_research_bar", on_click=reset_dates, args=("research_cutoff",options))
data.bars = data.bars.loc[:as_of]
original_visible_csv = canonical_bars_bytes(data.bars)
action_factors = None
if action_ledger is not None:
    try:
        data, action_factors = apply_actions(data, action_ledger, as_of=as_of, adjusted=use_adjusted)
        if use_adjusted:
            adjustment = "Split/bonus adjusted research; no dividend/total-return adjustment"
            st.info("Split/bonus adjusted research view. Original quoted prices are preserved separately. Trade sizing and backtesting are unavailable in this view.")
    except ValueError as exc:
        st.error(f"Corporate-action review required: {exc}")
        st.stop()
from quant_engine.calendar import attach_quality
quality = attach_quality(data, replay=as_of != options[-1])
if any(quality[key] for key in ("missing_expected_dates", "unexpected_dates", "future_dates")):
    st.warning("Calendar checks found observations needing review. Open Data & exports for the dates and details; no bars were filled or removed.")
if len(data.bars) < 3:
    st.info("Select at least three observations to begin analysis.")
    st.stop()
settings = Settings(capital=capital, risk_fraction=risk / 100, fee_bps=fees, slippage_bps=slip)

@st.cache_data(show_spinner=False)
def compute(content_hash, bars, settings_dict, execution_restriction="", research_rule_values=None):
    from quant_engine.models import ValidatedData
    return analyze(ValidatedData(bars, [], content_hash, {"execution_restriction": execution_restriction}), Settings(**settings_dict), ResearchRules(**(research_rule_values or {})))

from copy import deepcopy
analysis = deepcopy(compute(data.source_hash, data.bars, asdict(settings), data.metadata.get("execution_restriction", ""), asdict(research_rules)))
analysis.warnings = data.warnings + analysis.warnings
execution_restriction = data.metadata.get("execution_restriction")
if execution_restriction:
    analysis.setup = {"status": "Research view · execution unavailable", "reason": execution_restriction}
render_readiness(analysis, data, symbol, adjustment)
render_reference_links()
if workspace == "After the pattern":
    render_event_study(analysis, data, settings, symbol, adjustment)
    st.stop()
frame, last = analysis.frame, analysis.frame.iloc[-1]
columns = st.columns(4)
columns[0].metric("Last close", f"{last.close:,.2f}", f"{(last.close / frame.close.iloc[-2] - 1) * 100:+.2f}%")
columns[1].metric("Confirmed structure", analysis.trend.replace(" structure", ""))
columns[2].metric("RSI · 14 sessions", f"{last.rsi_14:.1f}" if pd.notna(last.rsi_14) else "Warming up")
columns[3].metric("Relative volume", f"{last.relative_volume:.2f}×" if pd.notna(last.relative_volume) else "Warming up")
st.caption("Use the quick references above or Education and Concepts for RSI, MACD, ATR, candlestick patterns and worked examples.")
st.caption(f"{symbol} · {len(frame):,} sessions · as of {as_of} · daily exchange session dates · INR assumed; no currency conversion")

tab_names = ["Chart & structure", "Patterns & momentum", "Evidence & trade plan", "Backtest lab", "Data & exports"]
requested_tab = st.session_state.pop("requested_research_tab", None)
chart_tab, analytical_tab, report_tab, backtest_tab, quality_tab = workspace_tabs(tab_names, key="research_active_tab", requested=requested_tab)
with analytical_tab:
    render_research(analysis)
with chart_tab:
    st.plotly_chart(price_chart(analysis, bands), width="stretch")
    st.caption(chart_window_caption(analysis))
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
        from hashlib import sha256
        pick_key = "observation_pick_" + sha256(canonical_bars_bytes(data.bars) + json.dumps(analysis.rules, sort_keys=True).encode()).hexdigest()[:16]
        choice = st.dataframe(observations, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key=pick_key)
        picked = choice.selection.rows
        chosen_event = sorted(analysis.events, key=lambda e: e["detected_at"], reverse=True)[:40][picked[0]] if picked and 0 <= picked[0] < len(visible) else None
        if chosen_event:
            from quant_engine.event_study import occurrence_ledger
            row = occurrence_ledger(analysis.frame, [chosen_event]).iloc[0]
            def open_study(cohort, direction):
                st.session_state["requested_study_cohort"] = cohort
                st.session_state["requested_study_direction"] = int(direction)
                navigate("After the pattern")
            st.button("Study this observation type", key="study_observation", disabled=not bool(row.eligible),
                      on_click=open_study, args=(row.cohort, row.direction))
            if not row.eligible:
                st.caption("This diagnostic lifecycle state stays in the audit. Select a breakout, retest or geometric observation to study outcomes.")
        st.caption("Select an observation row to study its event type. Formation dates, knowledge dates and full coordinates remain in the exported evidence.")
    else:
        st.caption("No supported geometries detected.")
    st.button("Explore historical outcomes", key="explore_outcomes", on_click=navigate, args=("After the pattern",))

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
    strategy = st.radio("Strategy to test", ["Fixed breakout baseline", "Breakout-retest v1"],
        horizontal=True, key="strategy_choice", persist_state="session")
    if strategy == "Breakout-retest v1":
        render_retest_lab(analysis, data, settings, symbol, adjustment)
    else:
        render_backtest(analysis, data, settings, symbol, adjustment)

with quality_tab:
    st.subheader("Source and limitations")
    st.write(f"Input: {filename} · source hash: `{data.source_hash}`")
    if action_ledger is not None:
        st.write(f"Analysis price basis: {data.metadata['analysis_price_basis']}.")
        st.caption(f"Original-source declaration: {data.metadata['adjustment_basis']}. Only explicitly selected split/bonus research adjustments are applied.")
    else:
        st.write(f"Adjustment declaration: {adjustment}. No adjustment is applied automatically.")
    render_passport(data)
    if action_ledger is not None:
        render_action_audit(data, original_visible_csv, action_factors)
    for warning in analysis.warnings:
        st.write(f"• {warning}")
    st.dataframe(frame.tail(100), width="stretch")
    evidence = run_evidence(analysis, data, settings, symbol, adjustment)
    st.download_button("Download analysis evidence", json.dumps(evidence, indent=2, allow_nan=False), "analysis.json", "application/json")
    st.download_button("Download research report", report_markdown(analysis, symbol, adjustment), "research-report.md", "text/markdown")
    st.download_button("Download calculated features", frame.to_csv(), "features.csv", "text/csv")

st.divider()
st.caption("Research and decision support only. No live orders, predictive guarantees, or calibrated success estimates. Screenshot analysis, other chart patterns, intraday data, ML and broker integrations are future work.")
