"""Researcher journeys: retained context, explicit file replacement and honest plots."""
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.comparison import synthetic_pair
from quant_engine.event_study_ui import comparison_chart, movement_label
from quant_engine.ui_state import SessionUpload, clamp_dates, upload_signature

ROOT=Path(__file__).resolve().parents[1]


def app():
    return AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()


@pytest.mark.parametrize('old,ranged,expected',[
    (None,False,'2026-01-08'),('2026-01-06',False,'2026-01-05'),('2025-12-01',False,'2026-01-02'),
    (('2026-01-03','2026-01-07'),True,('2026-01-05','2026-01-05')),
    (('2025-01-01','2025-02-01'),True,('2026-01-02','2026-01-08'))])
def test_date_recovery_uses_observed_dates_without_inventing_rows(old,ranged,expected):
    assert clamp_dates(['2026-01-02','2026-01-05','2026-01-08'],old,ranged=ranged)==expected


def test_input_identity_is_order_independent_but_changes_with_bytes_or_filename():
    a=SessionUpload('A.csv',b'a');b=SessionUpload('B.csv',b'b')
    assert upload_signature([a,b])==upload_signature([b,a])
    assert upload_signature(a)!=upload_signature(SessionUpload('A.csv',b'changed'))
    assert upload_signature(a)!=upload_signature(SessionUpload('RENAMED.csv',b'a'))


def test_replay_rules_strategy_tab_and_saved_result_survive_reference_visit():
    a=app()
    a.select_slider(key='research_cutoff').set_value('2024-01-31').run()
    a.number_input(key='research_rvol').set_value(2.5).run()
    a.button(key='explore_outcomes').click().run()
    a.button(key='study_to_retest').click().run()
    a.number_input(key='retest_rule_max_hold').set_value(5).run()
    a.button(key='run_retest').click().run()
    saved=a.session_state['saved_retest_run'].record_json
    a.button(key='reference_retest_strategy').click().run()
    a.selectbox(key='workspace_page').set_value('Research dashboard').run()
    assert not a.exception
    assert a.select_slider(key='research_cutoff').value=='2024-01-31'
    assert a.number_input(key='research_rvol').value==2.5
    assert a.radio(key='strategy_choice').value=='Breakout-retest v1'
    assert a.number_input(key='retest_rule_max_hold').value==5
    assert a.session_state['research_active_tab']=='Backtest lab'
    assert a.session_state['saved_retest_run'].record_json==saved
    assert not any('Saved breakout-retest result is out of date' in w.value for w in a.warning)
    a.button(key='latest_research_bar').click().run()
    assert a.select_slider(key='research_cutoff').value=='2025-04-18'
    assert a.select_slider(key='research_cutoff').proto.set_value
    assert list(a.select_slider(key='research_cutoff').proto.raw_value)==['2025-04-18']
    assert any('Saved breakout-retest result is out of date' in w.value for w in a.warning)


def test_comparison_uploads_confirmation_range_and_window_survive_page_visit(monkeypatch):
    import streamlit as st
    state={'supply':True}
    contents=synthetic_pair()
    def uploader(*args,**kwargs):
        if not state['supply']:return None
        i=0 if kwargs['key'].startswith('compare_upload_A') else 1
        f=BytesIO(contents[i]);f.name=f'stock-{i}.csv';return f
    monkeypatch.setattr(st,'file_uploader',uploader)
    a=app();a.selectbox(key='workspace_page').set_value('Compare two stocks').run()
    a.radio(key='comparison_mode').set_value('Upload two stocks').run()
    a.checkbox(key='compare_complete').check().run()
    a.number_input(key='correlation_window').set_value(10).run()
    a.select_slider(key='comparison_period').set_value(('2026-01-01','2026-01-07')).run()
    a.selectbox(key='workspace_page').set_value('Education and Concepts').run()
    state['supply']=False  # New empty uploader widget; retained bytes must supply the data.
    a.selectbox(key='workspace_page').set_value('Compare two stocks').run()
    assert not a.exception
    assert a.radio(key='comparison_mode').value=='Upload two stocks'
    assert a.checkbox(key='compare_complete').value
    assert a.number_input(key='correlation_window').value==10
    assert a.select_slider(key='comparison_period').value==('2026-01-01','2026-01-07')
    assert any('Retained in this session' in c.value for c in a.caption)
    assert any('Rolling correlation is unavailable' in i.value for i in a.info)
    a.button(key='all_comparison_dates').click().run()
    assert a.select_slider(key='comparison_period').value==('2026-01-01','2026-07-29')
    contents=tuple(pd.read_csv(BytesIO(b)).tail(12).to_csv(index=False).encode() for b in contents)
    state['supply']=True
    a.run()
    assert not a.checkbox(key='compare_complete').value
    a.checkbox(key='compare_complete').check().run()
    dates=pd.read_csv(BytesIO(contents[0])).date.tolist()
    assert not a.exception
    assert a.select_slider(key='comparison_period').value==(dates[0],dates[-1])


def test_replacement_file_requires_new_confirmation_and_clear_does_not_resurrect(monkeypatch):
    import streamlit as st
    raw=(ROOT/'data/synthetic_daily.csv').read_bytes()
    state={'file':SessionUpload('first.csv',raw)}
    monkeypatch.setattr(st,'file_uploader',lambda *args,**kwargs:state['file'])
    a=app();next(r for r in a.radio if r.label=='Data source').set_value('Upload daily data').run()
    a.checkbox(key='research_complete').check().run()
    assert not a.exception and a.checkbox(key='research_complete').value
    state['file']=SessionUpload('replacement.csv',raw)
    a.run()
    assert not a.checkbox(key='research_complete').value
    assert any('Confirm that all' in w.value for w in a.warning)
    state['file']=None
    a.button(key='clear_upload_research_upload').click().run()
    assert 'research_upload' not in a.session_state['session_uploads']
    assert any('Upload one symbol' in i.value for i in a.info)
    a.run()
    assert 'research_upload' not in a.session_state['session_uploads']


def test_study_filters_horizons_and_reference_search_recover_safely():
    a=app();a.button(key='explore_outcomes').click().run()
    a.multiselect(key='study_horizons').set_value([1,5])
    a.number_input(key='study_min_controls').set_value(2)
    a.selectbox(key='study_overlap').set_value('Keep all')
    next(b for b in a.button if b.label=='Run event study').click().run()
    assert not a.exception
    assert a.selectbox(key='study_chart_horizon').value in (1,5)
    one=a.multiselect(key='study_cohorts').value[:1]
    a.multiselect(key='study_cohorts').set_value(one)
    next(b for b in a.button if b.label=='Run event study').click().run()
    a.selectbox(key='workspace_page').set_value('Education and Concepts').run()
    a.text_input(key='concept_search').set_value('no-such-concept-xyz').run()
    a.button(key='clear_concept_filters').click().run()
    assert a.text_input(key='concept_search').value==''
    a.selectbox(key='workspace_page').set_value('After the pattern').run()
    assert not a.exception
    assert a.multiselect(key='study_horizons').value==[1,5]
    assert a.multiselect(key='study_cohorts').value==one
    assert a.number_input(key='study_min_controls').value==2
    assert a.selectbox(key='study_overlap').value=='Keep all'


def test_event_plot_labels_show_direction_horizon_and_actual_matched_sample():
    summary=pd.DataFrame([dict(cohort='breakout | Bullish breakout/retest | Breakout | +1',horizon=5,
        matched_events=3,complete=5,selected=7,matched_event_mean=.04,matched_baseline_mean=.01)])
    fig=comparison_chart(summary,5,'Pattern direction')
    assert fig.layout.xaxis.title.text=='Direction-aligned gross movement (%)'
    assert '5 observations' in fig.layout.title.text
    assert list(fig.data[0].x)==[4.] and list(fig.data[1].x)==[1.]
    assert list(fig.data[0].customdata[0])==[3,5,7]
    assert list(fig.data[1].customdata[0])==[3,5,7]
    assert movement_label('Upward price change')=='Gross upward price change (%)'


def test_retained_action_ledger_keeps_execution_restrictions_on_reference_return(monkeypatch):
    import streamlit as st
    from quant_engine.corporate_actions import synthetic_action_files
    prices,events=synthetic_action_files();state={'supply':True}
    def uploader(*args,**kwargs):
        if not state['supply']:return None
        is_action=kwargs['key'].startswith('action_ledger_file')
        return SessionUpload('actions.csv' if is_action else 'prices.csv',events if is_action else prices)
    monkeypatch.setattr(st,'file_uploader',uploader)
    a=app();next(r for r in a.radio if r.label=='Data source').set_value('Upload daily data').run()
    a.checkbox(key='research_complete').check().run()
    next(s for s in a.selectbox if s.label=='Price adjustment basis').set_value('Unadjusted OHLC').run()
    a.checkbox(key='use_action_ledger').check().run()
    a.radio(key='action_price_view').set_value('Split/bonus adjusted research').run()
    assert a.button(key='run_baseline').disabled
    a.selectbox(key='workspace_page').set_value('Education and Concepts').run()
    state['supply']=False
    a.selectbox(key='workspace_page').set_value('Research dashboard').run()
    assert not a.exception
    assert a.checkbox(key='use_action_ledger').value
    assert a.radio(key='action_price_view').value=='Split/bonus adjusted research'
    assert a.button(key='run_baseline').disabled


def test_retired_picker_clear_is_ignored_but_current_native_removal_forgets_bytes(monkeypatch):
    import streamlit as st
    def empty_picker(*args,**kwargs):
        st.session_state['current_picker_clear']=kwargs['on_change']
        if 'retired_picker_clear' not in st.session_state:
            st.session_state['retired_picker_clear']=kwargs['on_change']
        return None
    monkeypatch.setattr(st,'file_uploader',empty_picker)
    script="""
import streamlit as st
from quant_engine.ui_state import preserve_tab_state,retained_upload,SessionUpload
preserve_tab_state()
page=st.selectbox('Workspace',['Compare','Reference'],key='workspace_page')
st.session_state['research_navigation']=page
st.session_state['comparison_mode']='Upload two stocks'
if 'seeded' not in st.session_state:
    st.session_state['session_uploads']={'compare_upload_A':[SessionUpload('sample.csv',b'demo')]}
    st.session_state['seeded']=True
if page=='Compare':
    retained_upload('Stock A',key='compare_upload_A',type=['csv'])
st.button('Retired picker sent None',on_click=st.session_state.get('retired_picker_clear'))
st.button('Current native removal',on_click=st.session_state.get('current_picker_clear'))
"""
    a=AppTest.from_string(script,default_timeout=30).run()
    a.selectbox(key='workspace_page').set_value('Reference').run()
    next(b for b in a.button if b.label=='Retired picker sent None').click().run()
    assert 'compare_upload_A' in a.session_state['session_uploads']
    a.selectbox(key='workspace_page').set_value('Compare').run()
    next(b for b in a.button if b.label=='Retired picker sent None').click().run()
    assert 'compare_upload_A' in a.session_state['session_uploads']
    next(b for b in a.button if b.label=='Current native removal').click().run()
    assert not a.exception and 'compare_upload_A' not in a.session_state['session_uploads']
