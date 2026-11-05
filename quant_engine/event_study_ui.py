"""Pattern outcome research, auditable cohorts and original plain-language reference notes."""
from dataclasses import asdict
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .analysis import json_safe
from .datasets import passport_for_analysis
from .event_study import (StudyRules, TREND_LABELS, VOLUME_LABELS, build_study,
                          occurrence_ledger, study_record)


@st.cache_data(show_spinner=False)
def _cached_study(frame, events, rule_values, metadata):
    return build_study(frame, events, StudyRules(**rule_values), metadata)


def cohort_label(cohort):
    family, name, state, direction = cohort.split(" | ")
    return f"{name} · {state} · {'upward' if direction == '+1' else 'downward' if direction == '-1' else 'neutral'}"


def summary_display(summary):
    table = summary.copy()
    table["cohort"] = table.cohort.map(cohort_label)
    for key in ("mean_return", "median_return", "q25_return", "q75_return", "positive_fraction",
                "median_mfe", "median_mae", "matched_event_mean", "matched_baseline_mean", "difference_from_baseline"):
        table[key] *= 100
    return table.rename(columns={"cohort": "Event type", "horizon": "Observations ahead",
        "selected": "Selected", "complete": "Complete", "incomplete": "Incomplete",
        "action_excluded": "Raw-action exclusions", "mean_return": "Mean movement (%)",
        "median_return": "Median movement (%)", "q25_return": "25th percentile (%)", "q75_return": "75th percentile (%)",
        "positive_fraction": "Positive outcomes (%)", "zero_count": "Flat outcomes",
        "median_mfe": "Median MFE (%)", "median_mae": "Median signed MAE (%)",
        "matched_events": "Events with baseline", "matched_event_mean": "Matched event mean (%)",
        "matched_baseline_mean": "Matched baseline mean (%)", "difference_from_baseline": "Difference (percentage points)",
        "sample_note": "Sample note"})


def event_detail_chart(frame, occurrence, outcome, horizon):
    i = int(occurrence["index"])
    visible = frame.iloc[max(0, i - 35):min(len(frame), i + horizon + 4)]
    fig = go.Figure(go.Candlestick(x=visible.index, open=visible.open, high=visible.high,
        low=visible.low, close=visible.close, increasing_line_color="#36d6a4", decreasing_line_color="#ff6b82", name="Observed OHLC"))
    known = occurrence["known_at"]
    fig.add_shape(type="line", x0=known, x1=known, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#f6c86a", dash="dot"))
    fig.add_annotation(x=known, y=1.02, xref="x", yref="paper", text="Knowable at close", showarrow=False)
    if pd.notna(outcome.get("reference_price")):
        fig.add_trace(go.Scatter(x=[outcome["reference_date"]], y=[outcome["reference_price"]],
            mode="markers", marker=dict(size=11, color="#6ca6ff", symbol="diamond"), name="Measurement reference"))
        fig.add_hline(y=outcome["reference_price"], line_color="#6ca6ff", line_dash="dot")
    if outcome.get("outcome_state") == "Complete":
        end = outcome["exit_date"]
        fig.add_trace(go.Scatter(x=[end], y=[frame.loc[end, "close"]], mode="markers",
            marker=dict(size=11, color="#ffffff", symbol="x"), name=f"{horizon}-observation close"))
    fig.update_layout(template="plotly_dark", height=480, xaxis_rangeslider_visible=False,
        paper_bgcolor="#101a2b", plot_bgcolor="#101a2b", margin=dict(l=12, r=12, t=50, b=10),
        legend=dict(orientation="h", y=-.12))
    return fig


def render_event_study(analysis, data, settings, symbol, adjustment):
    frame = analysis.frame
    st.subheader("Historical outcome research")
    st.write("Measure what followed each setup, compare it with similar non-event dates, and inspect the underlying observations.")
    st.caption(f"{symbol} · {len(frame):,} observed bars · through {frame.index[-1].date()} · {adjustment}")
    st.info("Gross historical price outcomes. No portfolio returns, trading fills, calibrated probabilities or statistical-significance claims are produced by this study.")
    ledger = occurrence_ledger(frame, analysis.events)
    available = ledger.loc[ledger.eligible]
    if available.empty:
        st.info("No supported event occurrences are available in this replay. Add history or change the detection rules above.")
        return
    cohorts = sorted(available.cohort.unique())
    preferred = available.loc[available.state.isin(["Breakout", "Breakdown", "Retest held"])
        | available.name.isin(["Morning Star", "Evening Star"]), "cohort"].unique().tolist()
    defaults = sorted(preferred) or [c for c in cohorts if not c.endswith("+0")][:5] or cohorts[:5]
    dates = frame.index.strftime("%Y-%m-%d").tolist()
    previous = st.session_state.get("study_available_cohorts")
    if previous is not None and previous != cohorts:
        old = st.session_state.get("study_cohorts", [])
        retained = [c for c in old if c in cohorts]
        if old and not retained:
            st.session_state["study_cohorts"] = defaults
            st.caption("The available event types changed with the data/replay. Selection was reset to available types.")
        elif retained != old:
            st.session_state["study_cohorts"] = retained
    st.session_state["study_available_cohorts"] = cohorts
    previous_period = st.session_state.get("study_period")
    if previous_period:
        remaining = [date for date in dates if previous_period[0] <= date <= previous_period[1]]
        st.session_state["study_period"] = (remaining[0], remaining[-1]) if remaining else (dates[0], dates[-1])
    with st.form("event_study_form"):
        st.markdown("**Study definition**")
        selected = st.multiselect("Event types to study", cohorts, default=defaults,
            format_func=cohort_label, key="study_cohorts")
        left, right = st.columns(2)
        reference = left.selectbox("Measurement reference", ["Next observed open", "Detection close"], key="study_reference",
            help="Next open excludes the overnight move from the knowledge close. Detection close is an observational reference, not an assumed available fill.")
        perspective = right.selectbox("Outcome perspective", ["Pattern direction", "Upward price change"], key="study_perspective",
            help="Pattern direction makes falls positive for bearish observations. Neutral patterns can be studied using upward price change.")
        horizons = left.multiselect("Horizons (observations after detection)", [1, 2, 3, 5, 10, 20, 40, 60], default=[1, 5, 10, 20], key="study_horizons")
        overlap = right.selectbox("Overlapping observations", ["Thin within cohort", "Keep all"], key="study_overlap",
            help="Thinning keeps the earliest occurrence, then requires spacing greater than the largest selected horizon. Other event types can still overlap.")
        trend = left.selectbox("Trend at detection", ["All", *TREND_LABELS], key="study_trend")
        volume = right.selectbox("Relative volume at detection", ["All", *VOLUME_LABELS], key="study_volume")
        controls = left.number_input("Minimum matching baseline observations", 1, 100, 5, key="study_min_controls")
        period = st.select_slider("Event date range (outcomes may extend beyond this interval)", options=dates,
            value=(dates[0], dates[-1]), key="study_period")
        st.caption("Horizons count uploaded observations, not calendar days. Replay above limits all available outcomes. Settings apply when you run the study.")
        st.form_submit_button("Run event study", type="primary")
    if not selected or not horizons:
        st.warning("Choose at least one event type and one horizon.")
        return
    # A changed file or replay can retire Streamlit's formerly selected options.
    selected = [c for c in selected if c in cohorts]
    if not selected:
        st.info("Select event types available in the current replay.")
        return
    rules = StudyRules(horizons=tuple(sorted(horizons)), reference=reference, perspective=perspective,
        overlap=overlap, cohorts=tuple(sorted(selected)), trend=trend, volume=volume,
        start=period[0], end=period[1], min_controls=int(controls))
    metadata = {"source_sha256": data.source_hash, "dataset_id": data.metadata.get("dataset_id"),
        "research_view_id": data.metadata.get("research_view_id"), "symbol": symbol,
        "price_basis": adjustment, "corporate_actions": data.metadata.get("corporate_actions", {}),
        "research_rules": analysis.rules, "pivot_window": settings.pivot_window}
    with st.spinner("Measuring historical outcomes and matching baseline conditions…"):
        try:
            result = _cached_study(frame, analysis.events, asdict(rules), metadata)
        except ValueError as exc:
            st.error(f"Study could not run: {exc}")
            return
    st.caption(f"Study record {result.run_id[:16]} · fixed largest horizon {max(horizons)} · all measurements use only this replay's bars.")
    selected_rows = result.occurrences.loc[result.occurrences.selection.eq("Included")]
    if result.outcomes.empty:
        st.info("No occurrences remain under this definition. Neutral events need Upward price change; other filters may also remove observations.")
    counts = result.audit["selection_counts"]
    a, b, c, d = st.columns(4)
    a.metric("Included occurrences", len(selected_rows))
    b.metric("Overlap exclusions", counts.get("Overlapping within cohort", 0))
    c.metric("Event types represented", selected_rows.cohort.nunique())
    longest = result.summary.loc[result.summary.horizon.eq(max(horizons))]
    d.metric(f"Complete at {max(horizons)} observations", int(longest.complete.sum()))
    summary_tab, distribution_tab, detail_tab, audit_tab = st.tabs([
        "Outcome comparison", "Distribution & excursions", "Inspect an occurrence", "Audit & exports"])
    with summary_tab:
        st.caption("Each row is a separate event type/state and horizon. Positive outcomes are observed frequencies, not trade win rates or future probabilities. Returns and excursions below are percentages.")
        st.dataframe(summary_display(result.summary), hide_index=True, width="stretch")
        if not result.summary.empty:
            h = st.selectbox("Comparison horizon", sorted(horizons), index=len(horizons)-1, key="study_chart_horizon")
            s = result.summary.loc[result.summary.horizon.eq(h)]
            labels = [cohort_label(c).replace(" · ", "<br>", 1) for c in s.cohort]
            fig = go.Figure()
            fig.add_bar(y=labels, x=s.matched_event_mean * 100, orientation="h", name="Events with baseline", marker_color="#36d6a4", customdata=s.matched_events,
                hovertemplate="%{y}<br>Mean %{x:.2f}%<br>Matched events %{customdata}<extra></extra>")
            fig.add_bar(y=labels, x=s.matched_baseline_mean * 100, orientation="h", name="Matched non-event baseline", marker_color="#6ca6ff")
            fig.update_layout(template="plotly_dark", height=max(400, 90 * len(s)), barmode="group", xaxis_title="Mean gross price movement (%)",
                legend=dict(orientation="h", y=1.12), margin=dict(t=70, b=45), yaxis=dict(autorange="reversed", automargin=True))
            st.plotly_chart(fig, width="stretch", key="event_study_comparison")
        st.write("Baseline: non-event dates in this stock and event-date range, matched to each occurrence's EMA50 and relative-volume bucket. Both bars use the same events with sufficient controls. Controls can be reused and their outcome windows can overlap other pools or events.")
        st.caption("A missing baseline stays unavailable. The baseline uses the whole selected historical interval and is retrospective; it is not an earlier-only live forecast or a market/sector-adjusted return model.")
    with distribution_tab:
        if not result.outcomes.empty:
            h = st.selectbox("Distribution horizon", sorted(horizons), index=len(horizons)-1, key="study_distribution_horizon")
            complete = result.outcomes.loc[result.outcomes.horizon.eq(h) & result.outcomes.outcome_state.eq("Complete")]
            fig = go.Figure()
            for cohort, group in complete.groupby("cohort", sort=True):
                fig.add_trace(go.Box(y=group.forward_return * 100, name=cohort_label(cohort), boxpoints="all", jitter=.25, pointpos=0))
            fig.update_layout(template="plotly_dark", height=470, yaxis_title="Gross price movement (%)", showlegend=False)
            st.plotly_chart(fig, width="stretch", key="event_study_distribution")
            st.dataframe(summary_display(result.summary.loc[result.summary.horizon.eq(h)])[["Event type", "Complete", "Median MFE (%)", "Median signed MAE (%)", "Sample note"]], hide_index=True, width="stretch")
        st.write("MFE is the largest favourable high/low excursion from the reference, floored at zero. Signed MAE is the worst adverse excursion, capped at zero. The detection candle is excluded. Daily bars cannot tell which extreme happened first or whether an order could fill there.")
        st.caption("Box plots and quartiles describe observed dispersion. They are not confidence bands. Spacing observations reduces window reuse without establishing statistical independence; inferential tests and dependent-data uncertainty estimates remain pending.")
    with detail_tab:
        if not selected_rows.empty:
            keys = selected_rows.event_key.tolist()
            lookup = selected_rows.set_index("event_key")
            key = st.selectbox("Occurrence", keys,
                format_func=lambda k: f"{lookup.loc[k, 'known_at']} · {cohort_label(lookup.loc[k, 'cohort'])}", key="study_occurrence")
            h = st.selectbox("Occurrence horizon", sorted(horizons), key="study_occurrence_horizon")
            occurrence = lookup.loc[key].to_dict()
            outcome = result.outcomes.loc[result.outcomes.event_key.eq(key) & result.outcomes.horizon.eq(h)].iloc[0].to_dict()
            st.write(f"Formed {occurrence['formed_at']} · knowable {occurrence['known_at']} · {outcome['outcome_state']}.")
            st.caption(f"Context at knowledge close: {occurrence['trend_context']} · {occurrence['volume_context']}. No final-state or eventual-success filter was used.")
            a, b, c, d = st.columns(4)
            complete = outcome["outcome_state"] == "Complete"
            a.metric("Forward movement", f"{outcome['forward_return']:.2%}" if complete else "Unavailable")
            b.metric("Favourable excursion", f"{outcome['mfe']:.2%}" if complete else "Unavailable")
            c.metric("Adverse excursion (signed)", f"{outcome['mae']:.2%}" if complete else "Unavailable")
            d.metric("Matching baseline observations", int(outcome["control_count"]))
            st.plotly_chart(event_detail_chart(frame, occurrence, outcome, h), width="stretch", key="event_study_occurrence_chart")
            values = {k: outcome.get(k) for k in ("reference_date", "reference_price", "exit_date", "calendar_days", "forward_return", "mfe", "mae", "control_count", "control_mean")}
            with st.expander("Exact numeric record"):
                st.json(json_safe(values))
                st.caption("Detailed JSON uses fractional movements: 0.04 means 4%. Incomplete and excluded movements are null.")
            source = next(e for e in analysis.events if e["id"] == occurrence["formation_id"] and e["status"] == occurrence["state"] and e["detected_at"] == occurrence["known_at"])
            with st.expander("Detection evidence and geometry"):
                st.json(json_safe(source))
    with audit_tab:
        st.dataframe(result.occurrences[["name", "state", "formed_at", "known_at", "trend_context", "volume_context", "selection"]], hide_index=True, width="stretch")
        with st.expander("Measurement rules and limitations", expanded=True):
            st.json(json_safe({"rules": result.rules, "audit": result.audit}))
        provenance = {**metadata, "source_passport": passport_for_analysis(data) if data.metadata.get("dataset_id") else None,
            "data_quality": data.metadata.get("data_quality"), "source_events": analysis.events}
        record = study_record(result, provenance)
        st.download_button("Download complete study record", json.dumps(record, indent=2, allow_nan=False),
            "pattern-outcome-study.json", "application/json", key="study_record_download")
        st.download_button("Download occurrence outcomes CSV", result.outcomes.to_csv(index=False), "occurrence-outcomes.csv", "text/csv")
        st.download_button("Download baseline observations CSV", result.controls.to_csv(index=False), "baseline-observations.csv", "text/csv")
        st.download_button("Download summary CSV", result.summary.to_csv(index=False), "outcome-summary.csv", "text/csv")
        st.caption("Exports retain fractions, exact configuration, event ledger, source/visible-data hashes and baseline observations. Files are saved on demand; a database and saved-study history remain planned.")
    with st.expander("Concepts used on this page"):
        st.markdown("**Forward return:** end close divided by the stated reference minus one. A 1-observation next-open study measures the next bar's open-to-close movement.\n\n**Direction:** bearish alignment negates the price change; it does not simulate an executable short trade. Neutral shapes require upward-price mode.\n\n**Censoring:** a horizon beyond replay is unknown and excluded from averages, rather than counted as a loss.\n\n**Sample mean versus expectancy:** the average of this selected gross historical sample is not after-cost expected trading profit.\n\n**Baseline coverage:** the difference uses only complete events with enough matching controls; its event mean can differ from the full-cohort mean.\n\n**Research bias:** changing filters after seeing outcomes is exploratory selection. Save the definition, then evaluate it on unseen history before claiming predictive evidence. See Education and Concepts for worked definitions.")
