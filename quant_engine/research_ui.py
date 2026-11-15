import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .analysis import json_safe
from .models import ResearchRules


def research_controls():
    with st.expander("Analysis rules · breakout and retest"):
        lookback = int(st.number_input("Reference range lookback", 5, 252, 20, key="research_lookback", persist_state="session"))
        volume = st.number_input("Minimum breakout relative volume", 0.0, 10.0, 1.2, .1, key="research_rvol", persist_state="session")
        buffer = st.number_input("Breakout close buffer (prior ATR)", 0.0, .5, .1, .05, key="research_buffer", persist_state="session")
        window = int(st.number_input("Retest expiry (observations after break)", 2, 60, 10, key="research_expiry", persist_state="session"))
        st.caption("Reference level and previous-bar ATR freeze at the break. Retests require a later touch and a close holding the level. Failure takes precedence; expiry is evaluated before a new retest on the deadline bar. These events do not replace the baseline strategy.")
    return ResearchRules(lookback=lookback, min_relative_volume=volume, breakout_buffer_atr=buffer, retest_window=window)


def render_research(analysis):
    st.subheader("Breakout, pattern and momentum analysis")
    st.caption("Observations are versioned geometry/context rules, not validated trade signals or probabilities. Replay changes only the information available through its cutoff.")
    families = [("Breakout / retest", {"breakout"}), ("Chart patterns", {"chart"}),
                ("Candlestick context", {"candle"}), ("Momentum / divergence", {"momentum"})]
    panels = st.tabs([name for name, _ in families])
    for panel, (name, family) in zip(panels, families):
        with panel:
            selected = [e for e in analysis.events if e.get("family") in family or
                        (name == "Chart patterns" and e["name"].startswith("Double")) or
                        (name == "Candlestick context" and "family" not in e and not e["name"].startswith("Double"))]
            if name == "Momentum / divergence":
                st.dataframe(pd.DataFrame(analysis.momentum["facts"]), hide_index=True, width="stretch")
                for text in analysis.momentum["interpretation"]:
                    st.write(text)
                fig = go.Figure()
                for key, label in (("macd", "MACD"), ("macd_signal", "Signal"), ("macd_histogram", "Histogram")):
                    fig.add_scatter(x=analysis.frame.index, y=analysis.frame[key], name=label)
                fig.update_layout(template="plotly_dark", height=300, title="MACD line, signal and histogram")
                st.plotly_chart(fig, width="stretch")
                st.caption("Divergences require two confirmed price pivots; the second pivot's confirmation delay is preserved. No current RSI value is substituted for historical pivot RSI.")
            if name == "Chart patterns":
                st.caption("Supported: double top/bottom, rectangle, ascending/descending/symmetrical triangles. Six alternating confirmed anchors and frozen fitted boundaries define the new families. Other named patterns remain planned.")
            if name == "Candlestick context":
                st.caption("Added: Hammer, Hanging man, Inverted hammer, Shooting star, Morning Star and Evening Star. New observations require a preceding trend; star variants do not require a gap. Existing doji/engulfing observations remain geometry-only.")
            if not selected:
                st.info("No supported observations in this slice. More history or different market structure may be needed.")
                continue
            latest = {}
            for event in sorted(selected, key=lambda e: (e["detected_at"], e["index"])):
                latest[event["id"]] = event
            st.markdown("**Latest state of each formation**")
            st.dataframe(pd.DataFrame([{k: e.get(k) for k in ("name", "status", "formed_at", "detected_at", "level", "evidence")} for e in sorted(latest.values(), key=lambda e: e["detected_at"], reverse=True)[:50]]), hide_index=True, width="stretch")
            with st.expander("State transitions and detection evidence"):
                printable = [{key: json.dumps(json_safe(value), ensure_ascii=False) if isinstance(value, (list, dict)) else value
                              for key, value in event.items()} for event in selected]
                st.dataframe(pd.DataFrame(printable), hide_index=True, width="stretch")
    with st.expander("Exact research rules and scope"):
        st.json(analysis.rules)
        st.caption("Triangle/rectangle fits use three highs and three lows, 10–120-bar anchor span, <=0.5 ATR fitting error and frozen boundaries; break buffer 0.1 ATR and 40-observation expiry. Star/single-candle definitions and divergence thresholds are in the feature specification. None estimates historical success rates yet.")
    st.download_button("Download analytical events", json.dumps(json_safe({"rules": analysis.rules, "events": analysis.events, "momentum": analysis.momentum}), indent=2, allow_nan=False), "analytical-events.json", "application/json")
