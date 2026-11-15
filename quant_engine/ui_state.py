"""Session-only continuity and safe recovery for research controls and local uploads."""
from dataclasses import dataclass
from hashlib import sha256
import json

import streamlit as st


@dataclass(frozen=True)
class SessionUpload:
    name: str
    content: bytes

    def getvalue(self):
        return self.content


def upload_signature(files):
    if not files:
        return "empty"
    if not isinstance(files, (list, tuple)):
        files = [files]
    values = sorted((f.name, sha256(f.getvalue()).hexdigest()) for f in files)
    return sha256(json.dumps(values).encode()).hexdigest()


def retained_upload(label, *, key, type, accept_multiple_files=False, **kwargs):
    """Keep bytes outside ephemeral file-widget state; clearing never resurrects them."""
    memory = st.session_state.setdefault("session_uploads", {})
    generations = st.session_state.setdefault("upload_generations", {})
    seen = st.session_state.setdefault("upload_render_contexts", {})
    epoch = st.session_state.get("ui_epoch", 0)
    workspace = st.session_state.get("workspace_page")
    last = seen.get(key)
    if last and (last['epoch'] < epoch - 1 or last['workspace'] != workspace):
        # A recreated picker must not reuse expired frontend file IDs.
        generations[key] = generations.get(key, 0) + 1
    generation = generations.get(key, 0)
    widget_key = key if generation == 0 else f"{key}_generation_{generation}"

    def capture():
        if generation != generations.get(key, 0):
            return  # A delayed clear from a retired picker is not a user removal.
        current = st.session_state.get(widget_key)
        if not current:
            last_seen=seen.get(key,{})
            same_page=(st.session_state.get('workspace_page')==workspace and
                st.session_state.get('research_navigation',workspace)==workspace)
            active_source=(key!='research_upload' or st.session_state.get('data_source')=='Upload daily data')
            active_source=active_source and (key!='nse_reports' or st.session_state.get('data_source')=='Import NSE daily reports')
            active_source=active_source and (not key.startswith('compare_upload_') or st.session_state.get('comparison_mode')=='Upload two stocks')
            active_source=active_source and (key!='action_ledger_file' or st.session_state.get('use_action_ledger'))
            if same_page and active_source and last_seen.get('epoch')==st.session_state.get('ui_epoch',0):
                memory.pop(key, None)
        else:
            values = current if isinstance(current, list) else [current]
            memory[key] = [SessionUpload(f.name, f.getvalue()) for f in values]

    uploaded = st.file_uploader(label, type=type, key=widget_key,
        accept_multiple_files=accept_multiple_files, on_change=capture, **kwargs)
    seen[key]={'epoch':epoch,'workspace':workspace}
    if uploaded:
        values = uploaded if isinstance(uploaded, list) else [uploaded]
        memory[key] = [SessionUpload(f.name, f.getvalue()) for f in values]
    retained = memory.get(key, [])
    if retained and not uploaded:
        st.caption("Retained in this session: " + ", ".join(f.name for f in retained))
    if retained:
        def clear():
            memory.pop(key, None)
            generations[key] = generation + 1
        st.button("Clear " + label, key="clear_upload_" + key, on_click=clear,
            help="Forget this session's copy and choose a different file. Your original file is unchanged.")
    return retained if accept_multiple_files else retained[0] if retained else None


def completed_confirmation(label, files, *, key):
    signature = upload_signature(files)
    identities = st.session_state.setdefault("confirmation_sources", {})
    if identities.get(key) != signature:
        st.session_state[key] = False
        identities[key] = signature
    return st.checkbox(label, key=key, persist_state="session",
        help="This declaration belongs to these exact input files. Replacing a file requires confirmation again.")


def valid_selection(key, options, default=None, multiple=False):
    """Remove retired options before keyed widgets/formatters can use them."""
    if multiple:
        if key in st.session_state:
            st.session_state[key] = [v for v in st.session_state[key] if v in options]
    elif key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = default if default in options else options[0] if options else None


def clamp_dates(options, value, *, ranged=False):
    """ISO session dates; preserve overlap, otherwise recover to available history."""
    if not options:
        raise ValueError("Date controls need observed dates.")
    if ranged:
        if not value or len(value) != 2:
            return (options[0], options[-1])
        covered = [d for d in options if value[0] <= d <= value[1]]
        return (covered[0], covered[-1]) if covered else (options[0], options[-1])
    if value in options:
        return value
    if value:
        before = [d for d in options if d <= value]
        return before[-1] if before else options[0]
    return options[-1]


def date_control(label, options, *, key, context, ranged=False):
    """Remember dates per dataset/pair; never pass retired dates to a slider."""
    memory = st.session_state.setdefault("date_contexts", {})
    previous = st.session_state.setdefault("date_control_context", {})
    old_context = previous.get(key)
    if old_context != context:
        if old_context is not None and key in st.session_state:
            memory[(key, old_context)] = st.session_state[key]
        value = memory.get((key, context))
    else:
        value = st.session_state.get(key, memory.get((key, context)))
    resets = st.session_state.setdefault("next_date_values", {})
    value = resets.pop(key, value)
    restored = clamp_dates(options, value, ranged=ranged)
    if key in st.session_state and st.session_state[key] != restored:
        # A default alone does not update an already mounted frontend control.
        # Write the value so Streamlit sends its explicit set_value instruction.
        st.session_state[key] = restored
    previous[key] = context
    # Explicit value establishes single/range mode; Session State alone does not.
    selected = st.select_slider(label, options=options, value=restored, key=key, persist_state="session")
    memory[(key, context)] = selected
    return selected


def reset_dates(key, options):
    st.session_state.setdefault("next_date_values", {})[key] = (options[0], options[-1]) if isinstance(st.session_state.get(key), (tuple, list)) else options[-1]


def workspace_tabs(names, *, key, requested=None):
    # Tabs have no persist_state parameter in the pinned runtime.
    if requested in names:
        st.session_state[key] = requested
    valid_selection(key, names, names[0])
    return st.tabs(names, key=key, on_change="rerun")


def preserve_tab_state():
    st.session_state['ui_epoch']=st.session_state.get('ui_epoch',0)+1
    for key in ("research_active_tab", "comparison_active_tab", "study_active_tab", "education_active_tab"):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
