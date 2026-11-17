"""Scanner page: run the Analyze page's read over a watchlist and rank the results."""
import pandas as pd
import streamlit as st

from .paper_ui import record
from .providers import EXCHANGE_SUFFIX
from .scanner import NIFTY_50, NIFTY_50_AS_OF, VERDICT_ORDER, parse_watchlist, scan

PRESETS = {f"NIFTY 50 (as of {NIFTY_50_AS_OF})": NIFTY_50, "Custom list": []}


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_scan(symbols: tuple, exchange: str, period: str):
    return scan(list(symbols), exchange, period)


def _open_in_analyze(symbol, exchange):
    st.session_state.update(workspace_page="Analyze", data_source="Fetch by ticker",
                            ticker_symbol=symbol, ticker_exchange=exchange)


def render_scanner():
    st.title("Scanner")
    st.caption("Runs the same Market read, timeframe check and pattern detection as the Analyze page across a watchlist, "
               "so you can see which stocks have something happening. A starting point for research, not a buy list.")
    preset = st.segmented_control("Watchlist", list(PRESETS), default=list(PRESETS)[0], key="scan_preset", persist_state="session") or list(PRESETS)[0]
    if preset != "Custom list":
        default_text = ", ".join(PRESETS[preset])
    else:
        default_text = st.session_state.get("scan_custom", "RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK")
    cols = st.columns([5, 1.2, 1.2, 1.3])
    text = cols[0].text_area("Symbols (comma or space separated, max 100)", default_text, height=80,
                             key=f"scan_text_{preset}", disabled=preset != "Custom list")
    if preset == "Custom list":
        st.session_state["scan_custom"] = text
    exchange = cols[1].selectbox("Exchange", list(EXCHANGE_SUFFIX), key="scan_exchange", persist_state="session")
    period = cols[2].selectbox("History", ["1 year", "2 years", "5 years"], index=1, key="scan_period", persist_state="session",
                               help="2 years gives the 200-day average and 52-week range; longer is slower.")
    symbols = parse_watchlist(text)
    with cols[3]:
        st.write("")
        run = st.button(f"Scan {len(symbols)}", type="primary", help="Fetch and analyze every symbol in the list", icon=":material/radar:", width="stretch", disabled=not symbols)
    key = (tuple(symbols), exchange, period)
    if run:
        with st.spinner(f"Scanning {len(symbols)} stocks: fetching daily history and running the full analysis on each "
                        f"(about {max(5, round(len(symbols) * 1.2))} seconds the first time)…"):
            rows = _cached_scan(*key)
        st.session_state["scan_results"] = {"key": key, "rows": rows, "at": pd.Timestamp.now(tz="Asia/Kolkata").strftime("%d %b %H:%M IST")}
    saved = st.session_state.get("scan_results")
    if not saved:
        st.info("Press **Scan** to analyze the list. The first scan of 50 stocks takes about a minute; repeats within an hour are instant.",
                icon=":material/radar:")
        return
    if saved["key"] != key:
        st.caption(":material/info: Showing the previous scan. The list or settings changed; press Scan to refresh.")
    rows = pd.DataFrame(saved["rows"])
    failed = rows[rows["Error"].fillna("") != ""] if "Error" in rows else rows.iloc[:0]
    ok = rows.drop(failed.index)
    if ok.empty:
        st.error("No stock could be analyzed. Check the symbols or your internet connection.")
        with st.expander("Errors"):
            st.dataframe(failed[["Symbol", "Error"]], hide_index=True, width="stretch")
        return
    ok = ok.assign(_order=ok["Market read"].map(VERDICT_ORDER)).sort_values(["_order", "Up votes", "Down votes"], ascending=[True, False, True]).drop(columns="_order")
    counts = ok["Market read"].value_counts()
    metrics = st.columns(6)
    for col, label in zip(metrics, ["Bullish", "Leaning bullish", "Mixed / conflicting", "Leaning bearish", "Bearish"]):
        col.metric(label, int(counts.get(label, 0)))
    metrics[5].metric("With recent pattern", int((ok["Recent patterns (n)"] > 0).sum()))
    st.caption(f"Scanned {len(ok)} of {len(rows)} at {saved['at']} · daily candles from Yahoo Finance · last completed session per stock in 'As of'.")

    f1, f2, f3 = st.columns([2.5, 2, 1.5])
    verdicts = f1.multiselect("Market read", list(VERDICT_ORDER)[:-1], key="scan_filter_verdict", placeholder="All")
    aligned = f2.multiselect("Timeframe alignment", sorted(ok["Alignment"].unique()), key="scan_filter_align", placeholder="All")
    only_patterns = f3.toggle("Only with a recent pattern", key="scan_filter_pattern")
    view = ok
    if verdicts:
        view = view[view["Market read"].isin(verdicts)]
    if aligned:
        view = view[view["Alignment"].isin(aligned)]
    if only_patterns:
        view = view[view["Recent patterns (n)"] > 0]
    columns = ["Symbol", "Close", "Day %", "1M %", "Market read", "Up votes", "Down votes", "Alignment", "Daily trend", "Weekly",
               "Monthly", "RSI", "ADX", "Rel. volume", "From 52w high %", "Recent pattern", "As of"]
    event = st.dataframe(
        view[columns], hide_index=True, width="stretch", height=min(38 * (len(view) + 1) + 3, 720),
        on_select="rerun", selection_mode="single-row", key="scan_table",
        column_config={
            "Close": st.column_config.NumberColumn(format="%.2f"),
            "Day %": st.column_config.NumberColumn(format="%+.2f"),
            "1M %": st.column_config.NumberColumn(format="%+.1f"),
            "From 52w high %": st.column_config.NumberColumn(format="%+.1f", help="Distance below the 52-week high"),
            "Up votes": st.column_config.NumberColumn("↑", help="Evidence families pointing up (of 6)"),
            "Down votes": st.column_config.NumberColumn("↓", help="Evidence families pointing down (of 6)"),
            "Rel. volume": st.column_config.NumberColumn(format="%.2f×"),
            "Recent pattern": st.column_config.TextColumn(width="large", help="Newest still-live directional pattern in the last 10 sessions"),
        })
    chosen = event.selection.rows if event and event.selection else []
    if chosen:
        row = view.iloc[chosen[0]]
        symbol = row["Symbol"]
        a, b, _ = st.columns([1.4, 2.2, 2])
        a.button(f"Open {symbol} in Analyze", type="primary", icon=":material/open_in_new:",
                 on_click=_open_in_analyze, args=(symbol, exchange))
        if b.button(f"Paper-trade {symbol} (2 ATR stop, 2R, 20 sessions)", icon=":material/bookmark_add:",
                    disabled=pd.isna(row.get("ATR"))):
            ok, message = record(dict(symbol=symbol, provider_symbol=row["Provider symbol"], exchange=exchange,
                                      signal_date=row["As of"], signal_close=float(row["Close"]), atr=float(row["ATR"]),
                                      source="Scanner", pattern=row["Recent pattern"] or "",
                                      snapshot={"verdict": row["Market read"], "alignment": row["Alignment"], "rsi": row["RSI"]}),
                                 last_bar_date=row["As of"])
            (st.success if ok else st.warning)(message)
    else:
        st.caption("Select a row to open that stock in Analyze.")
    st.download_button("Download scan (CSV)", view[columns].to_csv(index=False), "signal-ledger-scan.csv", "text/csv")
    if not failed.empty:
        with st.expander(f"{len(failed)} symbol(s) could not be analyzed"):
            st.dataframe(failed[["Symbol", "Error"]], hide_index=True, width="stretch")
    st.caption("Market read counts agreeing evidence families; it is not a probability or a recommendation. "
               "Check each stock on the Analyze page before acting on anything.")
