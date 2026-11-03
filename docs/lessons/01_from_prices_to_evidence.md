# Lesson 1 · From prices to evidence

Your goal is to build the habit of asking **what is known, when is it known,
and what would disprove the idea?** This is more useful than memorizing a hundred
pattern names. All prices below are hypothetical teaching examples in INR.

## 1. Four layers that must stay separate

| Layer | Example | What it does not establish |
| --- | --- | --- |
| Observation | Today's close exceeded the previous 20 highs | A good execution price tomorrow |
| Calculation | RSI14 is 66.67 under a stated seed convention | A 66.67% chance of profit |
| Strategy | Enter next open; 2 ATR stop; 2R target; ten-session expiry | A profitable rule |
| Research evidence | Frozen-rule results on eligible unseen observations after costs | Guaranteed future performance |

The application is a workbench for moving carefully between these layers. An LLM
will eventually explain the evidence; it will not replace the calculations.

## 2. Read a candle before reading an indicator

Suppose a completed daily bar has open100, high108, low98, close105 and volume50,000.

- The body is105−100=5.
- The upper shadow is108−105=3.
- The lower shadow is100−98=2.
- The high-low range is108−98=10.
- It is an up-body candle because close exceeds open.

You cannot tell whether98 occurred before108, how many separate traders
participated, or whether an order of your size would fill at105. Daily bars
compress a sequence into a summary. That lost sequence matters in backtesting.

**Try:** draw O105,H109,L99,C101. Then suppose yesterday closed at100. The candle
has a down body but a positive close-to-close return. Explain why both are true.

## 3. Separate a change in quoted price from an economic return

Price rising from200 to210 is210/200−1=5%. But a hypothetical2-for-1 split can
change200 into100 while doubling shares, before any other movement. Treating that
as a50% loss corrupts indicators, stop levels and strategy outcomes.

Our uploader checks numerical relationships but cannot prove adjustment quality.
That is why the next data milestone includes corporate-action records and a
consistent OHLC/volume policy, not merely a download button.

**Try:** explain why adjusted close plus unadjusted high/low is a dangerous input.
Do not invent an adjustment because a price move looks large; verify the event.

## 4. Calculate a smoothing step

Closes100,102,104 give SMA3=(100+102+104)/3=102. With EMA3, alpha=2/(3+1)=0.5.
If the previous EMA is100 and today's close is104, the update is0.5×104+0.5×100=102.
The previous EMA is an input: initialization therefore affects early values.

Read `quant_engine/indicators.py`. The current EMA uses a recursive first-price
seed and hides output until its warm-up is complete. Wilder RSI and ATR use
arithmetic seeds followed by their own recursion. Do not assume every library's
early values are identical simply because its indicator has the same name.

## 5. Interpret RSI and MACD without turning them into probabilities

For already-smoothed average gain2 and loss1, RS=2 and RSI=100−100/(1+2)=66.67.
This is a description of recent gain/loss balance. It does not count future winners.
RSI80 can coexist with continued gains in a strong trend.

For fast EMA105 and slow EMA101, MACD=4. If its signal is3, histogram=1. A
positive histogram means MACD is above its signal, not necessarily that MACD is
above zero. For example MACD−2 and signal−3 also give histogram+1.

**Practice:** use the Learning lab for average gain3 and loss1. Then gain0/loss0.
Explain the app's flat-series convention instead of interpreting50 as a forecast.

## 6. Distinguish the size of movement from its direction

Yesterday close100, today high108 and low104 give true range max(4,8,4)=8. The
high-low range alone misses the gap from yesterday's close. ATR averages true ranges
using a specified convention; rising ATR does not specify bullish or bearish.

If ATR=3, a2ATR stop has a gross6-per-share distance. This links volatility to
position quantity. It does not make the stop impossible to gap through.

## 7. Find when a pattern becomes knowable

The starter pivot rule needs three bars on the left and three on the right. A
peak at session10 is not confirmed until session13 closes. The marker may be
drawn at10 for visual clarity, but its evidence must say known at13.

**Practice in the app:** keep the synthetic walkthrough selected. Move replay
across a visible peak. Hover the eventual pivot and compare its formation and
knowability dates. Then explain why an entry on10 based on that confirmation
would be look-ahead bias.

An Evening Star similarly needs its required third candle. We explain and
illustrate it, but have not implemented its detector. Read its concept entry and
identify prior trend, first body, small middle body and third-bar penetration.
The exact gap/penetration convention must be selected before testing.

## 8. Make a risk calculation explicit

Capital100,000 with1% intended risk gives a1,000 budget. At entry200 and stop195,
gross risk per share is5, so gross quantity is floor(1,000/5)=200. That position
requires40,000 before entry fees. Risk budget and exposure are different amounts.

With charges and adverse stop slippage, modeled loss per share exceeds5 and
quantity falls. The lab calls the same sizing function as the engine, which
also caps quantity by cash and1% of the previous session's reported volume.

**Try:** set costs to zero, then restore10bps fees and5bps stop slippage. Compare
quantity and cash required. Next set prior volume to50: the1% cap cannot support
one whole share, so quantity becomes zero.

This is an intentionally simple fill model. A stop at195 does not guarantee an
exit there. An opening gap to180 can make realized loss larger than the budget.
The prototype models gap-through-stop exits; it does not model all execution risks.

## 9. Turn the idea into a complete rule

The current baseline asks whether a completed close is above the prior20 highs,
above EMA50 and on relative volume at least1.2. If true, the next observed
session's open is the earliest entry opportunity under this simulator. Stops and
targets are fixed from that entry using the already-known ATR. There is one long
position, a2ATR stop, a2R target and a ten-session maximum hold.

Notice the important words: **prior**, **completed**, **next**, **already-known**
and **maximum**. Without them, the idea is too ambiguous to reproduce.

**Write your own rule specification**, without optimizing it yet:

1. Instrument/universe and timeframe.
2. Data source, adjustment basis and availability time.
3. Exact signal inputs and parameters.
4. Earliest eligible entry, order assumption, expiry and non-fill behavior.
5. Stop, target, holding limit and invalidation.
6. Position sizing and cost assumptions.
7. A simple benchmark and a chronological evaluation protocol.
8. A result that would make you reject or revise the hypothesis.

## 10. Read a result critically

An equity path100,000→110,000→99,000 has a10% drawdown from its peak. Closed-trade
cash alone can hide losses while positions remain open, which is why the starter
equity curve includes an estimated liquidation value.

A win rate needs a denominator and net gains/losses. A hypothetical40% win rate
with average gain200 and loss100 gives expected P&L20 per trade before omitted
costs. That arithmetic does not tell us those frequencies will persist.

If a candle reaches both stop and target, its daily summary does not order the
touches. Our conservative simulator chooses the stop first. That is a declared
assumption, not recovered intraday truth. The historical example is exploratory:
we have not established a profitable strategy on real Indian equities.

## Answer guide and completion check

- Candle O105,H109,L99,C101: body4, upper shadow4, lower shadow2. Relative to a
  prior100 close, the return is+1%, even though today's body is down.
- Gain3/loss1 gives RSI75; gain0/loss0 gives50 under this implementation's policy.
- MACD−2 minus signal−3 is histogram+1; MACD remains below its zero line.
- Stop-driven gross quantity200 with entry200/stop195 is an exposure of40,000,
  not a1,000 investment. Costs and caps can lower that quantity.
- A three-right-bar pivot at10 is usable after13 closes, under this daily rule.
- A3-candle observation cannot be confirmed with only its first2 candles.

You have completed the exercise when you can explain these in your own words,
locate the corresponding app fields and reproduce the arithmetic. The project
does not mark your understanding as complete automatically. Send questions or your
answers in the chat; we will record and work through them as the build proceeds.

## Where the code connects

| Idea | Read next |
| --- | --- |
| File validation and sessions | `quant_engine/data.py` |
| Smoothing, RSI, MACD and ATR | `quant_engine/indicators.py` |
| Pivots and geometric observations | `quant_engine/patterns.py` |
| Signal, sizing and execution | `quant_engine/strategy.py` |
| Evidence/report consistency | `quant_engine/analysis.py` |
| Learning content and curriculum | `learning/concepts.py`, `learning/roadmap.py` |
| Verification examples | `tests/test_engine.py`, `tests/test_learning.py` |

Further reading: [Fidelity RSI](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI),
[Fidelity MACD](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd),
[Fidelity ATR](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/atr),
[Zerodha's Morning/Evening Star discussion](https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/).
External authors may use different entry, gap or confirmation conventions; our
implementation and tests must always state the actual rule we use.
