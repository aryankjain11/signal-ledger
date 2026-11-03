"""Learning UI. Read-only project status; no silent changes to completion records."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from quant_engine.models import Settings
from quant_engine.strategy import size_position
from .concepts import CONCEPTS, BY_ID, concept_markdown, find_concepts, handbook_markdown
from .roadmap import TASKS, STAGE_BY_ID, STATUS_LABELS, checklist_markdown


def rsi_from_averages(gain, loss):
    """One teaching step using already-smoothed nonnegative Wilder averages."""
    import math
    if not all(math.isfinite(x) and x >= 0 for x in (gain, loss)):
        raise ValueError("Average gains and losses must be finite and nonnegative.")
    return (50.0 if gain == 0 else 100.0) if loss == 0 else 100 - 100 / (1 + gain / loss)


def render_education(root: Path):
    st.title("Education and Concepts")
    st.write("Learn the idea, work through an example, then inspect how the application uses it.")
    st.caption(f"{len(CONCEPTS)} searchable entries · hypothetical examples · explicit implementation status")
    st.info("Knowing a pattern's name is different from having a detector, a strategy, or evidence that it works. Each entry tells you what is actually implemented.")
    start, library, lab = st.tabs(["Start here", "Concept library", "Learning lab"])
    with start:
        st.subheader("Your learning route")
        route = [
            ("1 · Read price data", "OHLCV, candle body/shadows, sessions, returns and corporate actions."),
            ("2 · Describe structure", "Confirmed swings, HH/HL/LH/LL, support/resistance and confirmation delay."),
            ("3 · Understand indicators", "SMA/EMA first, then RSI and MACD; finally ATR, volume and volatility."),
            ("4 · Recognize geometry", "Doji, engulfing, Evening Star and double patterns; distinguish shape from context."),
            ("5 · Define a strategy", "Exact trigger, next eligible action, expiry, stop, target and no-trade rules."),
            ("6 · Size and simulate", "Risk versus exposure, costs, slippage, gaps, trade ledger and drawdown."),
            ("7 · Evaluate evidence", "Benchmarks, chronological validation, leakage, sample size and overfitting."),
            ("8 · Add models carefully", "Only after reliable labels and data: base rates, calibration and prospective paper results."),
        ]
        for title, description in route:
            with st.expander(title):
                st.write(description)
        st.markdown("**First practical milestone:** explain one candle, calculate an average and true range, then replay a pivot. You do not need to memorize every pattern before building.")
        lesson = (root / "docs" / "lessons" / "01_from_prices_to_evidence.md").read_text(encoding="utf-8")
        with st.expander("Lesson 1 · From prices to evidence"):
            st.markdown(lesson)
        st.download_button("Download Lesson 1", lesson, "lesson-01.md", "text/markdown")
        st.download_button("Download the complete concepts handbook", handbook_markdown(), "education-and-concepts.md", "text/markdown")
        st.caption("Exercises are for you to complete. The project does not automatically mark a lesson as understood.")
    with library:
        query = st.text_input("Search concepts", placeholder="Try RSI, MACD, Evening Star, gap risk…", key="concept_search")
        category = st.selectbox("Concept category", ["All categories"] + sorted({c["category"] for c in CONCEPTS}), key="concept_category")
        scope = st.selectbox("Application coverage", ["All implementation states", "Has current engine behavior"], key="concept_scope")
        matches = find_concepts(query, category, scope)
        st.caption(f"{len(matches)} matching concepts. Compact glossary entries will gain longer lessons when we implement their feature.")
        if not matches:
            st.warning("No matching concepts. Try a shorter name or a different category.")
        else:
            ids = [c["id"] for c in matches]
            chosen = st.selectbox("Choose a concept", ids, index=ids.index("rsi") if "rsi" in ids else 0,
                                  format_func=lambda key: BY_ID[key]["title"], key="chosen_concept")
            concept = BY_ID[chosen]
            st.markdown(concept_markdown(concept, builder_details=False))
            if concept["code"]:
                with st.expander("For builders · connect the concept to the code"):
                    st.code(concept["code"], language="text")
                    st.caption("Read the implementation and its tests after you can explain the worked example.")
    with lab:
        st.subheader("1 · RSI is momentum, not probability")
        st.caption("Inputs below are already-smoothed average gains/losses. This demonstrates one RSI step, not an RSI calculated from an uploaded price history.")
        a, b = st.columns(2)
        gain = a.number_input("Smoothed average gain", min_value=0.0, value=2.0, step=0.1, key="rsi_gain")
        loss = b.number_input("Smoothed average loss", min_value=0.0, value=1.0, step=0.1, key="rsi_loss")
        st.metric("Illustrative RSI", f"{rsi_from_averages(gain, loss):.2f}")
        st.write("Increasing gains relative to losses raises RSI. It does not assign a probability to tomorrow's return.")
        st.subheader("2 · Risk budget versus invested capital")
        a, b = st.columns(2)
        capital = a.number_input("Example capital (INR)", min_value=100.0, value=100_000.0, key="lab_capital")
        risk = b.number_input("Example risk budget (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="lab_risk")
        a, b, c = st.columns(3)
        entry = a.number_input("Assumed entry fill (INR)", min_value=0.01, value=200.0, key="lab_entry")
        stop = b.number_input("Stop trigger (INR)", min_value=0.01, value=195.0, key="lab_stop")
        volume = c.number_input("Previous session volume", min_value=0.0, value=1_000_000.0, key="lab_volume")
        a, b = st.columns(2)
        fee = a.number_input("Example charges per side (bps)", min_value=0.0, max_value=100.0, value=10.0, key="lab_fee")
        slip = b.number_input("Example stop slippage (bps)", min_value=0.0, max_value=100.0, value=5.0, key="lab_slip")
        if stop >= entry:
            st.warning("For this long-position example, the stop must be below the entry.")
        else:
            settings = Settings(capital=capital, risk_fraction=risk / 100, fee_bps=fee, slippage_bps=slip)
            size = size_position(capital, entry, stop, volume, settings)
            c1, c2, c3 = st.columns(3)
            c1.metric("Whole shares", size["quantity"])
            c2.metric("Capital required with entry fee", f"₹{size['cash_required']:,.2f}")
            c3.metric("Planned stop loss with costs", f"₹{size['planned_loss_with_costs']:,.2f}")
            st.caption("The assumed entry is already a fill price. This is the same sizing function used by the engine: cash, risk and a 1% previous-volume cap all apply. Opening gaps and actual execution can create larger losses.")
        st.subheader("3 · Evening Star: a shape needs context")
        st.caption("Entirely synthetic illustration. Evening Star is explained here; the research engine does not yet detect it.")
        labels = ["Context 1", "Context 2", "Context 3", "First body", "Small body", "Third body"]
        figure = go.Figure(go.Candlestick(x=labels, open=[98, 100, 102, 104, 110.5, 110.5],
                                          high=[101, 103, 105, 111, 112, 111], low=[97, 99, 101, 103, 110, 105.5],
                                          close=[100, 102, 104, 110, 111, 106],
                                          increasing_line_color="#36d6a4", decreasing_line_color="#ff6b82"))
        figure.add_hline(y=107, line_dash="dot", annotation_text="First body midpoint = 107")
        figure.update_layout(height=360, xaxis_rangeslider_visible=False, template="plotly_dark",
                             margin=dict(l=10, r=10, t=35, b=10), showlegend=False)
        st.plotly_chart(figure, width="stretch")
        st.write("Observe the prior rise, large bullish body, small body near the top, and bearish penetration below the first body's midpoint. This is one proposed geometry convention, not a confirmed profitable trade.")
        st.subheader("Check your understanding")
        answer = st.radio("What does an RSI reading of 80 mean?", [
            "The current trade has an 80% probability of profit",
            "Recent smoothed gains dominate losses; future direction is still uncertain",
            "The stock must fall in the next session"], index=None, key="rsi_quiz")
        if st.button("Check my answer", key="check_rsi_answer"):
            if answer is None:
                st.info("Choose an answer first.")
            elif answer.startswith("Recent"):
                st.success("Correct. RSI describes recent momentum. A probability needs a defined outcome and validated evidence.")
            else:
                st.warning("Try again: an indicator scale is not a success probability or an inevitable reversal.")


def render_build_journal(root: Path):
    st.title("Build checklist and journal")
    st.write("One small milestone at a time: learn → specify → build → verify → explain → record.")
    done = sum(t["status"] == "done" for t in TASKS)
    partial = sum(t["status"] == "partial" for t in TASKS)
    optional = sum(t["status"] == "optional" for t in TASKS)
    a, b, c, d = st.columns(4)
    a.metric("Tracked work items", len(TASKS))
    b.metric("Done", done)
    c.metric("Partial", partial)
    d.metric("Optional extensions", optional)
    st.caption("Counts are work items, not effort estimates or a percent of project value. Implementation completion is different from learner mastery.")
    stage = st.selectbox("Build stage", list(STAGE_BY_ID), format_func=lambda key: f"{key} · {STAGE_BY_ID[key]['title']}", key="build_stage")
    meta = STAGE_BY_ID[stage]
    st.markdown(f"**Learn:** {meta['learn']}")
    st.markdown(f"**Completion gate:** {meta['gate']}")
    st.caption(f"Original brief coverage: {meta['brief']}")
    rows = [dict(ID=t["id"], Status=STATUS_LABELS[t["status"]], Feature=t["title"]) for t in TASKS if t["stage"] == stage]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.download_button("Download the complete master checklist", checklist_markdown(), "master-checklist.md", "text/markdown")
    st.caption("Statuses are reviewed against evidence in the project files; they are not toggles that silently declare software complete.")
    with st.expander("Chronological work log", expanded=True):
        st.markdown((root / "docs" / "WORK_LOG.md").read_text(encoding="utf-8"))
    with st.expander("Detailed build report"):
        st.markdown((root / "docs" / "BUILD_REPORT.md").read_text(encoding="utf-8"))
    st.download_button("Download work log", (root / "docs" / "WORK_LOG.md").read_text(encoding="utf-8"), "work-log.md", "text/markdown")
