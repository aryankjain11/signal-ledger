import os
import json
from copy import deepcopy

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .analysis import analyze, json_safe
from .charts import price_chart
from .comparison import compare_stocks, synthetic_pair
from .data import load_bars
from .providers import EXCHANGE_SUFFIX, PERIODS, PROVIDER_ADJUSTMENT, fetch_daily
from .datasets import Instrument, attach_passport
from .models import Settings
from .ui_state import retained_upload, completed_confirmation, date_control, reset_dates, workspace_tabs


@st.cache_data(ttl=3600, show_spinner="Fetching daily history…")
def _cached_fetch(symbol, exchange, period):
    return fetch_daily(symbol, exchange, period)


def render_comparison():
    st.title("Compare stocks")
    st.write("Compare price performance, risk, momentum and return correlation over the same observation window.")
    modes = ["Fetch two tickers", "Synthetic pair", "Upload two stocks"]
    default = 1 if os.environ.get("SIGNAL_LEDGER_DEFAULT_SOURCE") == "Demo data" else 0
    mode = st.radio("Comparison data", modes, index=default, key="comparison_mode", horizontal=True, persist_state="session")
    data, labels = [], []
    synthetic = mode == "Synthetic pair"
    if mode == "Fetch two tickers":
        cols = st.columns([2, 2, 1, 1])
        first = cols[0].text_input("Stock A", "HDFCBANK", key="compare_ticker_A", persist_state="session")
        second = cols[1].text_input("Stock B", "ICICIBANK", key="compare_ticker_B", persist_state="session")
        exchange = cols[2].selectbox("Exchange", list(EXCHANGE_SUFFIX), key="compare_exchange", persist_state="session")
        period = cols[3].selectbox("History", list(PERIODS), index=1, key="compare_period", persist_state="session")
        if not first.strip() or not second.strip():
            st.info("Enter two tickers to compare.")
            return
        for ticker in (first, second):
            try:
                fetched = _cached_fetch(ticker, exchange, period)
            except ValueError as exc:
                st.error(f"Couldn't load {ticker.strip().upper()}. Check the symbol and your connection, or switch to Synthetic pair / Upload.")
                with st.expander("Technical details"):
                    st.code(str(exc), language=None)
                return
            loaded = load_bars(fetched.csv_bytes, f"{fetched.provider_symbol}.csv")
            attach_passport(loaded, instrument=Instrument(fetched.exchange if fetched.exchange != "As typed" else "Unknown", fetched.provider_symbol),
                provider="Yahoo Finance via yfinance", input_format="Provider daily history", adjustment=PROVIDER_ADJUSTMENT,
                sources=[{"name": f"{fetched.provider_symbol}.csv", "sha256": loaded.source_hash}])
            data.append(loaded)
            labels.append(fetched.display_symbol)
        st.caption(f"Daily candles from Yahoo Finance · {PROVIDER_ADJUSTMENT.lower()}. Price returns only (no dividends).")
    elif synthetic:
        st.info("SYNTHETIC PAIR · DEMO-A and DEMO-B are invented observations. Business dates are a fixture, not an exchange calendar.")
        inputs = list(zip(("DEMO-A", "DEMO-B"), synthetic_pair()))
        for label, content in inputs:
            st.download_button(f"Download {label} example", content, f"{label}.csv", "text/csv")
            loaded = load_bars(content, f"{label}.csv")
            attach_passport(loaded, instrument=Instrument("Synthetic", label), provider="Original synthetic pair fixture",
                input_format="Standard CSV", adjustment="Synthetic example", sources=[{"name": f"{label}.csv", "sha256": loaded.source_hash}], is_synthetic=True)
            data.append(loaded)
            labels.append(label)
    else:
        cols = st.columns(2)
        files = []
        declarations = []
        entered_labels = []
        for i, col in enumerate(cols):
            with col:
                label = "A" if i == 0 else "B"
                st.subheader(f"Stock {label}")
                files.append(retained_upload(f"Stock {label} daily CSV/XLSX", type=["csv", "xlsx"], key=f"compare_upload_{label}"))
                entered_labels.append(st.text_input(f"Stock {label} label (fallback)", f"Stock-{label}", key=f"compare_label_{label}", persist_state="session"))
                declarations.append(st.selectbox(f"Stock {label} price basis", ["Unknown / unverified", "Unadjusted OHLC", "Consistently adjusted OHLC"], key=f"compare_basis_{label}", persist_state="session"))
        st.caption("Native NSE stock-history CSVs are accepted unchanged. This comparison does not import UDiFF ZIPs or apply an action ledger.")
        if not all(files):
            st.info("Upload both stocks to compare them.")
            return
        if not completed_confirmation("Both files contain completed daily INR observations",files,key="compare_complete"):
            st.warning("Confirm completed daily observations before comparison.")
            return
        try:
            for i, uploaded in enumerate(files):
                loaded = load_bars(uploaded.getvalue(), uploaded.name)
                meta = dict(loaded.metadata)
                label = meta.get("file_symbol") or entered_labels[i].strip()
                attach_passport(loaded, instrument=Instrument("NSE" if meta.get("detected_nse_quote") else "Unknown", label, meta.get("file_series", "")),
                    provider="User-supplied comparison file", input_format=meta.get("input_format", "Standard CSV/XLSX"), adjustment=declarations[i],
                    sources=[{"name": uploaded.name, "sha256": loaded.source_hash}], normalization=meta.get("normalization"))
                data.append(loaded)
                labels.append(label)
        except ValueError as exc:
            st.error(f"Comparison upload could not be used: {exc}")
            return
        if data[0].source_hash == data[1].source_hash:
            st.warning("Both uploads contain the same bytes. This is a same-dataset comparison, not independent stock evidence.")
        st.warning("Adjustment basis is user-declared. Splits, dividends and missing observations can distort comparison and correlation.")
    common = data[0].bars.index.intersection(data[1].bars.index)
    if len(common) < 2:
        st.error("The two stocks need at least two common observation dates.")
        return
    options = common.strftime("%Y-%m-%d").tolist()
    context = '|'.join(d.source_hash for d in data)
    start, end = date_control("Shared comparison period",options,key="comparison_period",context=context,ranged=True)
    st.button("Use all shared dates",key="all_comparison_dates",on_click=reset_dates,args=("comparison_period",options))
    window = int(st.number_input("Rolling correlation window (matched intervals)", min_value=5, max_value=252, value=20, key="correlation_window",persist_state="session"))
    try:
        pair = compare_stocks(data[0].bars.loc[start:end], data[1].bars.loc[start:end], window=window)
    except ValueError as exc:
        st.error(str(exc))
        return
    summary = pair.summary
    cols = st.columns(3)
    value = summary["pearson_return_correlation"]
    cols[0].metric("Return correlation (Pearson)", "Unavailable" if value is None else f"{value:.3f}")
    cols[1].metric("Matched return intervals", summary["paired_intervals"])
    cols[2].metric("Common price dates", summary["common_dates"])
    st.caption(f"{labels[0]} versus {labels[1]} · {start}–{end} · {summary['correlation_status']}")
    st.caption(summary["method"])
    if summary["paired_intervals"] < 60:
        st.warning("Fewer than 60 matched intervals: correlation and risk summaries can be unstable.")
    if summary["excluded_unmatched_return_intervals"] or summary["only_A_dates"] or summary["only_B_dates"]:
        st.warning(f"Coverage differs: A-only dates {summary['only_A_dates']}, B-only dates {summary['only_B_dates']}; {summary['excluded_unmatched_return_intervals']} return interval(s) excluded because their endpoints do not match.")
    metrics = pd.DataFrame(summary["metrics"])
    metrics["stock"] = labels
    for column in ("period_price_return", "observed_date_max_drawdown", "matched_interval_volatility"):
        metrics[column] = metrics[column] * 100
    st.dataframe(metrics.rename(columns={"stock": "Stock", "period_price_return": "Period price return (%)", "observed_date_max_drawdown": "Observed-date drawdown (%)", "matched_interval_volatility": "Matched-interval return volatility (%)", "start_close":"Starting close", "end_close":"Ending close", "observations":"Common prices", "native_observations":"Source observations"}), hide_index=True, width="stretch")
    performance, correlation, technical, exports = workspace_tabs(["Performance & risk", "Correlation", "Side-by-side analysis", "Comparison exports"],key="comparison_active_tab")
    def lines(frame, title, percent=False):
        fig = go.Figure()
        for i, column in enumerate(frame):
            fig.add_scatter(x=frame.index, y=frame[column], name=labels[i], mode="lines")
        fig.update_layout(title=title, template="plotly_dark", height=340, margin=dict(l=10, r=10, t=45, b=10))
        if percent:
            fig.update_yaxes(tickformat=".1%")
        st.plotly_chart(fig, width="stretch")
    with performance:
        lines(pair.indexed, "Price performance · both start at 100")
        lines(pair.drawdowns, "Drawdown on common observed dates", True)
        relative = pair.indexed.iloc[:, 0] / pair.indexed.iloc[:, 1]
        fig = go.Figure(go.Scatter(x=relative.index, y=relative, mode="lines", name=f"{labels[0]} / {labels[1]}"))
        fig.update_layout(title="Relative performance · above 1 means A has outperformed B since the selected start", template="plotly_dark", height=300)
        st.plotly_chart(fig, width="stretch")
    with correlation:
        fig = go.Figure(go.Scatter(x=pair.rolling.index, y=pair.rolling, name="Rolling return correlation", mode="lines"))
        fig.update_layout(title=f"Rolling correlation · {window} matched intervals", template="plotly_dark", height=330, yaxis_range=[-1, 1])
        st.plotly_chart(fig, width="stretch")
        if pair.rolling.notna().sum() == 0:
            st.info(f"Rolling correlation is unavailable for this window. It needs {window} matched, nonconstant return intervals. Select more shared dates or reduce the rolling window.")
        scatter = go.Figure(go.Scatter(x=pair.returns.A, y=pair.returns.B, mode="markers", text=pair.returns.index.strftime("%Y-%m-%d")))
        scatter.update_layout(title="Matched return scatter", xaxis_title=labels[0], yaxis_title=labels[1], template="plotly_dark", height=330)
        scatter.update_xaxes(tickformat=".1%")
        scatter.update_yaxes(tickformat=".1%")
        st.plotly_chart(scatter, width="stretch")
        rank = summary["spearman_return_correlation"]
        st.write("Spearman rank correlation: " + ("unavailable" if rank is None else f"{rank:.3f}"))
        st.caption("Correlation describes co-movement in this sample. It does not establish causation, diversification safety, cointegration or a profitable pairs trade. Constant returns have undefined correlation. Spearman ranks returns rounded to 12 decimals to stabilize floating-point ties.")
    with technical:
        st.caption("Both charts show the selected period. Indicators/context use each file's uploaded history through the selected end; no later observations are used.")
        for i, col in enumerate(st.columns(2)):
            with col:
                st.subheader(labels[i])
                visible = deepcopy(data[i])
                visible.bars = visible.bars.loc[:end]
                if len(visible.bars) < 3:
                    st.info("At least three uploaded observations through this end date are needed for technical analysis. Price comparison remains available.")
                    continue
                analysis = analyze(visible, Settings())
                st.write(analysis.trend)
                for text in analysis.momentum.get("interpretation", []):
                    st.caption(text)
                shown = deepcopy(analysis)
                shown.frame = shown.frame.loc[start:end]
                st.plotly_chart(price_chart(shown), width="stretch", key=f"comparison_technical_{i}")
                recent = sorted([e for e in analysis.events if e["detected_at"] >= start], key=lambda e: e["detected_at"], reverse=True)[:10]
                if recent:
                    st.dataframe(pd.DataFrame([{k: e.get(k) for k in ("name", "status", "detected_at")} for e in recent]).rename(columns={"name":"Observation","status":"State","detected_at":"Knowable on"}), hide_index=True, width="stretch")
    with exports:
        evidence = {"comparison": summary, "labels": labels, "source_passports": [d.metadata for d in data]}
        st.download_button("Download comparison evidence", json.dumps(json_safe(evidence), indent=2, allow_nan=False), "comparison.json", "application/json")
        st.download_button("Download common prices and indexed performance", pair.prices.join(pair.indexed.add_suffix(" · index100")).to_csv(), "comparison-prices.csv", "text/csv")
        st.download_button("Download matched return intervals", pair.returns.to_csv(), "comparison-returns.csv", "text/csv")
        st.caption(summary["limitations"])
        for i, d in enumerate(data):
            st.caption(f"{labels[i]} · declared basis: {d.metadata['adjustment_basis']} · source SHA-256: {d.source_hash}")
