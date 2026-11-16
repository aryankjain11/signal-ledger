"""Watchlist-wide pattern research page."""
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .analysis import analyze
from .data import load_bars
from .event_study import TREND_LABELS, VOLUME_LABELS, StudyRules
from .event_study_ui import cohort_label
from .models import Settings
from .pooled_study import pooled_study
from .providers import EXCHANGE_SUFFIX, fetch_daily
from .scanner import NIFTY_50, NIFTY_50_AS_OF, parse_watchlist

PRESETS = {f"NIFTY 50 (as of {NIFTY_50_AS_OF})": NIFTY_50, "Custom list": []}


def _load(symbol, exchange, period):
    try:
        fetched = fetch_daily(symbol, exchange, period)
        data = load_bars(fetched.csv_bytes, f"{fetched.provider_symbol}.csv")
        return fetched.display_symbol, data, None
    except Exception as exc:  # reported per symbol, never fatal
        return symbol, None, str(exc)


@st.cache_data(ttl=3600, show_spinner=False, max_entries=4)
def load_universe(symbols: tuple, exchange: str, period: str):
    """Fetch + full analysis for each symbol, shared by the pooled study and the portfolio backtest."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        loaded = list(pool.map(lambda s: _load(s, exchange, period), symbols))
    stocks, failures = {}, []
    for symbol, data, error in loaded:
        if data is None:
            failures.append({"symbol": symbol, "error": error})
            continue
        analysis = analyze(data, Settings())
        stocks[symbol] = (analysis.frame, analysis.events, {"source_sha256": data.source_hash})
    return stocks, failures


@st.cache_data(ttl=3600, show_spinner=False)
def run_pooled(symbols: tuple, exchange: str, period: str, rule_values: dict):
    stocks, failures = load_universe(symbols, exchange, period)
    return pooled_study(stocks, StudyRules(**rule_values)), failures


def _pct(x):
    return None if x is None or pd.isna(x) else 100 * x


def difference_chart(summary, horizon):
    s = summary.loc[summary.horizon.eq(horizon) & summary.difference_low.notna()].copy()
    s = s.sort_values("difference_from_baseline")
    labels = [cohort_label(c) for c in s.cohort]
    has = s.difference_low.notna()
    fig = go.Figure()
    clear = (s.difference_low > 0) | (s.difference_high < 0)
    fig.add_bar(y=labels, x=s.difference_from_baseline * 100, orientation="h",
                marker_color=["#36d6a4" if v > 0 else "#ff6b82" for v in s.difference_from_baseline],
                marker_opacity=[1.0 if c else 0.45 for c in clear],
                error_x=dict(type="data", symmetric=False,
                             array=((s.difference_high.astype(float) - s.difference_from_baseline) * 100).where(has, 0.0).fillna(0.0),
                             arrayminus=((s.difference_from_baseline - s.difference_low.astype(float)) * 100).where(has, 0.0).fillna(0.0),
                             color="#dfe7f3", thickness=1.2),
                customdata=s[["events", "stocks", "distinct_dates"]].to_numpy(),
                hovertemplate="%{y}<br>%{x:.2f} pp vs ordinary days<br>%{customdata[0]} events · %{customdata[1]} stocks · %{customdata[2]} dates<extra></extra>")
    fig.add_vline(x=0, line_color="#576579")
    fig.update_layout(template="plotly_dark", height=max(320, 34 * len(s) + 120), paper_bgcolor="#101a2b",
                      plot_bgcolor="#101a2b", margin=dict(l=10, r=20, t=50, b=40), showlegend=False,
                      title=f"{horizon} sessions after detection: move vs the same stocks' ordinary days",
                      xaxis_title="Difference in mean move (percentage points)", yaxis=dict(automargin=True))
    return fig


def render_pooled_research():
    st.caption("Runs the same pattern detection on every stock in a watchlist, measures what happened after each "
               "occurrence, and compares it with that stock's own ordinary days. Pooling many stocks turns a "
               "handful of examples into hundreds.")
    preset = st.segmented_control("Watchlist", list(PRESETS), default=list(PRESETS)[0], key="pool_preset",
                                  persist_state="session") or list(PRESETS)[0]
    default_text = ", ".join(PRESETS[preset]) if preset != "Custom list" else st.session_state.get(
        "pool_custom", "RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, SBIN, LT, ITC")
    with st.form("pooled_form"):
        text = st.text_area("Symbols (max 100)", default_text, height=70, key=f"pool_text_{preset}",
                            disabled=preset != "Custom list")
        c1, c2, c3, c4 = st.columns(4)
        exchange = c1.selectbox("Exchange", list(EXCHANGE_SUFFIX), key="pool_exchange")
        period = c2.selectbox("History", ["2 years", "5 years", "10 years"], index=1, key="pool_period",
                              help="More history gives more events. 5 years of NIFTY 50 takes about a minute the first time.")
        horizons = c3.multiselect("Horizons (sessions)", [1, 3, 5, 10, 20, 40, 60], default=[5, 10, 20], key="pool_horizons")
        reference = c4.selectbox("Measured from", ["Next observed open", "Detection close"], key="pool_reference",
                                 help="Next open: what you could act on after seeing the pattern at the close.")
        c5, c6, _ = st.columns([1, 1, 2])
        trend = c5.selectbox("Trend at detection", ["All", *TREND_LABELS], key="pool_trend")
        volume = c6.selectbox("Volume at detection", ["All", *VOLUME_LABELS], key="pool_volume")
        run = st.form_submit_button("Run watchlist study", type="primary", icon=":material/science:")
    if preset == "Custom list":
        st.session_state["pool_custom"] = text
    symbols = parse_watchlist(text)
    if run:
        if not symbols or not horizons:
            st.warning("Choose at least one symbol and one horizon.")
            return
        rules = dict(horizons=tuple(sorted(horizons)), reference=reference, trend=trend, volume=volume)
        with st.spinner(f"Studying {len(symbols)} stocks: fetching history, detecting patterns and measuring outcomes "
                        f"(about {max(10, round(len(symbols) * 1.5))} seconds the first time)…"):
            result, failures = run_pooled(tuple(symbols), exchange, period, rules)
        st.session_state["pooled_result"] = {"result": result, "failures": failures, "symbols": len(symbols),
                                             "period": period, "horizons": rules["horizons"]}
    saved = st.session_state.get("pooled_result")
    if not saved:
        st.info("Choose a watchlist and press **Run watchlist study**.", icon=":material/science:")
        return
    result, failures = saved["result"], saved["failures"]
    summary = result.summary
    if summary.empty:
        st.warning("No pattern occurrences with complete outcomes were found. Try more history or more stocks.")
        _coverage(result, failures)
        return
    stocks_ok = result.audit["stocks_requested"]
    m = st.columns(4)
    m[0].metric("Stocks studied", f"{stocks_ok} of {saved['symbols']}")
    m[1].metric("Pattern types", summary.cohort.nunique())
    first_h = min(saved["horizons"])
    m[2].metric("Events (complete)", int(summary.loc[summary.horizon.eq(first_h), "events"].sum()))
    with_interval = summary.difference_low.notna().sum()
    m[3].metric("Rows with an interval", int(with_interval), help="Enough matched events and distinct dates to show a date-clustered 90% interval.")

    horizon = st.segmented_control("Horizon", list(saved["horizons"]), default=saved["horizons"][min(1, len(saved["horizons"]) - 1)],
                                   key="pool_view_horizon", format_func=lambda h: f"{h} sessions") or saved["horizons"][0]
    view = summary.loc[summary.horizon.eq(horizon)].sort_values("events", ascending=False)
    st.markdown("#### What followed each pattern")
    st.caption("**vs ordinary days** compares the move after the pattern with the same stocks' moves on days without one, "
               "in the same trend and volume conditions. Bearish patterns count a fall as a positive move. "
               "The 90% range resamples whole dates, so a market-wide day is not counted as many independent examples.")
    table = pd.DataFrame({
        "Pattern": view.cohort.map(cohort_label),
        "Events": view.events, "Stocks": view.stocks, "Distinct dates": view.distinct_dates,
        "Mean move %": view.mean_return.map(_pct), "Median move %": view.median_return.map(_pct),
        "Went the pattern's way %": view.positive_fraction.map(_pct),
        "vs ordinary days (pp)": view.difference_from_baseline.map(_pct),
        "90% range low": view.difference_low.map(_pct), "90% range high": view.difference_high.map(_pct),
        "Most events from": view.top_stock + " (" + (view.top_stock_share * 100).round(0).astype(int).astype(str) + "%)",
        "Note": view.sample_note})
    pick = st.dataframe(table, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row",
                        key="pool_table", column_config={c: st.column_config.NumberColumn(format="%+.2f") for c in
                        ("Mean move %", "Median move %", "vs ordinary days (pp)", "90% range low", "90% range high")} |
                        {"Went the pattern's way %": st.column_config.NumberColumn(format="%.0f")})
    ranged = view.dropna(subset=["difference_low"])
    if len(ranged):
        clear = int(((ranged.difference_low > 0) | (ranged.difference_high < 0)).sum())
        st.info(f"At {horizon} sessions, **{clear} of {len(ranged)}** patterns with a range sit clearly away from ordinary days "
                f"(range excludes zero). With this many patterns tested, about **{len(ranged) / 10:.0f}** would do so by chance "
                "alone even if no pattern worked. Treat a lone result as a lead to re-test on other stocks and periods, "
                "not as a proven edge.", icon=":material/rule:")
    hidden = int((view.difference_low.isna() & view.difference_from_baseline.notna()).sum())
    if len(ranged):
        st.plotly_chart(difference_chart(summary, horizon), width="stretch")
    st.caption("Bars show patterns with enough matched events (30+) on enough distinct dates (20+) for a range. "
               "A range that crosses zero means the difference from ordinary days is not distinguishable from noise here."
               + (f" {hidden} smaller-sample pattern(s) are left out of the chart (see the table); their averages swing too much to compare." if hidden else ""))
    rows = pick.selection.rows if pick and pick.selection else []
    if rows:
        cohort = view.iloc[rows[0]].cohort
        st.markdown(f"#### {cohort_label(cohort)} · {horizon} sessions")
        per = result.by_stock.loc[result.by_stock.cohort.eq(cohort) & result.by_stock.horizon.eq(horizon)].sort_values("events", ascending=False)
        left, right = st.columns([1, 1.3])
        left.dataframe(pd.DataFrame({"Stock": per.symbol, "Events": per.events, "Mean move %": per.mean_return * 100,
                                     "vs ordinary days (pp)": per.difference_from_baseline * 100}),
                       hide_index=True, width="stretch", height=360,
                       column_config={c: st.column_config.NumberColumn(format="%+.2f") for c in ("Mean move %", "vs ordinary days (pp)")})
        done = result.outcomes.loc[result.outcomes.cohort.eq(cohort) & result.outcomes.horizon.eq(horizon)
                                   & result.outcomes.outcome_state.eq("Complete")]
        fig = go.Figure(go.Histogram(x=done.forward_return * 100, nbinsx=40, marker_color="#6ca6ff"))
        fig.add_vline(x=0, line_color="#576579")
        fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="#101a2b", plot_bgcolor="#101a2b",
                          margin=dict(l=10, r=10, t=30, b=40), xaxis_title="Move after the pattern (%)", yaxis_title="Events",
                          title="Spread of outcomes")
        right.plotly_chart(fig, width="stretch")
    else:
        st.caption("Select a row to see which stocks it came from and the spread of outcomes.")
    st.download_button("Download all event outcomes (CSV)", result.outcomes.to_csv(index=False),
                       "signal-ledger-pooled-outcomes.csv", "text/csv")
    _coverage(result, failures)
    with st.expander("Method and limits"):
        st.write(result.audit["method"])
        st.write(result.audit["interval"])
        st.write(result.audit["limits"])


def _coverage(result, failures):
    coverage = pd.DataFrame(result.audit["coverage"])
    label = f"Coverage · {len(coverage)} stocks analyzed" + (f" · {len(failures)} could not be fetched" if failures else "")
    with st.expander(label):
        if not coverage.empty:
            st.dataframe(coverage, hide_index=True, width="stretch")
        if failures:
            st.dataframe(pd.DataFrame(failures), hide_index=True, width="stretch")
