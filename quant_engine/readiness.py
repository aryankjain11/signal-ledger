"""Observable calculation readiness, distinct from verified data quality or trade suitability."""
import pandas as pd


def readiness_rows(analysis):
    frame = analysis.frame
    n = len(frame)
    checks = [("RSI14", "rsi_14", 15), ("ATR14", "atr_14", 14),
        ("EMA20 / SMA20 / Bollinger20", "ema_20", 20), ("EMA50 / SMA50", "ema_50", 50),
        ("SMA200", "sma_200", 200), ("MACD line", "macd", 26),
        ("MACD signal / histogram", "macd_histogram", 34),
        ("Relative volume (prior 20)", "relative_volume", 21), ("ROC10", "roc_10", 11),
        ("Fast stochastic %K14", "stoch_k_14", 14), ("Fast stochastic %D3", "stoch_d_3", 16)]
    rows = []
    for label, column, minimum in checks:
        valid = pd.notna(frame[column].iloc[-1])
        reason = "Available at cutoff" if valid else f"Need {minimum-n} more observations (minimum {minimum})" if n < minimum else "Undefined for this price/volume window; more rows alone may not resolve it"
        rows.append({"Calculation": label, "Status": "Available" if valid else "Unavailable", "What is needed": reason})
    rows.append({"Calculation": "Confirmed price structure", "Status": "Unavailable" if analysis.trend == "Insufficient structure" else "Available",
        "What is needed": analysis.structure})
    rows.append({"Calculation": "Prior-week SMA20", "Status": analysis.weekly["status"],
        "What is needed": f"{analysis.weekly['completed_weeks']} prior calendar weeks; need 20 for weekly SMA20. Latest calendar week excluded." if analysis.weekly["status"] != "Available" else analysis.weekly["context"]})
    inputs = [label for key, label in (("ema_50", "EMA50"), ("atr_14", "ATR14"), ("relative_volume", "Relative volume")) if pd.isna(frame[key].iloc[-1])]
    rows.append({"Calculation": "Fixed breakout baseline context", "Status": "Unavailable" if inputs else "Available",
        "What is needed": "Unavailable inputs: " + ", ".join(inputs) if inputs else "Context calculations available; trigger, sizing and execution checks still apply."})
    return rows


def render_readiness(analysis, data, symbol, adjustment):
    import streamlit as st
    rows = readiness_rows(analysis)
    n = len(analysis.frame)
    missing = [r["Calculation"] for r in rows if r["Status"] != "Available"]
    quality = data.metadata.get("data_quality", {})
    st.write(f"**{symbol}** · {n:,} observations · {analysis.frame.index[0].date()}–{analysis.frame.index[-1].date()} · price basis: **{adjustment}**")
    if missing:
        st.info(f"Partial analysis available: {len(missing)} calculations/context checks unavailable. Open Data readiness below for the reasons.")
    else:
        st.caption("Listed calculations are available. This does not validate the source or identify a trading opportunity.")
    if n < 50:
        st.write(f"EMA50 needs **{50-n} more observations** (50 total). The fixed breakout baseline needs EMA50 plus its price, ATR and volume conditions; available indicators do not guarantee a signal.")
    flags = {key: len(quality.get(key, [])) for key in ("missing_expected_dates", "unexpected_dates", "future_dates", "unsupported_dates", "zero_volume_dates") if quality.get(key)}
    if data.metadata.get("execution_restriction"):
        st.warning(data.metadata["execution_restriction"])
    with st.expander("Data readiness · calculation availability and recovery steps"):
        st.caption("Freshness: " + quality.get("freshness", "Unverified") + ". Calendar: " + quality.get("calendar_status", "Unverified"))
        if quality.get("latest_ready_session"):
            st.caption(f"Latest expected completed session: {quality['latest_ready_session']} · lag: {quality.get('lag_sessions', 'unverified')} session(s). Historical uploads may be intentional.")
        if flags:
            st.warning("Review flags: " + "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in flags.items()) + ". No rows were filled or removed.")
        if adjustment == "Unknown / unverified":
            st.caption("Adjustment declaration is unverified. Review splits/dividends before interpreting long-period price comparisons.")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Counts refer to observed completed bars, not calendar days. Sufficient history is not a guarantee of a qualifying pattern, a trade or reliable source data.")
