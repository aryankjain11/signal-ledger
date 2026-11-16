from copy import deepcopy
from dataclasses import asdict, replace
from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze
from quant_engine.corporate_actions import synthetic_action_files
from quant_engine.data import load_bars
from quant_engine.models import Settings
from quant_engine.retest_records import retest_identity, save_retest
from quant_engine.retest_strategy import RetestRules
from quant_engine.retest_ui import setup_chart

ROOT=Path(__file__).resolve().parents[1]


def sample():
    d=load_bars((ROOT/'data/synthetic_daily.csv').read_bytes(),'synthetic.csv')
    return d,analyze(d,Settings())


@pytest.mark.parametrize('name',list(asdict(RetestRules())))
def test_identity_captures_each_strategy_rule(name):
    d,a=sample();rules=RetestRules()
    value=getattr(rules,name)
    changed=replace(rules,**{name:value+1 if type(value) is int else value+.1})
    assert retest_identity(a,d,Settings(),rules,'DEMO','Synthetic') != retest_identity(a,d,Settings(),changed,'DEMO','Synthetic')


def test_record_is_strict_immutable_and_inspection_uses_saved_prices_only():
    d,a=sample();saved=save_retest(a,d,Settings(),RetestRules(),'DEMO','Synthetic')
    r=json.loads(saved.record_json)
    assert r['strategy_version']=='long-breakout-retest/1' and len(r['bars'])==600
    assert r['metrics']['trades']==4 and len(r['candidates'])==5
    chart=setup_chart(r,r['candidates'][0]['setup_id'])
    assert len(chart.data[0].close) < 40  # Cancelled view ends near its decision, not years later.
    assert chart.data[1].x[0] == r['candidates'][0]['breakout_date']
    filled=next(t for t in r['trades'] if t['entry_date']==t['exit_date'])
    target=next(t for t in setup_chart(r,filled['setup_id']).data if t.name=='Target fixed at entry')
    assert 'markers' in target.mode and target.y[0]==filled['target']  # Visible even for a same-date exit.
    original=list(chart.data[0].close)
    a.frame.loc[:,'close']=1.
    d.source_hash='changed'
    assert list(setup_chart(json.loads(saved.record_json),r['candidates'][0]['setup_id']).data[0].close)==original
    assert retest_identity(a,d,Settings(),RetestRules(),'DEMO','Synthetic') != saved.request_id
    assert r['execution']['fee_bps']==10.
    assert all(t['entry_index']>t['retest_index']>t['breakout_index'] for t in r['trades'])
    json.dumps(r,allow_nan=False)


def test_identity_tracks_replay_basis_costs_policy_but_not_descriptive_rules():
    d,a=sample();rules=RetestRules();original=retest_identity(a,d,Settings(),rules,'DEMO','Synthetic')
    a.rules['min_relative_volume']=9.
    assert retest_identity(a,d,Settings(),rules,'DEMO','Synthetic')==original
    assert retest_identity(a,d,replace(Settings(),lookback=30,stop_atr=3),rules,'DEMO','Synthetic')==original
    assert retest_identity(a,d,replace(Settings(),fee_bps=25),rules,'DEMO','Synthetic')!=original
    assert retest_identity(a,d,Settings(),rules,'DEMO','Unadjusted')!=original
    a.frame=a.frame.iloc[:-1]
    assert retest_identity(a,d,Settings(),rules,'DEMO','Synthetic')!=original
    d.metadata['execution_restriction']='Blocked action research'
    with pytest.raises(ValueError,match='Blocked'):save_retest(a,d,Settings(),rules,'DEMO','Synthetic')


def app_retest():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()
    app.radio(key='strategy_choice').set_value('Breakout-retest v1').run()
    assert not app.exception
    return app


def test_ui_saved_rule_changes_exports_switching_and_replay():
    app=app_retest()
    app.button(key='run_retest').click().run()
    saved=app.session_state['saved_retest_run'].record_json
    assert any(m.label=='Retest strategy trades' and m.value=='4' for m in app.metric)
    app.number_input(key='retest_rule_max_hold').set_value(5).run()
    assert any('Saved breakout-retest result is out of date' in w.value for w in app.warning)
    assert app.session_state['saved_retest_run'].record_json==saved
    next(c for c in app.checkbox if c.label=='Show Bollinger bands').check().run()
    assert app.session_state['saved_retest_run'].record_json==saved
    app.button(key='run_retest').click().run()
    assert not any('Saved breakout-retest result is out of date' in w.value for w in app.warning)
    assert json.loads(app.session_state['saved_retest_run'].record_json)['rules']['max_hold']==5
    app.radio(key='strategy_choice').set_value('Fixed breakout baseline').run()
    app.button(key='run_baseline').click().run()
    assert app.session_state['saved_baseline_run'].record_json
    app.radio(key='strategy_choice').set_value('Breakout-retest v1').run()
    assert app.number_input(key='retest_rule_max_hold').value==5
    assert not app.exception
    app.select_slider[0].set_value('2023-01-30').run()
    assert any('Saved breakout-retest result is out of date' in w.value for w in app.warning)
    app.button(key='run_retest').click().run()
    record=json.loads(app.session_state['saved_retest_run'].record_json)
    assert not record['candidates'] and not record['trades']
    assert record['candidate_columns'][0]=='setup_id'
    assert any('No simulated trades' in i.value for i in app.info)


def test_concept_and_event_strategy_links_select_the_requested_strategy():
    app=app_retest()
    app.button(key='run_retest').click().run()
    app.button(key='reference_retest_strategy').click().run()
    assert app.selectbox(key='chosen_concept').value=='retest-strategy'
    app.radio(key='workspace_page').set_value('Pattern research').run()
    app.button(key='study_to_baseline').click().run()
    assert app.radio(key='strategy_choice').value=='Fixed breakout baseline'
    app.button(key='explore_outcomes').click().run()
    app.button(key='study_to_retest').click().run()
    assert app.radio(key='strategy_choice').value=='Breakout-retest v1'
    assert not app.exception


def test_strategy_selection_survives_missing_upload_gate_and_reference_page():
    app=app_retest()
    next(r for r in app.radio if r.label=='Data source').set_value('Upload daily data').run()
    assert any('Upload one symbol' in i.value for i in app.info)
    next(r for r in app.radio if r.label=='Data source').set_value('Demo data').run()
    assert app.radio(key='strategy_choice').value=='Breakout-retest v1'
    app.radio(key='workspace_page').set_value('Learn').run()
    app.radio(key='workspace_page').set_value('Analyze').run()
    assert app.radio(key='strategy_choice').value=='Breakout-retest v1'
    assert not app.exception


def test_adjusted_research_view_disables_retest_execution_and_does_not_save(monkeypatch):
    import streamlit as st
    prices,events=synthetic_action_files()
    def uploader(*args,**kwargs):
        is_action=kwargs.get('key')=='action_ledger_file'
        f=BytesIO(events if is_action else prices);f.name='actions.csv' if is_action else 'prices.csv'
        return f
    monkeypatch.setattr(st,'file_uploader',uploader)
    app=app_retest()
    next(r for r in app.radio if r.label == "Data source").set_value('Upload daily data').run()
    next(c for c in app.checkbox if c.label=='Every row is a completed daily session bar').check().run()
    next(s for s in app.selectbox if s.label=='Price adjustment basis').set_value('Unadjusted OHLC').run()
    app.checkbox(key='use_action_ledger').check().run()
    app.radio(key='action_price_view').set_value('Split/bonus adjusted research').run()
    assert not app.exception and app.button(key='run_retest').disabled
    assert 'saved_retest_run' not in app.session_state
