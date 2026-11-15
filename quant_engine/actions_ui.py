"""Optional action-ledger controls. Source prices remain intact in memory."""
import json

import pandas as pd
import streamlit as st

from .corporate_actions import read_action_ledger, synthetic_action_files
from .ui_state import retained_upload


def action_controls(data):
    with st.expander("Corporate actions · splits and bonus issues"):
        st.caption("Keep your NSE price download unchanged. A separate reviewed action ledger can normalize splits/bonus issues; no event is inferred from a price jump.")
        enabled = st.checkbox("Use a corporate-action ledger", key="use_action_ledger", persist_state="session")
        if not enabled:
            return None, False
        st.caption("CSV fields: action_id, symbol, ex_date, known_on, action_type, shares_before, shares_after, source. For a 1:1 bonus use 1 share before and 2 total shares after. Dates: YYYY-MM-DD.")
        bars, ledger = synthetic_action_files()
        st.download_button("Download synthetic action-ledger example", ledger, "synthetic-actions.csv", "text/csv")
        st.download_button("Download matching synthetic price example", bars, "synthetic-action-prices.csv", "text/csv")
        st.caption("Both examples are invented fixtures, not market data. Review actual events against your source before using them.")
        uploaded = retained_upload("Split/bonus action ledger", type=["csv"], key="action_ledger_file")
        mode = st.radio("Price view", ["Original prices", "Split/bonus adjusted research"], key="action_price_view", persist_state="session")
        if uploaded is None:
            st.info("Upload the separate action ledger to continue, or turn off Use a corporate-action ledger.")
            st.stop()
        try:
            parsed = read_action_ledger(uploaded.getvalue())
        except ValueError as exc:
            st.error(f"Action ledger could not be used: {exc}")
            st.stop()
        if mode == "Split/bonus adjusted research" and data.metadata.get("adjustment_basis") not in {"Unadjusted OHLC", "Synthetic example"}:
            st.warning("Select Unadjusted OHLC as the original Price adjustment basis before enabling adjusted research. Already-adjusted/unknown inputs cannot be adjusted again.")
            st.stop()
        return parsed, mode == "Split/bonus adjusted research"


def render_action_audit(data, raw_csv, factors):
    audit = data.metadata.get("corporate_actions")
    if not audit:
        return
    with st.expander("Corporate-action audit and original data", expanded=True):
        st.write(f"**Analysis view:** {audit['mode']} · cutoff {audit['cutoff']} · {audit['applied_events']} applied event(s)")
        st.caption("Original-source price basis and hash remain in the passport. This view has a separate research ID and analyzed-data hash.")
        st.caption(audit["scope"])
        if audit["known_events"]:
            st.dataframe(pd.DataFrame(audit["known_events"]), hide_index=True, width="stretch")
        else:
            st.caption("No matching events were knowable by this replay cutoff. No event details from later declarations are used.")
        st.download_button("Download corporate-action audit", json.dumps(audit, indent=2, allow_nan=False), "corporate-action-audit.json", "application/json")
        st.download_button("Download original visible prices", raw_csv, "original-visible-prices.csv", "text/csv")
        st.download_button("Download adjustment factors", factors.to_csv(date_format="%Y-%m-%d"), "adjustment-factors.csv", "text/csv")
