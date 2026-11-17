"""Same-session task navigation and contextual reference links."""
import streamlit as st

# Display label -> URL query value. "build" (developer checklist) is reachable only via ?page=build.
PAGES = {"Analyze": "research", "Scanner": "scanner", "Pattern research": "events", "Strategy backtest": "backtest", "Paper trades": "paper", "Compare stocks": "compare", "Learn": "education"}
PAGE_ICONS = {"Analyze": ":material/candlestick_chart:", "Scanner": ":material/radar:", "Pattern research": ":material/science:", "Strategy backtest": ":material/query_stats:", "Paper trades": ":material/bookmark:",
              "Compare stocks": ":material/compare_arrows:", "Learn": ":material/menu_book:"}


def navigate(workspace, concept=None, research_tab=None, strategy=None):
    st.session_state["workspace_page"] = workspace
    if research_tab:
        st.session_state["requested_research_tab"] = research_tab
    if strategy:
        st.session_state["strategy_choice"] = strategy
    if concept:
        st.session_state["concept_search"] = ""
        st.session_state["concept_category"] = "All categories"
        st.session_state["concept_scope"] = "All implementation states"
        st.session_state["chosen_concept"] = concept
        st.session_state["reference_requested"] = True


def render_reference_links():
    st.caption("Look up a term")
    for col, (label, key) in zip(st.columns(5), [("RSI", "rsi"), ("ATR", "atr"), ("Relative volume", "rvol"), ("Pivot delay", "pivot"), ("Historical outcomes", "forward-outcomes")]):
        col.button(label, key=f"reference_{key}", on_click=navigate, args=("Learn", key), width="stretch")
