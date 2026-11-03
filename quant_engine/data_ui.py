"""Read-only passport and offline report import controls for the research UI."""
import json

import pandas as pd
import streamlit as st

from .datasets import canonical_bars_bytes, passport_for_analysis
from .nse_files import read_reports, synthetic_reports


@st.cache_data(show_spinner=False)
def cached_reports(files):
    return read_reports(files)


def report_import(files, *, is_synthetic=False):
    if is_synthetic:
        files = [("SYNTHETIC_NSE_FORMAT_REPORTS.zip", synthetic_reports())]
        st.info("SYNTHETIC REPORT WALKTHROUGH · DEMOALPHA, DEMOBETA and the ZZ identifiers are teaching fixtures, not NSE securities or market observations.")
    if not files:
        st.info("Upload NSE CM UDiFF-style daily report CSVs or ZIPs. Multiple completed sessions build one stock's history; the first working target is EQ series. The importer makes no network requests.")
        st.markdown("[Official NSE reports](https://www.nseindia.com/all-reports) · [Format documentation](https://www.nseindia.com/static/resources/forms-formats-members)")
        st.caption("Use files according to your source's permissions. An accessible download does not establish redistribution rights. This adapter is a schema-subset preview; real-file acceptance remains to be completed.")
        st.download_button("Download synthetic report-format example", synthetic_reports(), "SYNTHETIC_NSE_FORMAT_REPORTS.zip", "application/zip")
        st.stop()
    try:
        bundle = cached_reports(tuple(files))
        choices = bundle.instruments()
        labels = {f"{c['symbol']}|{c['series']}": c for c in choices}
        choice = st.selectbox("Instrument from the uploaded reports", list(labels),
                              format_func=lambda key: f"{labels[key]['symbol']} · {labels[key]['series']} · {labels[key]['sessions']} sessions",
                              key="report_instrument")
        selected = labels[choice]
        data = bundle.select(selected["symbol"], selected["series"], is_synthetic=is_synthetic)
    except ValueError as exc:
        st.error(f"Report import could not continue: {exc}")
        st.stop()
    st.caption("Uses trade date (TradDt), not business/settlement date. Ordinary EQ-series records only; other series are not combined. Input headers are not proof of NSE origin.")
    st.caption(f"Selected {selected['symbol']} · {len(data.bars)} observations from {len(bundle.reports)} reports · no price adjustment applied")
    if len(data.bars) < 3:
        st.warning("The import preview is valid, but analysis needs at least three completed sessions. Aim for 60+ sessions for the baseline indicators and strategy.")
        render_passport(data)
        st.stop()
    return data


def render_passport(data):
    passport = passport_for_analysis(data)
    st.markdown("#### Data passport")
    if not data.metadata.get("dataset_id"):
        st.caption("No passport is attached to this legacy in-memory dataset.")
        return
    instrument = passport["instrument"]
    render_quality(passport.get("data_quality"))
    st.write(f"**{instrument['symbol']}** · {instrument['exchange']} · series {instrument['series'] or 'not supplied'} · {instrument['currency']}")
    st.write(f"**Provider/source claim:** {passport['provider_claim']}")
    st.write(f"**Identity:** ISIN {instrument['isin'] or 'not supplied'} · {passport['origin_verification']}")
    st.write(f"**Price basis:** {passport['adjustment_basis']} · {passport['adjustment_verification']}")
    if passport.get("analysis_price_basis"):
        st.write(f"**Analysis price basis:** {passport['analysis_price_basis']}")
        st.caption(f"Research view ID: {passport['research_view_id']}")
    st.write(f"**Dates:** {passport['date_semantics']} ({passport['session_timezone']})")
    st.caption(f"Source dataset: {passport['source_rows']} rows, {passport['source_start']}–{passport['source_end']}. Analysis slice: {passport['analyzed_rows']} rows through {passport['analyzed_through']}.")
    st.caption(passport["calendar_status"])
    st.caption(passport["usage_rights"])
    if passport.get("normalization"):
        with st.expander("How this upload was interpreted"):
            for key, value in passport["normalization"].items():
                st.write(f"**{key.replace('_', ' ').capitalize()}:** {value}")
    coverage = passport.get("coverage", {})
    if coverage.get("report_dates_without_security"):
        st.warning("Selected security is absent from these uploaded report dates: " + ", ".join(coverage["report_dates_without_security"][:20]))
        st.caption("An absent security may be untraded, suspended, newly listed, or missing from a source file; calendar reconciliation is still pending. No bar was fabricated.")
    st.dataframe(pd.DataFrame(passport["source_files"]), hide_index=True, width="stretch")
    with st.expander("For builders · dataset identity and hashes"):
        st.code(json.dumps({"dataset_id": passport["dataset_id"], "source_hash": passport["source_hash"],
                            "source_hash_kind": passport["source_hash_kind"], "normalized_sha256": passport["normalized_sha256"],
                            "analyzed_normalized_sha256": passport["analyzed_normalized_sha256"],
                            "adapter_version": passport["adapter_version"]}, indent=2), language="json")
    st.download_button("Download data passport", json.dumps(passport, indent=2, allow_nan=False), "data-passport.json", "application/json")
    st.download_button("Download analyzed daily data", canonical_bars_bytes(data.bars), "analyzed-daily.csv", "text/csv")


def render_quality(quality):
    if not quality:
        return
    st.markdown("#### Data quality checks")
    st.write(quality["calendar_status"])
    st.write(f"**Freshness:** {quality['freshness']}")
    if quality["latest_ready_session"]:
        st.caption(f"Latest expected completed session: {quality['latest_ready_session']} · lag: {quality['lag_sessions'] if quality['lag_sessions'] is not None else 'unverified'} session(s)")
    issues = []
    labels = {"missing_expected_dates": "Absent expected observations", "unexpected_dates": "Observations on non-session dates",
              "unsupported_dates": "Dates outside calendar coverage", "future_dates": "Future-dated observations", "zero_volume_dates": "Zero-volume observations"}
    for key, label in labels.items():
        if quality[key]:
            issues.append({"Check": label, "Count": len(quality[key]), "Dates (first 20)": ", ".join(quality[key][:20])})
    if issues:
        st.warning("Data quality needs review. These flags do not establish why an observation is absent.")
        st.dataframe(pd.DataFrame(issues), hide_index=True, width="stretch")
    elif quality["calendar_version"]:
        st.success("No absent or unexpected observations found within the checked calendar range.")
    if quality["short_history"]:
        st.caption("Short history: fewer than 60 observations. Longer-window indicators and strategy context may be unavailable.")
    with st.expander("Calendar sources and assessment details"):
        if quality["calendar_version"]:
            st.caption(quality["calendar_version"])
            st.caption(quality["availability_policy"])
            for url in quality["calendar_sources"]:
                st.markdown(f"[NSE {url.rsplit('/', 1)[-1]}]({url})")
        for note in quality["notes"]:
            st.caption(note)
    st.download_button("Download data quality checks", json.dumps(quality, indent=2, allow_nan=False), "data-quality.json", "application/json")
