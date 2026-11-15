from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze
from quant_engine.charts import price_chart, clip_geometry, chart_window_caption
from quant_engine.data import load_bars
from quant_engine.models import Settings
from quant_engine.readiness import readiness_rows
from quant_engine.saved_backtest import backtest_identity, save_backtest

ROOT = Path(__file__).resolve().parents[1]


def sample(n=None):
    data = load_bars((ROOT/'data/synthetic_daily.csv').read_bytes(), 'synthetic.csv')
    if n:
        data.bars = data.bars.iloc[:n].copy()
    return data, analyze(data, Settings())


def test_narrow_chart_clips_all_coordinates_without_changing_original_evidence():
    data, full = sample()
    event = next(e for e in full.events if e.get('family') == 'breakout' and e['status'] == 'Breakout')
    data.bars = data.bars.iloc[:event['index']+1]
    analysis = analyze(data, Settings())
    original = deepcopy(analysis.events)
    analysis.frame = analysis.frame.iloc[-3:]
    start, end = analysis.frame.index[[0,-1]]
    fig = price_chart(analysis)
    for trace in fig.data:
        if trace.x is not None:
            dates = [pd.Timestamp(x) for x in trace.x if x is not None]
            assert all(start <= date <= end for date in dates), trace.name
    assert analysis.events == original
    assert list(fig.layout.xaxis.range) == [start-pd.Timedelta(hours=12), end+pd.Timedelta(hours=12)]
    assert fig.layout.xaxis.autorange is False
    assert len(fig.data[0].x) == 3


@pytest.mark.parametrize('points,expected', [
    ([['2026-01-01',0],['2026-01-11',10]], [('2026-01-03',2),('2026-01-05',4)]),
    ([['2026-01-11',10],['2026-01-01',0]], [('2026-01-05',4),('2026-01-03',2)]),
    ([['2025-01-01',0],['2025-01-02',10]], []),
    ([['2026-01-03',2],['2026-01-03',4]], [('2026-01-03',2),('2026-01-03',4)]),
])
def test_display_segment_clipping_has_exact_intersections_and_no_fake_anchor_markers(points, expected):
    clipped = clip_geometry(points, '2026-01-03', '2026-01-05')
    assert [(x.date().isoformat(), y) for x,y in clipped] == expected


def test_future_state_and_pivot_annotations_are_not_exposed_by_cropped_view():
    _, analysis = sample()
    analysis.frame = analysis.frame.iloc[100:120]
    end = analysis.frame.index[-1]
    fig = price_chart(analysis)
    for trace in fig.data:
        if trace.x is not None:
            assert all(pd.Timestamp(x) <= end for x in trace.x if x is not None)


def test_caption_reports_actual_counts_for_short_and_long_views():
    _, short = sample(21)
    assert 'Showing 21 of 21' in chart_window_caption(short)
    _, long = sample()
    assert 'Showing 250 of 600' in chart_window_caption(long)


def test_readiness_distinguishes_available_warming_and_undefined_calculations():
    _, a = sample(21)
    rows = {r['Calculation']:r for r in readiness_rows(a)}
    assert rows['RSI14']['Status'] == 'Available'
    assert rows['EMA50 / SMA50']['Status'] == 'Unavailable'
    assert '29 more' in rows['EMA50 / SMA50']['What is needed']
    assert rows['Fixed breakout baseline context']['Status'] == 'Unavailable'
    _, long = sample()
    long.frame['relative_volume'] = float('nan')
    row = next(r for r in readiness_rows(long) if r['Calculation'].startswith('Relative volume'))
    assert 'Undefined' in row['What is needed']


@pytest.mark.parametrize('count,label,available', [(14,'RSI14',False),(15,'RSI14',True),
    (13,'ATR14',False),(14,'ATR14',True),(33,'MACD signal / histogram',False),
    (34,'MACD signal / histogram',True),(49,'EMA50 / SMA50',False),(50,'EMA50 / SMA50',True)])
def test_readiness_uses_real_indicator_seeds_and_warmup_boundaries(count,label,available):
    _, analysis = sample(count)
    row = next(r for r in readiness_rows(analysis) if r['Calculation']==label)
    assert (row['Status']=='Available') == available


@pytest.mark.parametrize('change', [dict(capital=200000.),dict(risk_fraction=.02),dict(fee_bps=25.),
    dict(slippage_bps=20.),dict(lookback=30),dict(stop_atr=3.),dict(max_hold=20)])
def test_calculation_identity_changes_with_actual_strategy_assumptions(change):
    data, analysis = sample()
    a = backtest_identity(analysis,data,Settings(),'DEMO','Synthetic example')
    b = backtest_identity(analysis,data,replace(Settings(),**change),'DEMO','Synthetic example')
    assert a != b


def test_identity_captures_source_replay_price_basis_and_execution_restrictions():
    data, analysis = sample()
    original = backtest_identity(analysis,data,Settings(),'DEMO','Synthetic example')
    changed = deepcopy(data);changed.source_hash = 'another-file'
    assert backtest_identity(analysis,changed,Settings(),'DEMO','Synthetic example') != original
    assert backtest_identity(analysis,data,Settings(),'DEMO','Unadjusted OHLC') != original
    truncated = deepcopy(analysis);truncated.frame = truncated.frame.iloc[:-1]
    assert backtest_identity(truncated,data,Settings(),'DEMO','Synthetic example') != original
    changed = deepcopy(data);changed.metadata['execution_restriction']='Blocked research view'
    assert backtest_identity(analysis,changed,Settings(),'DEMO','Synthetic example') != original
    with pytest.raises(ValueError,match='Blocked'):
        save_backtest(analysis,changed,Settings(),'DEMO','Synthetic example')


def test_saved_export_is_immutable_and_observation_rules_do_not_change_strategy_identity():
    data, analysis = sample()
    saved = save_backtest(analysis,data,Settings(),'DEMO','Synthetic example')
    before = saved.record_json
    analysis.rules['min_relative_volume'] = 9.9
    assert backtest_identity(analysis,data,Settings(),'DEMO','Synthetic example') == saved.request_id
    analysis.frame.loc[analysis.frame.index[-1],'close'] *= 2
    data.source_hash = 'new-source'
    assert saved.record_json == before
    record = json.loads(before)
    assert record['analysis']['settings']['fee_bps'] == 10.
    assert record['metrics']['trades'] == 5
    assert record['analysis']['source_sha256'] != data.source_hash


def test_saved_ui_survives_overlay_and_navigation_and_marks_changed_costs_stale():
    app = AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    app.button(key='run_baseline').click().run()
    saved = app.session_state['saved_baseline_run'].record_json
    next(c for c in app.checkbox if c.label=='Show Bollinger bands').check().run()
    assert not app.exception
    assert any(m.label=='Completed trades' for m in app.metric)
    assert app.session_state['saved_baseline_run'].record_json == saved
    next(n for n in app.number_input if n.label=='Estimated total charges per side (bps)').set_value(25.).run()
    assert any('out of date' in w.value for w in app.warning)
    assert json.loads(app.session_state['saved_baseline_run'].record_json)['analysis']['settings']['fee_bps']==10.
    app.button(key='run_baseline').click().run()
    assert not any('out of date' in w.value for w in app.warning)
    app.button(key='reference_rsi').click().run()
    assert app.selectbox(key='workspace_page').value=='Education and Concepts'
    assert app.selectbox(key='chosen_concept').value=='rsi'
    app.selectbox(key='workspace_page').set_value('Research dashboard').run()
    assert not app.exception
    assert any(m.label=='Completed trades' for m in app.metric)
    assert next(n for n in app.number_input if n.label=='Estimated total charges per side (bps)').value == 25.
    assert next(c for c in app.checkbox if c.label=='Show Bollinger bands').value
    assert not any('out of date' in w.value for w in app.warning)
    assert json.loads(app.session_state['saved_baseline_run'].record_json)['analysis']['settings']['fee_bps']==25.


def test_outcome_and_baseline_navigation_links_and_requested_cohort():
    app = AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    app.button(key='explore_outcomes').click().run()
    assert app.title[0].value=='After the pattern'
    cohort = next(c for c in app.multiselect(key='study_cohorts').value if 'Retest held' in c)
    app.session_state['requested_study_cohort'] = cohort
    app.session_state['requested_study_direction'] = 1
    app.run()
    assert app.multiselect(key='study_cohorts').value == [cohort]
    app.button(key='study_to_baseline').click().run()
    assert not app.exception
    assert app.selectbox(key='workspace_page').value=='Research dashboard'
    assert app.button(key='run_baseline')


def test_short_upload_readiness_does_not_claim_ema50_or_baseline_is_available(monkeypatch):
    from io import BytesIO
    import streamlit as st
    content = pd.read_csv(ROOT/'data/synthetic_daily.csv').iloc[:21].to_csv(index=False).encode()
    uploaded = BytesIO(content);uploaded.name='short.csv'
    monkeypatch.setattr(st,'file_uploader',lambda *args,**kwargs: uploaded)
    app = AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    next(r for r in app.radio if r.label == "Data source").set_value('Upload daily data').run()
    app.checkbox[0].check().run()
    assert not app.exception
    assert any('29 more observations' in m.value for m in app.markdown)
    assert any('Showing 21 of 21' in c.value for c in app.caption)
    assert any('Partial analysis' in i.value for i in app.info)
