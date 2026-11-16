import os

# App-level tests run offline against the bundled synthetic series. The live
# default (ticker fetch) is covered with injected provider responses in test_providers.py.
os.environ.setdefault("SIGNAL_LEDGER_DEFAULT_SOURCE", "Demo data")

import pytest


@pytest.fixture(autouse=True)
def _fresh_streamlit_cache():
    """st.cache_data is process-global; isolate tests that fetch through it."""
    import streamlit as st
    st.cache_data.clear()
    yield
