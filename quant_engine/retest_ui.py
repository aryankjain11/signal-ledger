"""Inspectable strategy lifecycle, audit reasons and saved-run-only visual evidence."""
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .retest_records import retest_identity, save_retest
from .retest_strategy import RetestRules, STRATEGY_VERSION
from .workflow_ui import navigate


def retest_controls():
    with st.expander("Breakout-retest strategy rules", expanded="saved_retest_run" not in st.session_state):
        st.caption("These controls belong only to this execution strategy. The chart's descriptive analysis controls and the fixed baseline remain separate.")
        cols = st.columns(3)
        specs = [("lookback", "Prior range (observations)", 5, 252, 20, 1),
            ("retest_window", "Retest expiry age (observations)", 2, 60, 10, 1),
            ("max_hold", "Maximum holding observations", 1, 252, 10, 1),
            ("min_relative_volume", "Minimum breakout relative volume", 0., 10., 1.2, .1),
            ("breakout_buffer_atr", "Breakout close buffer (frozen ATR)", 0., 10., .1, .05),
            ("retest_tolerance_atr", "Retest touch tolerance (frozen ATR)", 0., 10., .25, .05),
            ("invalidation_atr", "Close invalidation below level (frozen ATR)", 0., 10., .5, .1),
            ("stop_buffer_atr", "Stop below retest/level (frozen ATR)", .01, 10., .25, .05),
            ("max_entry_gap_atr", "Maximum upward entry gap (frozen ATR)", 0., 10., 1., .25),
            ("reward_multiple", "Gross target multiple (R)", .1, 10., 2., .25)]
        values = {}
        remembered = st.session_state.get("retest_rule_values", {})
        for i, (name, label, low, high, default, step) in enumerate(specs):
            values[name] = cols[i % 3].number_input(label, min_value=low, max_value=high,
                value=remembered.get(name, default), step=step, key=f"retest_rule_{name}",persist_state="session")
        st.session_state["retest_rule_values"] = values
    return RetestRules(**values)


def setup_chart(record, setup_id):
    """All prices and annotations come from the saved snapshot, including stale runs."""
    candidate = next(c for c in record["candidates"] if c["setup_id"] == setup_id)
    bars = pd.DataFrame(record["bars"])
    bars["date"] = pd.to_datetime(bars.date)
    start = max(0, int(candidate["breakout_index"]) - 15)
    trade = next((t for t in record["trades"] if t["setup_id"] == setup_id), None)
    decision = candidate.get("decision_date")
    last_index = int(trade["exit_index"]) if trade else int(bars.index[bars.date.eq(pd.Timestamp(decision))][0]) if decision else len(bars) - 1
    # No following outcomes from another/current dataset are introduced here.
    shown = bars.iloc[start:min(len(bars), last_index + 4)]
    fig = go.Figure(go.Candlestick(x=shown.date, open=shown.open, high=shown.high, low=shown.low, close=shown.close,
        name="Saved OHLC", increasing_line_color="#36d6a4", decreasing_line_color="#ff6b82"))
    fig.add_scatter(x=[candidate['breakout_date'],bars.date.iloc[last_index]],y=[candidate['level']]*2,
        mode="lines",name="Level frozen at breakout close",line=dict(color="#6ca6ff",dash="dot"))
    for key, label, color, ykey in (("breakout_date", "Breakout known at close", "#6ca6ff", "breakout_close"),
        ("retest_date", "Retest known at close", "#f6c86a", "retest_close"),
        ("entry_date", "Next-open fill", "#36d6a4", "entry")):
        if candidate.get(key) and candidate.get(ykey) is not None:
            fig.add_scatter(x=[candidate[key]], y=[candidate[ykey]], mode="markers", name=label,
                marker=dict(size=11, color=color, symbol="diamond"))
    if candidate.get("stop") is not None:
        known = candidate["retest_date"]
        fig.add_scatter(x=[known, bars.date.iloc[last_index]], y=[candidate["stop"]]*2, mode="lines",
            name="Stop frozen at retest close", line=dict(color="#ff6b82", dash="dash"))
    if trade:
        fig.add_scatter(x=[trade["entry_date"], trade["exit_date"]], y=[trade["target"]]*2,
            mode="lines+markers", name="Target fixed at entry", line=dict(color="#36d6a4", dash="dash"),
            marker=dict(color="#36d6a4", symbol="line-ew", size=14, line=dict(width=2,color="#36d6a4")))
        fig.add_scatter(x=[trade["exit_date"]], y=[trade["exit"]], mode="markers", name=trade["reason"],
            marker=dict(size=12, color="#ffffff", symbol="x"))
    elif candidate.get('entry_attempt_date'):
        fig.add_scatter(x=[candidate['entry_attempt_date']],y=[candidate['entry_attempt_open']],mode='markers',
            name='Entry cancelled · no fill',marker=dict(size=12,color='#ff6b82',symbol='x'))
    fig.update_layout(template="plotly_dark", height=510, xaxis_rangeslider_visible=False,
        paper_bgcolor="#101a2b", plot_bgcolor="#101a2b", margin=dict(l=12,r=12,t=40,b=10),
        legend=dict(orientation="h", y=-.2))
    fig.update_xaxes(range=[shown.date.iloc[0]-pd.Timedelta(hours=12), shown.date.iloc[-1]+pd.Timedelta(hours=12)])
    return fig


def render_retest_lab(analysis, data, settings, symbol, adjustment):
    st.subheader("Breakout-retest · wait, confirm, then test")
    st.write("Buy only at the next observed open after a later retest closes holding the frozen breakout level and above EMA50. The retest low is never assumed to be your entry.")
    rules = retest_controls()
    st.caption(f"{STRATEGY_VERSION} · retest ages 1–{rules.retest_window-1}; expiry checked first at age {rules.retest_window}. Stop = min(retest low, level) − {rules.stop_buffer_atr:g} frozen ATR. Target = actual slipped entry + {rules.reward_multiple:g} × entry-to-stop distance.")
    st.write(f"**Entry cancellations:** open at/below stop; below breakout level; more than {rules.max_entry_gap_atr:g} frozen ATR above retest close; nonpositive reward after costs; or fewer than one share under cash/risk/prior-volume limits.")
    st.caption(f"Uses sidebar capital/risk/costs; maximum {settings.participation:.1%} of retest-bar volume. One setup/position at a time. No same-bar restart. Stops/targets remain fixed; stop first when both touch. Gaps can exceed planned loss. A {rules.max_hold}-observation hold includes the entry bar. Remaining positions close at replay end; pending setups stay pending.")
    restriction = data.metadata.get("execution_restriction") or analysis.frame.attrs.get("execution_restriction")
    if restriction:
        st.warning(restriction)
    if st.button("Run breakout-retest strategy", key="run_retest", type="primary", disabled=bool(restriction)):
        with st.spinner("Simulating one chronological setup/position at a time…"):
            st.session_state["saved_retest_run"] = save_retest(analysis,data,settings,rules,symbol,adjustment)
    saved = st.session_state.get("saved_retest_run")
    if saved is None:
        st.info("Run the strategy to see trades, pending/no-trade decisions and the setup audit. A valid short file can still lack EMA50 or a qualifying sequence.")
        return
    record = json.loads(saved.record_json)
    if saved.request_id == retest_identity(analysis,data,settings,rules,symbol,adjustment):
        st.success("Saved breakout-retest result matches the current calculation inputs.")
    else:
        st.warning("Saved breakout-retest result is out of date. Rerun for the current data/rules/costs. Every table, chart and download below belongs to the saved run.")
    old, cfg, m = record["analysis"], record["execution"], record["metrics"]
    st.write(f"**Saved strategy run:** {old['symbol']} · {old['rows']:,} observations · through {old['as_of'][:10]} · {old['adjustment_status']}")
    st.caption(f"Saved capital ₹{cfg['capital']:,.0f} · risk {cfg['risk_fraction']:.1%} · charges {cfg['fee_bps']:g} bps/side · slippage {cfg['slippage_bps']:g} bps/side. One record in this session; download to keep it.")
    cols=st.columns(4)
    cols[0].metric("Retest strategy trades",m["trades"])
    cols[1].metric("Retest net return",f"{m['total_return']:.2%}")
    cols[2].metric("Retest maximum drawdown",f"{m['max_drawdown']:.2%}")
    cols[3].metric("Retest historical win rate",f"{m['historical_win_fraction']:.1%}" if m['trades'] else "Unavailable")
    st.caption(f"{m['candidates']} candidate breaks · {m['cancelled']} rejected/cancelled/expired · {m['skipped_capacity']} skipped for capacity · {m['pending']} pending · {m['forced_cutoff_exits']} forced cutoff exits. {m['ready_observations']} observations had the strategy's calculation context.")
    if not m['trades']:
        st.info("No simulated trades. Review the setup audit and readiness; rejected and pending setups are not losing trades.")
    state=record["current"]
    st.markdown(f"**Conditional state at the saved cutoff: {state['status']}**")
    st.write(state['reason'])
    if state.get('level') is not None:
        st.caption(f"Frozen level {state['level']:.4f} · frozen ATR {state['reference_atr']:.4f}" + (f" · frozen stop {state['stop']:.4f}" if state.get('stop') is not None else ""))
    ledger,audit,inspect,exports=st.tabs(["Trades & equity","Setup audit","Inspect a setup","Strategy record & exports"])
    with ledger:
        equity=pd.DataFrame(record['equity']);equity['date']=pd.to_datetime(equity.date)
        from .charts import equity_chart
        st.plotly_chart(equity_chart(equity.set_index('date')), width="stretch")
        st.caption("Equity marks held shares at estimated net liquidation value. End-of-file exits are included above and labelled separately in the ledger. No benchmark superiority is claimed.")
        trades=pd.DataFrame(record['trades'],columns=record['trade_columns'])
        columns=['entry_date','exit_date','quantity','pnl','reason','entry','stop','target','planned_risk','realized_r','breakout_date','retest_date','forced_cutoff_exit']
        labels={'breakout_date':'Breakout close','retest_date':'Retest close','entry_date':'Entry date','exit_date':'Exit date',
            'entry':'Entry fill','stop':'Stop threshold','target':'Target threshold','quantity':'Shares','planned_risk':'Planned loss (INR)',
            'pnl':'Net P&L (INR)','realized_r':'Net P&L / planned loss','reason':'Exit reason','forced_cutoff_exit':'Forced cutoff exit'}
        st.dataframe(trades[columns].rename(columns=labels),hide_index=True,width="stretch")
    with audit:
        candidates=pd.DataFrame(record['candidates'],columns=record['candidate_columns'])
        st.write("Every fresh price/volume break receives a setup decision. A pending setup does not count as a loss; capacity skips are not executable trades.")
        columns=['breakout_date','retest_date','status','reason','level','stop','entry_attempt_open','max_entry_open','entry_date','quantity','planned_risk','decision_date']
        st.dataframe(candidates[columns].rename(columns={'breakout_date':'Breakout close','retest_date':'Retest close',
            'status':'Decision','reason':'Reason','level':'Frozen level','stop':'Frozen stop','entry_date':'Entry date',
            'quantity':'Shares','planned_risk':'Planned loss (INR)','decision_date':'Decision date',
            'entry_attempt_open':'Observed entry-attempt open','max_entry_open':'Maximum allowed open'}),hide_index=True,width="stretch")
        st.markdown("**Chronological transitions**")
        events=pd.DataFrame(record['events'],columns=record['event_columns'])
        st.dataframe(events.drop(columns=['index']).rename(columns={'setup_id':'Setup identifier','date':'Known on',
            'state':'Transition','reason':'Reason','level':'Frozen level','reference_atr':'Frozen ATR','stop':'Stop threshold',
            'target':'Target threshold','entry':'Entry fill'}),hide_index=True,width="stretch")
        st.caption("Natural events copy evidence when known. Artificial dataset-end liquidation is recorded in trades, not mislabelled as a natural transition.")
    with inspect:
        if record['candidates']:
            options={c['setup_id']:f"{c['breakout_date']} · {c['status']} · {c['reason']}" for c in record['candidates']}
            picked=st.selectbox("Saved setup to inspect",list(options),format_func=options.get,key="retest_inspect_"+saved.request_id[:16])
            st.plotly_chart(setup_chart(record,picked),width="stretch")
            st.caption("Saved prices only. Markers use close-time observations and actual simulated fills. Stop begins at retest confirmation; target begins at entry. Surrounding later bars are retrospective context.")
            candidate=next(c for c in record['candidates'] if c['setup_id']==picked)
            st.write(f"**{candidate['status']}** · {candidate['reason']}")
            st.caption(f"Breakout known {candidate['breakout_date']} · retest known {candidate.get('retest_date') or 'not observed'} · frozen level {candidate['level']:.4f} · frozen ATR {candidate['reference_atr']:.4f}")
            with st.expander("Exact setup evidence"):
                st.json(candidate)
        else:
            st.info("No price/volume breaks in this saved replay. More rows do not guarantee a qualifying sequence.")
    with exports:
        st.json({'strategy':record['strategy_version'],'request_id':saved.request_id,'recorded_at_utc':record['recorded_at_utc'],
            'rules':record['rules'],'execution':cfg,'conventions':record['execution_conventions']})
        st.download_button("Download breakout-retest record",saved.record_json,"breakout-retest.json","application/json",key="download_retest_record")
        for key,label in [('trades','trade ledger'),('candidates','setup decisions'),('events','transitions')]:
            columns=record[{'trades':'trade_columns','candidates':'candidate_columns','events':'event_columns'}[key]]
            st.download_button('Download retest '+label,pd.DataFrame(record[key],columns=columns).to_csv(index=False),
                f"retest-{key}.csv","text/csv",key='download_retest_'+key)
        st.caption("The record includes saved price bars and source evidence. Keep it private if your source has redistribution limits. Durable archive reopening remains planned.")
    st.warning(m['validation'])
    st.button("Read the breakout-retest strategy concept",key="reference_retest_strategy",on_click=navigate,args=("Learn","retest-strategy"))
