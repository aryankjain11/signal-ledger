"""Independent price-path and accounting checks, not claims of a trading edge."""
from dataclasses import replace
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from quant_engine.models import Settings
from quant_engine.retest_strategy import RetestRules, simulate_retest


def path(n=26):
    f = pd.DataFrame({"open": 99., "high": 100., "low": 98., "close": 99.,
        "volume": 100000., "ema_50": 98., "atr_14": 2., "relative_volume": 1.},
        index=pd.bdate_range("2026-01-01", periods=n))
    put(f, 20, 100, 103, 99, 102)
    f.iloc[20, f.columns.get_loc("relative_volume")] = 2.
    if n > 21:
        put(f, 21, 102, 102.5, 99.8, 101.5)
    if n > 22:
        put(f, 22, 102, 103, 101, 102.5)
    if n > 23:
        put(f, 23, 103, 109, 102, 108)
    return f


def put(f, i, o, h, l, c):
    f.iloc[i, f.columns.get_indexer(["open", "high", "low", "close"])] = [o, h, l, c]


FREE = Settings(fee_bps=0., slippage_bps=0.)


def test_hand_calculated_trade_freezes_structure_and_obeys_next_open_chronology():
    f = path()
    f.iloc[20:, f.columns.get_loc("atr_14")] = 50.  # unavailable to the frozen reference
    r = simulate_retest(f, FREE)
    t = r.trades.iloc[0]
    assert t.breakout_index == 20 and t.retest_index == 21 and t.entry_index == 22
    assert t.exit_index == 23 and t.reason == "Target"
    assert t.level == 100 and t.reference_atr == 2
    assert t.stop == pytest.approx(99.3) and t.entry == 102 and t.target == pytest.approx(107.4)
    assert t.quantity == 370 and t.planned_risk == pytest.approx(999)
    assert t.pnl == pytest.approx(1998) and t.realized_r == pytest.approx(2)
    assert r.metrics["final_equity"] == pytest.approx(101998)
    assert r.equity.cash.iloc[22] == pytest.approx(62260)
    assert r.equity.equity.iloc[22] == pytest.approx(62260 + 370*102.5)
    assert r.events.state.tolist()[:4] == ["Breakout accepted", "Retest confirmed", "Entry filled", "Exit"]
    assert pd.isna(r.events.iloc[0].stop) and pd.isna(r.events.iloc[1].entry)
    assert r.candidates.iloc[0].status == "Closed"


def test_fees_slippage_and_marked_equity_match_independent_arithmetic():
    r = simulate_retest(path(), Settings())
    t = r.trades.iloc[0]
    entry = 102*1.0005
    stop_fill = 99.3*.9995
    unit_loss = entry-stop_fill + .001*(entry+stop_fill)
    qty = int(1000//unit_loss)
    target = entry+2*(entry-99.3)
    exit_fill = target*.9995
    pnl = qty*(exit_fill*(1-.001)-entry*(1+.001))
    assert t.quantity == qty and t.quantity == 333
    assert t.pnl == pytest.approx(pnl)
    assert t.entry_fee == pytest.approx(qty*entry*.001)
    assert t.exit_fee == pytest.approx(qty*exit_fill*.001)
    assert r.metrics["final_equity"] == pytest.approx(100000+pnl)
    assert r.equity.equity.iloc[22] == pytest.approx(100000-qty*entry*1.001+qty*102.5*.9995*.999)
    assert t.planned_risk <= 1000


@pytest.mark.parametrize("o,h,l,c,reason", [(99,101,98,100,"at/below frozen stop"),
    (99.6,101,99.4,100,"lost the frozen breakout level"),
    (104,105,103,104,"exceeded the permitted upward gap")])
def test_next_open_cancel_is_not_deferred_or_retroactively_filled(o,h,l,c,reason):
    f = path();put(f,22,o,h,l,c)
    r = simulate_retest(f, FREE)
    assert r.trades.empty and reason in r.candidates.iloc[0].reason
    assert not (r.events.state == "Entry filled").any()
    assert r.candidates.iloc[0].entry_attempt_open==o
    assert r.candidates.iloc[0].max_entry_open==103.5


def test_entry_gap_boundary_allowed_and_uses_actual_entry_for_target_and_size():
    f = path(23);put(f,22,103.5,104,103,103.8)
    r = simulate_retest(f, FREE)
    t = r.trades.iloc[0]
    assert t.entry == 103.5 and t.stop == pytest.approx(99.3)
    assert t.target == pytest.approx(111.9) and t.quantity == 238
    assert t.reason == "End of data"


@pytest.mark.parametrize("failure", [True,False])
def test_failure_and_expiry_precede_retest_on_deadline(failure):
    f=path(23)
    put(f,21,102,103,101,102)
    put(f,22,101,102,98 if failure else 99.8,98.9 if failure else 101)
    r=simulate_retest(f,FREE,RetestRules(retest_window=2))
    first=r.candidates.iloc[0]
    assert first.status == ("Cancelled" if failure else "Expired")
    assert not (r.events.state == "Retest confirmed").any()


def test_last_eligible_retest_can_enter_on_deadline_open():
    r=simulate_retest(path(),FREE,RetestRules(retest_window=2))
    assert r.trades.iloc[0].retest_index == 21 and r.trades.iloc[0].entry_index == 22


@pytest.mark.parametrize("n,status", [(21,"Awaiting retest"),(22,"Awaiting next open")])
def test_file_end_does_not_label_pending_setup_as_failure(n,status):
    r=simulate_retest(path(n),FREE)
    assert r.current["status"] == status and r.metrics["pending"] == 1
    assert r.trades.empty and r.metrics["historical_win_fraction"] is None
    assert r.candidates.iloc[0].status == status


@pytest.mark.parametrize("which", ["breakout","retest"])
def test_trend_filter_rejections_and_warmup_are_explained(which):
    f=path();f.iloc[20 if which=="breakout" else 21,f.columns.get_loc("ema_50")] = np.nan
    r=simulate_retest(f,FREE)
    assert r.trades.empty and "EMA50" in r.candidates.iloc[0].reason


def test_weak_volume_non_crossing_and_zero_atr_do_not_invent_candidates():
    f=path();f.iloc[20,f.columns.get_loc("relative_volume")]=1.
    assert simulate_retest(f,FREE).candidates.empty
    f=path();f.iloc[19,f.columns.get_loc("atr_14")]=0.
    assert simulate_retest(f,FREE).candidates.empty
    f=path();put(f,20,99,100,98,99)
    assert simulate_retest(f,FREE).candidates.empty


def test_zero_history_readiness_and_no_trade_metrics_are_defined():
    f=path(21).iloc[:10]
    r=simulate_retest(f,FREE)
    assert r.metrics["ready_observations"] == 0
    assert r.metrics["trades"] == 0 and r.metrics["total_return"] == 0
    assert r.metrics["max_drawdown"] == 0 and r.metrics["profit_factor"] is None


@pytest.mark.parametrize("entry_bar", [True,False])
def test_stop_first_on_daily_bar_ambiguity_including_entry_bar(entry_bar):
    f=path();put(f,22 if entry_bar else 23,102,110,98,103)
    t=simulate_retest(f,FREE).trades.iloc[0]
    assert "both touched" in t.reason and t.exit == pytest.approx(99.3)
    assert t.pnl == pytest.approx(-999)


def test_opening_stop_gap_exceeds_planned_risk_and_has_priority():
    f=path();put(f,23,80,110,79,105)
    t=simulate_retest(f,Settings()).trades.iloc[0]
    assert t.reason == "Gap through stop" and t.exit == pytest.approx(80*.9995)
    assert -t.pnl > t.planned_risk


def test_opening_target_gap_uses_observed_open_not_intraday_stop():
    f=path();put(f,23,112,114,98,105)
    t=simulate_retest(f,FREE).trades.iloc[0]
    assert t.reason == "Gap above target" and t.exit == 112.


@pytest.mark.parametrize("hold", [1,2])
def test_holding_limit_counts_entry_observation(hold):
    f=path();put(f,23,103,104,102,103)
    t=simulate_retest(f,FREE,RetestRules(max_hold=hold)).trades.iloc[0]
    assert t.reason == "Holding limit" and t.holding_sessions == hold
    assert t.exit_index == 21+hold


def test_cutoff_liquidation_is_explicit_and_does_not_become_natural_exit_event():
    r=simulate_retest(path(23),FREE)
    assert r.current["status"] == "Open at cutoff"
    assert r.metrics["forced_cutoff_exits"] == 1
    assert r.trades.iloc[0].forced_cutoff_exit
    assert "Exit" not in r.events.state.tolist()


def test_prior_retest_volume_limits_fill_and_zero_quantity_is_audited():
    f=path();f.iloc[21,f.columns.get_loc("volume")]=1000.;f.iloc[22,f.columns.get_loc("volume")]=10000000.
    t=simulate_retest(f,FREE).trades.iloc[0]
    assert t.quantity == 10 and t.liquidity_quantity == 10
    f.iloc[21,f.columns.get_loc("volume")]=0.
    r=simulate_retest(f,FREE)
    assert r.trades.empty and "fewer than one share" in r.candidates.iloc[0].reason
    assert r.candidates.iloc[0].liquidity_quantity == 0


def test_touch_without_held_close_is_not_a_retest_and_level_open_boundary_is_allowed():
    f=path(22);put(f,21,101,102,99.2,99.5)
    r=simulate_retest(f,FREE)
    assert r.current['status']=='Awaiting retest'
    assert r.events.state.tolist()==['Breakout accepted']
    f=path(23);put(f,22,100,101,99.5,100.5)
    t=simulate_retest(f,FREE).trades.iloc[0]
    assert t.entry==100.


def test_cash_cap_and_nonpositive_net_reward_cancellation():
    t=simulate_retest(path(),replace(FREE,capital=1000.,risk_fraction=.1)).trades.iloc[0]
    assert t.quantity == 9 and t.cash_required <= 1000
    r=simulate_retest(path(),Settings(fee_bps=100.,slippage_bps=100.),RetestRules(reward_multiple=.01))
    assert r.trades.empty and "nonpositive after" in r.candidates.iloc[0].reason


def test_nonpositive_structural_stop_is_cancelled():
    f=path();put(f,21,102,103,.1,101)
    r=simulate_retest(f,FREE)
    assert r.trades.empty and "nonpositive structural stop" in r.candidates.iloc[0].reason


def test_busy_fresh_break_is_audited_without_pyramiding():
    f=path(26);put(f,22,102,103,101,102.5);put(f,23,103,105,102,104)
    f.iloc[23,f.columns.get_loc("relative_volume")]=2.
    r=simulate_retest(f,FREE)
    assert (r.candidates.status == "Skipped capacity").sum() == 1
    assert len(r.trades) == 1


def test_exit_bar_cannot_restart_and_invalidation_equality_stays_pending():
    f=path();f.iloc[23,f.columns.get_loc('relative_volume')]=2.
    r=simulate_retest(f,FREE)
    assert r.trades.iloc[0].exit_index==23
    assert r.candidates.iloc[1].status=='Skipped capacity'
    assert r.candidates.iloc[1].breakout_index==23
    f=path(22);put(f,21,101,102,98.5,99.)
    assert simulate_retest(f,FREE).current['status']=='Awaiting retest'


def test_every_prefix_has_same_natural_event_tape_and_no_input_mutation():
    f=path();before=deepcopy(f);full=simulate_retest(f,FREE)
    for n in range(20,len(f)+1):
        prefix=simulate_retest(f.iloc[:n],FREE)
        expected=full.events.loc[full.events["index"] < n].reset_index(drop=True)
        pd.testing.assert_frame_equal(prefix.events,expected,check_dtype=False)
    pd.testing.assert_frame_equal(f,before)


@pytest.mark.parametrize("kwargs", [dict(lookback=True),dict(lookback=3),dict(retest_window=1),
    dict(max_hold=1.5),dict(stop_buffer_atr=0),dict(reward_multiple=0),
    dict(max_entry_gap_atr=np.nan),dict(min_relative_volume=np.inf),dict(invalidation_atr=-1)])
def test_invalid_rules_rejected(kwargs):
    with pytest.raises(ValueError):RetestRules(**kwargs)


def test_engine_enforces_execution_restriction_and_input_contract():
    f=path();f.attrs["execution_restriction"]="Adjusted share accounting unavailable"
    with pytest.raises(ValueError,match="share accounting"):simulate_retest(f,FREE)
    f=path().iloc[::-1]
    with pytest.raises(ValueError,match="increasing"):simulate_retest(f,FREE)
    f=path();f.iloc[22,f.columns.get_loc("low")]=1000.
    with pytest.raises(ValueError,match="consistent OHLC"):simulate_retest(f,FREE)
