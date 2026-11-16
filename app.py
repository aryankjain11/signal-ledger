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
from quant_engine.workflow_ui import PAGES, PAGE_ICONS, navigate, render_reference_links
from quant_engine.providers import EXCHANGE_SUFFIX, PERIODS, PROVIDER_ADJUSTMENT, fetch_daily
from quant_engine.market_read import market_read
from quant_engine.scanner_ui import render_scanner
from quant_engine.pooled_ui import render_pooled_research
from quant_engine.dashboard_ui import STYLE, render_header, render_market_read, render_timeframes, chart_controls, render_welcome
import os
from quant_engine.ui_state import (retained_upload, completed_confirmation,
    date_control, reset_dates, workspace_tabs, preserve_tab_state)

SOURCES = ["Fetch by ticker", "Upload daily data", "Demo data", "Import NSE daily reports"]
DEFAULT_SOURCE = os.environ.get("SIGNAL_LEDGER_DEFAULT_SOURCE", "Fetch by ticker")


@st.cache_data(ttl=3600, show_spinner="Fetching daily history…")
def cached_fetch(symbol, exchange, period):
    return fetch_daily(symbol, exchange, period)


ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Signal Ledger · Technical research", page_icon="◈", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

requested_page = st.query_params.get("page", "research")
if requested_page == "build":  # developer view, intentionally not in the main navigation
    render_build_journal(ROOT)
    st.stop()
preserve_tab_state()
page_names = list(PAGES)
if "workspace_page" not in st.session_state:
    st.session_state["workspace_page"] = next((k for k, v in PAGES.items() if v == requested_page), page_names[0])
with st.sidebar:
    st.markdown('<div class="brand">◈ Signal Ledger</div><div class="brand-sub">Technical research workbench</div>', unsafe_allow_html=True)
    workspace = st.radio("Navigate", page_names, key="workspace_page", label_visibility="collapsed",
                         format_func=lambda name: f"{PAGE_ICONS[name]}  {name}")
st.query_params["page"] = PAGES[workspace]
if workspace == "Scanner":
    render_scanner()
    st.stop()
if workspace == "Compare stocks":
    render_comparison()
    st.stop()
if workspace == "Learn":
    render_education(ROOT)
    st.stop()
if workspace == "Pattern research":
    st.title("Pattern research")
    scope = st.segmented_control("Study", ["This stock", "Watchlist (pooled)"], default="This stock",
                                 key="research_scope", persist_state="session") or "This stock"
    if scope == "Watchlist (pooled)":
        render_pooled_research()
        st.stop()
with st.sidebar:
    st.divider()
    st.markdown('<div class="side-head">Data</div>', unsafe_allow_html=True)
    source = st.radio("Data source", SOURCES, key="data_source", persist_state="session",
                      index=SOURCES.index(DEFAULT_SOURCE) if DEFAULT_SOURCE in SOURCES else 0)
    upload = None
    report_uploads = None
    fetched = None
    report_demo = False
    is_reports = source == "Import NSE daily reports"
    declared_provider, declared_exchange = "User-supplied file; provider not stated", "Unknown"
    if source == "Fetch by ticker":
        st.session_state.setdefault("ticker_symbol", "RELIANCE")
        ticker = st.text_input("Ticker", key="ticker_symbol", max_chars=30, persist_state="session",
                               placeholder="RELIANCE, TCS, HDFCBANK, ^NSEI",
                               help="NSE/BSE symbols get .NS/.BO added automatically. Indices start with ^ (e.g. ^NSEI). Choose 'As typed' for other markets.")
        left, right = st.columns(2)
        exchange = left.selectbox("Exchange", list(EXCHANGE_SUFFIX), key="ticker_exchange", persist_state="session")
        period = right.selectbox("History", list(PERIODS), index=2, key="ticker_period", persist_state="session")
        if st.button("Refresh data", key="ticker_refresh", icon=":material/refresh:", width="stretch"):
            cached_fetch.clear()
        symbol = ticker.strip().upper() or "TICKER"
        adjustment = PROVIDER_ADJUSTMENT
    elif source == "Upload daily data":
        upload = retained_upload("OHLCV file", type=["csv", "xlsx"], key="research_upload")
        st.caption("Original NSE stock-history CSVs work unchanged. Otherwise use date, open, high, low, close, volume columns.")
        symbol = Path(upload.name).stem.upper()[:40] if upload is not None else "UPLOAD"
    elif is_reports:
        report_uploads = retained_upload("Daily UDiFF reports (preview)", type=["csv", "zip"], accept_multiple_files=True, key="nse_reports")
        if not report_uploads:
            report_demo = st.checkbox("Use demo reports", key="report_demo", help="Three invented UDiFF-style reports to try this import path.")
        symbol = "NSE REPORTS"
    else:
        symbol = "SYNTHETIC"
    is_demo = source == "Demo data" or report_demo
    if source == "Upload daily data":
        adjustment = st.selectbox("Price adjustment basis", ["Unknown / unverified", "Consistently adjusted OHLC", "Unadjusted OHLC"], key="adjustment_basis", persist_state="session")
        with st.expander("Source details (optional)"):
            declared_provider = st.text_input("Provider/source label", value=declared_provider, key="declared_provider", persist_state="session")
            declared_exchange = st.selectbox("Exchange declaration", ["Unknown", "NSE", "BSE"], key="declared_exchange", persist_state="session")
    elif is_reports:
        adjustment = "Synthetic example" if is_demo else "Unadjusted OHLC"
    elif source == "Demo data":
        adjustment = "Synthetic example"
    complete = True
    if source in {"Upload daily data", "Import NSE daily reports"}:
        complete = completed_confirmation("Every row is a completed daily session bar", upload if source == "Upload daily data" else report_uploads, key="research_complete")
    st.divider()
    st.markdown('<div class="side-head">Settings</div>', unsafe_allow_html=True)
    with st.expander("Capital, risk and costs"):
        st.caption("Used by the trade plan and backtests only.")
        capital = st.number_input("Account capital (INR)", min_value=100.0, value=100_000.0, step=1000.0, key="simulation_capital", persist_state="session")
        risk = st.slider("Risk budget per trade (%)", 0.1, 5.0, 1.0, 0.1, key="simulation_risk", persist_state="session")
        fees = st.number_input("Estimated total charges per side (bps)", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key="simulation_fees", persist_state="session")
        slip = st.number_input("Slippage per side (bps)", min_value=0.0, max_value=100.0, value=5.0, step=1.0, key="simulation_slippage", persist_state="session")
        st.caption("1 basis point = 0.01%. Blend brokerage, STT, exchange and other charges into one per-side estimate.")
    st.caption(f"₹{capital:,.0f} · risk {risk:g}% · costs {fees:g}+{slip:g} bps/side")


if workspace == "Pattern research":
    st.caption("What happened after each detected pattern in this stock's history: forward moves, best/worst excursions and comparison with ordinary days. "
               "Switch to **Watchlist (pooled)** to study the same patterns across many stocks.")

provider_notes = []
if is_reports:
    if report_uploads and not complete:
        st.warning("Confirm that all uploaded rows are completed daily bars before running analysis.")
        st.stop()
    files = [(f.name, f.getvalue()) for f in report_uploads] if report_uploads else []
    data = report_import(files, is_synthetic=is_demo)
    symbol = data.metadata["instrument"]["symbol"]
    filename = f"{len(data.metadata['source_files'])} report input file(s)"
    adjustment = data.metadata["adjustment_basis"]
elif source == "Fetch by ticker":
    if not ticker.strip():
        render_welcome()
        st.stop()
    try:
        fetched = cached_fetch(ticker, exchange, period)
    except ValueError as exc:
        detail = str(exc)
        st.error(f"Couldn't load **{ticker.strip().upper()}** ({exchange}). Check the symbol and your internet connection.", icon=":material/cloud_off:")
        with st.expander("Technical details"):
            st.code(detail, language=None)
        st.caption("You can also use **Upload daily data** (e.g. an NSE stock-history CSV) or **Demo data** in the sidebar.")
        st.button("Try the demo data instead", on_click=lambda: st.session_state.update(data_source="Demo data"), icon=":material/play_arrow:")
        st.stop()
    content, filename = fetched.csv_bytes, f"{fetched.provider_symbol}.csv"
    symbol = fetched.display_symbol
    provider_notes = fetched.notes
elif source == "Demo data":
    content = (ROOT / "data" / "synthetic_daily.csv").read_bytes()
    filename = "synthetic_daily.csv"
    st.info("Demo data: an invented price series for exploring the app. Not a real stock.", icon=":material/science:")
else:
    if upload is None:
        render_welcome(upload_mode=True)
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
        if fetched is not None:
            instrument = Instrument(fetched.exchange if fetched.exchange != "As typed" else "Unknown", fetched.provider_symbol, "")
            provider_label, input_format = "Yahoo Finance via yfinance (fetched " + pd.Timestamp.now(tz="Asia/Kolkata").strftime("%Y-%m-%d %H:%M IST") + ")", "Provider daily history"
        else:
            instrument = Instrument("Synthetic" if is_demo else "NSE" if is_nse_quote else declared_exchange, instrument_symbol, input_metadata.get("file_series", ""))
            provider_label = "Synthetic project fixture" if is_demo else "User-supplied NSE security-history export" if is_nse_quote else declared_provider.strip() or "Provider not stated"
            input_format = input_metadata.get("input_format", "Standard OHLCV CSV/XLSX")
        data = attach_passport(data, instrument=instrument, provider=provider_label,
                               input_format=input_format, adjustment="Synthetic example" if is_demo else adjustment,
                               sources=[{"name": Path(filename).name, "sha256": data.source_hash, "bytes": len(content)}],
                               is_synthetic=is_demo,
                               normalization={**input_metadata.get("normalization", {}), "symbol_basis": input_metadata["symbol_basis"]} if is_nse_quote else None)
        if file_symbol and fetched is None:
            symbol = file_symbol
        if provider_notes:
            data.warnings = data.warnings + provider_notes
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
replaying = st.session_state.get("research_cutoff") not in (None, options[-1])
header_slot = st.container()
with st.expander(":material/history: Replay · analyze as of an earlier date" + (" — ACTIVE" if replaying else ""), expanded=replaying):
    as_of = date_control("Analyze using only sessions up to", options, key="research_cutoff", context=data.source_hash)
    st.caption("Everything below (indicators, patterns, trade plan) is recomputed using only data up to this date — see what the analysis said back then.")
if as_of != options[-1]:
    st.warning(f"Replay active: analysis as of {as_of}. Later sessions are hidden.", icon=":material/history:")
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
calendar_flags = {label: quality[key] for key, label in (("missing_expected_dates", "missing trading day"),
                  ("unexpected_dates", "date not in the NSE trading calendar"), ("future_dates", "future-dated row")) if quality[key]}
if calendar_flags:
    def _dates(values):
        values = [str(v.get("date", v)) if isinstance(v, dict) else str(v) for v in values]
        return ", ".join(values[:4]) + (f" +{len(values) - 4} more" if len(values) > 4 else "")
    summary = "; ".join(f"{len(v)} {label}{'s' if len(v) > 1 else ''} ({_dates(v)})" for label, v in calendar_flags.items())
    st.caption(f":material/event_busy: Calendar check: {summary}. Often a special session (e.g. Muhurat trading) or a provider gap. Nothing was filled or removed; details in Data & exports.")
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
read = market_read(analysis)
with header_slot:
    render_header(analysis, symbol, adjustment, data, read)
render_readiness(analysis, data, symbol, adjustment)
if workspace == "Pattern research":
    render_event_study(analysis, data, settings, symbol, adjustment)
    st.stop()
frame, last = analysis.frame, analysis.frame.iloc[-1]

tab_names = ["Overview", "Patterns & momentum", "Trade plan & report", "Backtest lab", "Data & exports"]
requested_tab = st.session_state.pop("requested_research_tab", None)
chart_tab, analytical_tab, report_tab, backtest_tab, quality_tab = workspace_tabs(tab_names, key="research_active_tab", requested=requested_tab)
with analytical_tab:
    render_research(analysis)
with chart_tab:
    render_market_read(read)
    render_timeframes(read["mtf"])
    st.markdown("#### Chart")
    bands, overlays, lower, window = chart_controls()
    st.plotly_chart(price_chart(analysis, bands, overlays=overlays, lower=lower, window=window), width="stretch")
    st.caption(chart_window_caption(analysis, window))
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
                navigate("Pattern research")
            st.button("Study this observation type", key="study_observation", disabled=not bool(row.eligible),
                      on_click=open_study, args=(row.cohort, row.direction))
            if not row.eligible:
                st.caption("This diagnostic lifecycle state stays in the audit. Select a breakout, retest or geometric observation to study outcomes.")
        st.caption("Select a row to see how that pattern type has played out historically. 'Knowable on' is when the pattern could first be detected without hindsight.")
    else:
        st.caption("No supported geometries detected.")
    st.button("Explore historical outcomes", key="explore_outcomes", on_click=navigate, args=("Pattern research",))
    render_reference_links()

with report_tab:
    st.subheader(analysis.setup["status"])
    st.caption(f"Market read: **{read['verdict']}** — {read['summary']} The trade plan below uses its own fixed breakout rule, not the market read.")
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
    st.markdown(report_markdown(analysis, symbol, adjustment, read))

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
    st.download_button("Download research report", report_markdown(analysis, symbol, adjustment, read), "research-report.md", "text/markdown")
    st.download_button("Download calculated features", frame.to_csv(), "features.csv", "text/csv")

st.divider()
st.caption("Research and decision support only — not investment advice. No live orders. Pattern rules are heuristic and their predictive value is not validated; the app never shows a success probability it cannot support.")
