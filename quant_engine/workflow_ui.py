"""Same-session task navigation and contextual reference links."""
import streamlit as st

PAGES = {"Research dashboard": "research", "After the pattern": "events", "Compare two stocks": "compare", "Education and Concepts": "education", "Build checklist & log": "build"}


def navigate(workspace, concept=None, research_tab=None):
    st.session_state["workspace_page"] = workspace
    if research_tab:
        st.session_state["requested_research_tab"] = research_tab
    if concept:
        st.session_state["concept_search"] = ""
        st.session_state["concept_category"] = "All categories"
        st.session_state["concept_scope"] = "All implementation states"
        st.session_state["chosen_concept"] = concept
        st.session_state["reference_requested"] = True


def render_navigation(workspace):
    def changed():
        if st.session_state.get("research_navigation"):
            navigate(st.session_state["research_navigation"])
    st.session_state["research_navigation"] = workspace
    st.pills("Research steps", list(PAGES), key="research_navigation", on_change=changed,
        help="Inspect data and observations, study historical outcomes, compare stocks, or open a reference. Your completed backtest remains in this browser session.", wrap=True)


def render_reference_links():
    with st.expander("Understand this result · quick references"):
        for col, (label, key) in zip(st.columns(5), [("RSI", "rsi"), ("ATR", "atr"), ("Relative volume", "rvol"), ("Pivot delay", "pivot"), ("Historical outcomes", "forward-outcomes")]):
            col.button(label, key=f"reference_{key}", on_click=navigate, args=("Education and Concepts", key))
        st.caption("A detected shape is an observation. A strategy adds exact entry/exit rules. Historical outcomes describe a sample; they are not forecasts.")
