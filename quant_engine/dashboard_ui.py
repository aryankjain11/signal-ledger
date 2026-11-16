"""Presentation helpers for the Analyze page: header, market read, chart controls."""
from html import escape

import pandas as pd
import streamlit as st

STYLE = """<style>
 .block-container {padding-top:2.2rem; max-width:1480px}
 h1 {letter-spacing:-1px; font-weight:650!important}
 [data-testid="stMetric"] {background:#101a2b;border:1px solid #253248;border-radius:12px;padding:14px 16px}
 [data-testid="stMetricLabel"] {color:#97a7bf}
 [data-testid="stMetricValue"] {font-size:1.75rem}
 .tf-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:6px 0}
 .tf {background:#101a2b;border:1px solid #253248;border-radius:10px;padding:10px 14px}
 .tf .h {display:flex;justify-content:space-between;align-items:baseline;font-weight:650;color:#dfe7f3}
 .tf .s {font-size:20px;font-weight:700;margin:2px 0}
 .tf .d {color:#97a7bf;font-size:12.5px;line-height:1.35}
 [data-testid="stSidebar"] {border-right:1px solid #253248}
 [data-testid="stSidebar"] [role="radiogroup"] label {padding:3px 0}
 .stTabs [data-baseweb="tab-list"] {gap:22px;border-bottom:1px solid #253248}
 .brand {font-size:21px;font-weight:700;letter-spacing:-.3px;color:#e8eef8}
 .brand-sub {color:#7f8ea6;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px}
 .side-head {color:#7f8ea6;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;font-weight:700;margin-bottom:4px}
 .hdr {display:flex;align-items:flex-end;gap:22px;flex-wrap:wrap;margin:4px 0 6px}
 .hdr .sym {font-size:34px;font-weight:700;letter-spacing:-1px;color:#e8eef8;line-height:1}
 .hdr .px {font-size:30px;font-weight:600;color:#e8eef8;line-height:1}
 .hdr .chg {font-size:17px;font-weight:600}
 .hdr .meta {color:#8a99b2;font-size:13px;padding-bottom:3px}
 .up {color:#36d6a4} .down {color:#ff6b82} .flat {color:#97a7bf}
 .verdict {display:inline-block;border-radius:999px;padding:5px 14px;font-weight:700;font-size:14px;border:1px solid}
 .v-bull {color:#36d6a4;border-color:#1f6b55;background:#0f2a24}
 .v-bear {color:#ff6b82;border-color:#7a2f3c;background:#2a1219}
 .v-mixed {color:#f6c86a;border-color:#6d5a2e;background:#2a2312}
 .v-none {color:#97a7bf;border-color:#33415a;background:#141e2f}
 .fam-grid {display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;margin:8px 0 4px}
 .fam {background:#101a2b;border:1px solid #253248;border-left:4px solid #33415a;border-radius:10px;padding:10px 12px}
 .fam.b1 {border-left-color:#36d6a4} .fam.b-1 {border-left-color:#ff6b82} .fam.b0 {border-left-color:#f6c86a}
 .fam.ctx {border-style:dashed;border-left-style:solid;border-left-color:#6ca6ff}
 .fam .t {display:flex;justify-content:space-between;font-weight:650;color:#dfe7f3;font-size:14px}
 .fam .d {color:#97a7bf;font-size:12.5px;margin-top:4px;line-height:1.35}
 .lvl {width:100%;border-collapse:collapse;font-size:13px}
 .lvl td {padding:5px 6px;border-bottom:1px solid #1d2839;color:#cfd8e6}
 .lvl tr.now td {color:#e8eef8;font-weight:700;background:#141f33}
 .welcome {background:#101a2b;border:1px solid #253248;border-radius:14px;padding:26px 28px;margin-top:8px}
 .welcome h3 {margin-top:0}
</style>"""

VERDICT_CLASS = {"Bullish": "v-bull", "Leaning bullish": "v-bull", "Bearish": "v-bear", "Leaning bearish": "v-bear",
                 "Mixed / conflicting": "v-mixed", "Insufficient evidence": "v-none"}


def render_welcome(upload_mode=False):
    if upload_mode:
        st.info("Upload one symbol's daily file in the sidebar: an original NSE stock-history CSV works as downloaded, "
                "or any CSV/XLSX with date, open, high, low, close, volume columns.", icon=":material/upload_file:")
        return
    else:
        body = ("<h3>Analyze any NSE or BSE stock</h3><p>Type a ticker in the sidebar (for example <b>RELIANCE</b>, <b>TCS</b>, "
                "<b>HDFCBANK</b>, or the index <b>^NSEI</b>). Signal Ledger fetches completed daily candles and reads trend, structure, "
                "momentum, volume flow and chart patterns, then tests explicit strategies on the history.</p>")
    st.markdown(f'<div class="welcome">{body}<p style="color:#8a99b2">No account or API key needed. '
                "Nothing here places orders.</p></div>", unsafe_allow_html=True)


def render_header(analysis, symbol, adjustment, data, read):
    frame = analysis.frame
    last = frame.iloc[-1]
    prev = frame.close.iloc[-2] if len(frame) > 1 else last.close
    change = last.close - prev
    pct = 100 * change / prev if prev else 0.0
    cls = "up" if change > 0 else "down" if change < 0 else "flat"
    provider = data.metadata.get("passport", {}).get("provider") if isinstance(data.metadata.get("passport"), dict) else None
    meta = f"{frame.index[-1]:%a %d %b %Y} · {len(frame):,} sessions · {escape(adjustment)}"
    source = escape(str(data.metadata.get("passport", {}).get("provider", ""))) if isinstance(data.metadata.get("passport"), dict) else ""
    st.markdown(f'<div class="hdr"><span class="sym">{escape(symbol)}</span>'
                f'<span class="meta">{meta}</span></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Last close", f"{last.close:,.2f}", f"{pct:+.2f}%")
    cols[1].metric("Market read", read["verdict"], f"{read['bullish']}↑ {read['bearish']}↓ of {read['available']}",
                   delta_color="off", delta_arrow="off", help=read["basis"])
    cols[2].metric("RSI · 14 sessions", f"{last.rsi_14:.1f}" if pd.notna(last.rsi_14) else "Warming up")
    cols[3].metric("Relative volume", f"{last.relative_volume:.2f}×" if pd.notna(last.relative_volume) else "Warming up",
                   help="Today's volume divided by the average of the previous 20 sessions.")


def render_market_read(read):
    st.markdown("#### Market read")
    st.caption(f"{read['summary']} One vote per evidence family, so related indicators are not double-counted. {read['basis']}")
    left, right = st.columns([1.75, 1.25])
    with left:
        cards = []
        for f in read["families"]:
            klass = "ctx" if not f["votes"] else f"b{f['signal']}" if f["signal"] is not None else ""
            label = "context" if not f["votes"] else f["label"]
            tone = "up" if f["signal"] == 1 else "down" if f["signal"] == -1 else "flat"
            cards.append(f'<div class="fam {klass}"><div class="t"><span>{escape(f["family"])}</span>'
                         f'<span class="{tone}">{escape(label)}</span></div><div class="d">{escape(f["detail"])}</div></div>')
        st.markdown('<div class="fam-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)
    with right:
        st.markdown("**Key levels**")
        rows = []
        placed = False
        for level in read["levels"]:
            if not placed and level["distance_pct"] < 0:
                rows.append('<tr class="now"><td>▶ Price now</td><td></td><td></td></tr>')
                placed = True
            span = f"{level['low']:,.2f}" if level["low"] == level["high"] else f"{level['low']:,.2f}–{level['high']:,.2f}"
            atr = f" · {level['distance_atr']:+.1f} ATR" if level["distance_atr"] is not None else ""
            tone = "down" if level["kind"] == "Resistance" else "up" if level["kind"] == "Support" else "flat"
            rows.append(f'<tr><td class="{tone}">{escape(level["label"])}</td><td>{span}</td>'
                        f'<td>{level["distance_pct"]:+.1f}%{atr}</td></tr>')
        if not placed:
            rows.append('<tr class="now"><td>▶ Price now</td><td></td><td></td></tr>')
        st.markdown('<table class="lvl">' + "".join(rows) + "</table>", unsafe_allow_html=True)
        st.caption("Zones cluster confirmed swing points (±0.25 ATR). Distances are from the last close.")


OVERLAYS = ["EMA20", "EMA50", "SMA200", "Supertrend", "Donchian 20", "Keltner", "VWAP 20"]
LOWER = ["RSI", "MACD", "ADX / DI", "Stochastic", "MFI", "OBV"]
WINDOWS = {"3M": 63, "6M": 126, "1Y": 250, "2Y": 500, "All": None}


def chart_controls():
    cols = st.columns([3, 1.2, 2, 1.5])
    overlays = cols[0].multiselect("Overlays", OVERLAYS, default=["EMA20", "EMA50"], key="chart_overlays", persist_state="session")
    lower = cols[1].selectbox("Lower panel", LOWER, key="chart_lower", persist_state="session")
    window = cols[2].segmented_control("Range", list(WINDOWS), default="1Y", key="chart_window", persist_state="session") or "1Y"
    with cols[3]:
        st.write("")
        bands = st.checkbox("Show Bollinger bands", key="show_bands", persist_state="session")
    return bands, overlays, lower, WINDOWS[window]


def render_timeframes(mtf):
    st.markdown("#### Timeframes")
    cards = []
    for r in mtf["reads"]:
        tone = "up" if r["signal"] == 1 else "down" if r["signal"] == -1 else "flat"
        arrow = {1: "▲", -1: "▼", 0: "▶", None: "·"}[r["signal"]]
        meta = f"{r['bars']:,} bars" + (f" · to {r['last_period']}" if r.get("last_period") else "")
        cards.append(f'<div class="tf"><div class="h"><span>{escape(r["timeframe"])}</span><span class="d">{meta}</span></div>'
                     f'<div class="s {tone}">{arrow} {escape(r["label"])}</div><div class="d">{escape(r["detail"])}</div></div>')
    st.markdown('<div class="tf-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)
    st.caption(f"**{mtf['alignment']}** {mtf['note']}")
