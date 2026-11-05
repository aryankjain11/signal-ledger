# Education and Concepts

Updated: 2026-11-05

126 entries. Source of truth: `learning/concepts.py`; the app and this handbook share it.

All numerical examples are invented teaching examples, explicitly not market observations or performance claims. A traditional pattern description does not demonstrate a trading edge. A glossary entry is not proof that its detector exists.

Start with OHLCV → returns/adjustments → confirmed structure → SMA/EMA → RSI/MACD → ATR/risk → backtesting/leakage → probability calibration. Use the app's Learning lab and `docs/lessons/01_from_prices_to_evidence.md`.

The concise catalogue establishes vocabulary now. Detailed calculations and tested implementation lessons expand one milestone at a time. External links are further reading, not endorsement of their trading-entry conventions. These notes and examples are original explanations, not copied chapters.

## OHLCV and the anatomy of a candle

**Category:** Foundations · **Application status:** Validated and charted

One bar summarizes one interval: open is its first traded price, high/low are its extremes, close is its last price, and volume is traded quantity. The body spans open to close; shadows extend to high and low. A daily candle hides the sequence of trades inside that day.

**Calculation or rule:** Body = |close − open|; range = high − low; upper shadow = high − max(open,close); lower shadow = min(open,close) − low.

**Hypothetical worked example:** Open ₹100, high ₹108, low ₹98, close ₹105: body ₹5, upper shadow ₹3, lower shadow ₹2, range ₹10. Volume 50,000 means shares traded in this example, not 50,000 unique investors.

**How to read it:** A green candle says close exceeded open; it can still close below yesterday's close.

**Common mistake:** Inferring whether the high or low occurred first from daily OHLC alone.

**Try it yourself:** Draw the candle for O=105, H=109, L=99, C=101. Explain what cannot be known from it.

**Further reading:** [Fidelity: technical analysis introduction](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/what-is-technical-analysis)

**Implementation reference:** `quant_engine/data.py; quant_engine/charts.py`

## Timeframe, session and resampling

**Category:** Foundations · **Application status:** Daily/prior-week context; bounded NSE CM 2026 calendar and freshness checks

A timeframe is the interval represented by a bar. An exchange session is a trading period, not necessarily a whole calendar day. Weekly OHLCV must be built from eligible daily bars, with clear handling of incomplete weeks.

**Calculation or rule:** Aggregate open=first, high=max, low=min, close=last, volume=sum.

**Hypothetical worked example:** Two bars (O100,H105,L99,C104,V10) and (O104,H108,L102,C103,V20) aggregate to O100,H108,L99,C103,V30.

**How to read it:** Higher-timeframe context becomes usable only after its required information is available.

**Common mistake:** Using Friday's completed weekly close to explain a trade made on Monday of that same week.

**Implementation reference:** `quant_engine/data.py: completed_weeks; quant_engine/calendar.py`

## Price, simple return and total return

**Category:** Foundations · **Application status:** Price-return comparison available; total-return engine pending

Price is a currency amount per share. Simple return measures relative change. Total return also includes distributions under a defined reinvestment convention; it cannot be inferred from an unadjusted closing-price ratio alone.

**Calculation or rule:** Simple price return = new_price / old_price − 1.

**Hypothetical worked example:** ₹200 to ₹210 is +5%. A ₹4 dividend requires separate treatment when measuring total return.

**Common mistake:** Treating a 2-for-1 split as a 50% economic loss.

## Corporate actions and adjusted prices

**Category:** Data quality · **Application status:** Reviewed split/bonus ledger and replay-aware OHLCV research normalization; dividend/total-return and execution accounting pending

Splits, bonus issues, dividends and reorganizations can change the meaning of historical prices. A consistent adjustment policy preserves comparability. Price and share-volume transformations must agree with the event type; dividend adjustment is different from split adjustment.

**Hypothetical worked example:** In a hypothetical 2-for-1 split, ₹200 with one share becomes about ₹100 with two shares before other market movement. Splits alone do not halve portfolio value.

**How to read it:** Keep the raw series, event record, adjusted series, method and version. Back-adjustment can revise old numbers, so research needs a point-in-time policy.

**Common mistake:** Combining adjusted close with unadjusted open/high/low, or assuming every sharp move is a split.

**Further reading:** [NSE: corporate actions](https://www.nseindia.com/companies-listing/corporate-filings-actions)

**Implementation reference:** `quant_engine/corporate_actions.py; quant_engine/actions_ui.py`

## Trend and market structure: HH, HL, LH, LL

**Category:** Price structure · **Application status:** Basic confirmed-pivot structure implemented

Higher high (HH) and higher low (HL) mean successive meaningful highs and lows are rising. Lower high (LH) and lower low (LL) mean they are falling. Mixed sequences need a mixed/range interpretation rather than a forced direction.

**Hypothetical worked example:** Confirmed highs 100→110 and lows 90→96 give HH+HL. Highs 110→104 with lows 96→92 give LH+LL.

**Common mistake:** Using an unconfirmed final swing as if it were already knowable.

**Implementation reference:** `quant_engine/patterns.py: market_structure`

## Swing pivot, confirmation delay and repainting

**Category:** Price structure · **Application status:** Delayed pivots and knowability dates implemented

A local swing high exceeds nearby highs; a swing low is below nearby lows. If a detector requires three right-hand bars, the pivot at bar t cannot be confirmed until bar t+3 closes. Repainting means later information changes a historically displayed conclusion.

**Hypothetical worked example:** A peak on session 10 with a three-bar right window is first knowable after session 13. Plotting the marker at 10 is fine only if its later detection time is disclosed.

**Common mistake:** Backtesting an entry on session 10 using the confirmation that requires session 13.

**Try it yourself:** Move replay across a peak; find the first date it becomes confirmed.

**Implementation reference:** `quant_engine/patterns.py: swings`

## Support, resistance and zones

**Category:** Price structure · **Application status:** As-of approximate pivot clusters implemented

Support is an area where declines have previously encountered buying; resistance is an area where advances have encountered selling. These are descriptive historical areas, not barriers that prices must respect. Nearby levels are often more honestly represented as zones.

**Hypothetical worked example:** Lows near ₹99.4, ₹100.0 and ₹100.5 may motivate a zone around ₹100, not a universally exact ₹100.00 support.

**Common mistake:** Calling every clustered pivot an independent successful test, or treating a zone as guaranteed protection.

**Implementation reference:** `quant_engine/patterns.py: support_resistance`

## Breakout, breakdown, retest and false breakout

**Category:** Strategies · **Application status:** Configurable frozen-range breakout/retest/failure/continuation observations; baseline strategy remains separate

A breakout moves beyond a defined upper boundary; a breakdown moves below a lower one. A retest revisits a breached boundary. A false breakout fails a predeclared continuation/invalidation rule. The rule must state whether it uses a touch, completed close, distance or volume.

**Hypothetical worked example:** A prior high is ₹100. A close at ₹101.2 with eligible volume may qualify under one rule, while an intraday high of ₹100.1 followed by a ₹99 close may not.

**Common mistake:** Changing the confirmation threshold after seeing which trades won.

**Implementation reference:** `quant_engine/research.py: breakout_events`

## SMA — Simple Moving Average

**Category:** Trend indicators · **Application status:** SMA20/50/200 computed

SMA is the equal-weight average of the last N observations. It smooths fluctuations but reacts after prices change. A 20-session average describes a different horizon from a 200-session average.

**Calculation or rule:** SMA_N = sum(last N closes) / N.

**Hypothetical worked example:** Closes 100,102,104 have a three-bar SMA of 102.

**Common mistake:** Assuming price crossing an average is automatically a profitable entry.

**Implementation reference:** `quant_engine/indicators.py`

## EMA — Exponential Moving Average

**Category:** Trend indicators · **Application status:** EMA20/50 and MACD EMAs computed

EMA assigns recursively declining weight to older observations. The smoothing constant and initial seed both matter when comparing implementations.

**Calculation or rule:** alpha=2/(N+1); EMA_today=alpha×close+(1−alpha)×EMA_previous.

**Hypothetical worked example:** With N=3, alpha=0.5, previous EMA=100 and close=104, the next EMA is 102.

**How to read it:** This app seeds with the first observation and hides values until the requested warm-up length; some other implementations seed with an SMA.

**Common mistake:** Comparing early EMA values across libraries without checking seeds.

**Implementation reference:** `quant_engine/indicators.py`

## RSI — Relative Strength Index

**Category:** Momentum indicators · **Application status:** Wilder RSI14 computed and numerically tested

RSI summarizes the balance of recent upward and downward price changes on a 0–100 scale. It measures momentum, not the probability of a profitable trade. The common 70/30 reference levels are conventions; strong trends can remain beyond them.

**Calculation or rule:** RS=smoothed average gain / smoothed average loss; RSI=100−100/(1+RS). Wilder14 seeds with 14 changes then uses (13×previous average+new change)/14.

**Hypothetical worked example:** If smoothed gain is ₹2 and loss ₹1, RS=2 and RSI≈66.67. In this implementation, both zero gives 50; loss zero with positive gain gives 100.

**How to read it:** Use trend, price structure and a tested rule for decisions; an RSI level alone is not an entry rule.

**Common mistake:** RSI80 does not mean an 80% win probability or a guaranteed imminent fall.

**Try it yourself:** Use the lab with gain=3 and loss=1; explain why the result is 75 rather than a forecast.

**Further reading:** [Fidelity: RSI](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI)

**Implementation reference:** `quant_engine/indicators.py; tests/test_engine.py`

## MACD — Moving Average Convergence/Divergence

**Category:** Momentum indicators · **Application status:** MACD12/26/9 computed; contextual strategy extension pending

MACD compares a faster and slower EMA to describe momentum relative to trend. The signal line smooths MACD; the histogram is their difference. MACD has price units, so raw magnitudes are not directly comparable across differently priced stocks.

**Calculation or rule:** MACD=EMA12−EMA26; signal=EMA9(MACD); histogram=MACD−signal.

**Hypothetical worked example:** Fast EMA=105, slow EMA=101 gives MACD=4. If signal=3, histogram=1. The histogram can shrink while MACD remains positive.

**How to read it:** Zero-line and signal-line crossings answer different questions; neither establishes an edge without evaluation.

**Common mistake:** Reading a positive histogram as guaranteed positive next-day returns.

**Try it yourself:** If MACD=−2 and signal=−3, calculate the histogram and explain the negative MACD/positive histogram combination.

**Further reading:** [Fidelity: MACD](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd)

**Implementation reference:** `quant_engine/indicators.py`

## ATR — Average True Range

**Category:** Volatility indicators · **Application status:** ATR14 computed and used in fixed-at-entry stops

ATR summarizes bar ranges while accounting for gaps from the previous close. It describes movement size, not direction. Larger ATR means a fixed cash-risk budget generally buys fewer shares when stop distance is tied to ATR.

**Calculation or rule:** TR=max(high−low, |high−previous close|, |low−previous close|). Wilder ATR=(13×previous ATR+new TR)/14.

**Hypothetical worked example:** Previous close ₹100, high ₹108 and low ₹104 produce TR=max(4,8,4)=₹8. A 2 ATR stop at ATR=₹3 has ₹6 gross distance.

**How to read it:** The app seeds from the first 14 true ranges, using high−low for the first bar.

**Common mistake:** Calling rising ATR bullish, or treating a 2 ATR stop as a guaranteed maximum loss.

**Further reading:** [Fidelity: ATR](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/atr)

**Implementation reference:** `quant_engine/indicators.py; quant_engine/strategy.py`

## Bollinger Bands

**Category:** Volatility indicators · **Application status:** Bollinger20 computed; optional chart overlay

Bands surround a moving average with a multiple of rolling standard deviation. They describe relative dispersion around that average. Bandwidth contraction can describe quieter recent prices without determining the direction of the next move.

**Calculation or rule:** Middle=SMA20; upper/lower=middle±2×rolling standard deviation. This app uses population standard deviation (ddof=0).

**Hypothetical worked example:** Middle ₹100 and standard deviation ₹2 give bands ₹96 and ₹104.

**Common mistake:** Treating an upper-band touch as an automatic short or assuming a normal-distribution coverage guarantee.

**Implementation reference:** `quant_engine/indicators.py`

## Relative volume (RVOL)

**Category:** Volume indicators · **Application status:** Daily prior-20 RVOL computed; time-of-day baseline pending

Relative volume compares observed volume with a specified historical baseline. The baseline must match timeframe and session position. This daily app uses the mean of the preceding 20 daily volumes, excluding today's bar from the denominator.

**Calculation or rule:** Daily RVOL=today volume / mean(previous 20 daily volumes).

**Hypothetical worked example:** 300,000 shares versus a previous-20 mean of 200,000 gives 1.5×.

**Common mistake:** Comparing the first five minutes of a session with average full-day volume, or interpreting volume alone as net buying.

**Implementation reference:** `quant_engine/indicators.py`

## OBV — On-Balance Volume

**Category:** Volume indicators · **Application status:** OBV computed; contextual divergence rules pending

OBV cumulatively adds a bar's volume when its close rises, subtracts it when its close falls, and leaves it unchanged for an equal close. It is a signed-volume proxy, not a measurement of which investors accumulated shares.

**Hypothetical worked example:** Starting OBV=0: an up-close bar with V100 followed by a down-close bar with V40 yields OBV60.

**Common mistake:** Calling OBV proof of institutional accumulation or comparing arbitrary starting levels across datasets.

**Implementation reference:** `quant_engine/indicators.py`

## Doji

**Category:** Candlestick patterns · **Application status:** Geometry detected; context/research extensions pending

A doji has a small body relative to its full high-low range. It says open and close were close together, while the shadows describe excursions. Trend and location are needed before giving the shape a directional interpretation.

**Calculation or rule:** Prototype rule: positive range and |close−open| ≤ 10% of range.

**Hypothetical worked example:** O100, H105, L95, C100.5 has body0.5 and range10, so it qualifies under the prototype's tolerance.

**Common mistake:** Claiming a doji necessarily predicts a reversal.

**Implementation reference:** `quant_engine/patterns.py`

## Bullish and bearish engulfing

**Category:** Candlestick patterns · **Application status:** Both body-geometry observations detected; contextual validation pending

An engulfing observation has an opposite-color body that covers the prior candle's body. Body coverage does not require the entire high-low range to be covered. The traditional bullish/bearish interpretation depends on preceding movement and confirmation rules.

**Hypothetical worked example:** Prior O105,C101; next O100,C106: the new bullish body covers the old bearish body. This alone does not define an executable trade.

**Common mistake:** Confusing body engulfment with range engulfment, or ignoring that the second bar must close before a close-based signal is known.

**Implementation reference:** `quant_engine/patterns.py`

## Evening Star

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

A traditional three-candle bearish reversal candidate after an uptrend: a substantial bullish body, a small body near the top, then a bearish body moving back into the first body. Gap requirements and penetration thresholds vary across definitions and must be specified before coding.

**Calculation or rule:** Implemented variant: preceding five-bar rise >=1 prior ATR; bullish first body >=0.5 ATR; middle body <=30% of first near its upper half; bearish third body >=50% of first closing below first midpoint. Gaps are not required. Detection waits for the third close.

**Hypothetical worked example:** After an illustrative rise: candle1 O104,C110; candle2 O110.5,C111; candle3 O110.5,C106. The first midpoint is107; third close106 is below it. Use the lab to inspect the geometry.

**How to read it:** It is a hypothesis of weakening buying pressure, not proof of future decline. The current application does not permit overnight short-stock execution.

**Common mistake:** Calling any three candles an Evening Star without prior trend, or assuming a source's entry convention is this simulator's rule.

**Further reading:** [Zerodha Varsity: Morning and Evening Star](https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/)

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Morning Star

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

The traditional bullish counterpart to Evening Star: declining context, a substantial bearish body, a small middle body near the low, then a bullish body recovering into the first body. Precise gaps and penetration need a declared convention.

**Common mistake:** Describing the completed pattern before the third candle has closed.

**Further reading:** [Zerodha Varsity: Morning and Evening Star](https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/)

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Double top, double bottom and neckline

**Category:** Chart patterns · **Application status:** Prototype geometry/state events implemented; predictive validation pending

A double bottom has two sufficiently similar lows separated by a meaningful rebound; its neckline is the intervening high. A double top reverses that geometry. A developing shape and a neckline-confirmed event are different states.

**Calculation or rule:** Prototype: consecutive same-kind confirmed pivots 5–60 sessions apart, price difference ≤0.75 ATR and recovery ≥1.5 ATR. Confirmation uses a close beyond the neckline by >0.1 ATR.

**Hypothetical worked example:** Lows ₹90 and ₹90.2 with an intervening high ₹105 motivate a potential bottom; it is not confirmed merely because the second low exists.

**Common mistake:** Reporting a historic shape's detection at its second trough when right-hand pivot confirmation came later.

**Implementation reference:** `quant_engine/patterns.py: double_patterns`

## Bullish and bearish divergence

**Category:** Price structure · **Application status:** Delayed confirmed-pivot RSI and MACD divergence observations implemented

Bullish divergence commonly means price makes a lower low while a chosen momentum measure makes a higher low; bearish divergence reverses those comparisons. The paired pivots, tolerance, spacing and confirmation time must be defined.

**Common mistake:** Pairing whichever price and oscillator points make the hindsight chart look persuasive.

**Implementation reference:** `quant_engine/research.py: momentum_analysis`

## Position sizing, risk budget and exposure

**Category:** Risk and execution · **Application status:** Cost-aware whole-share sizing implemented

A risk budget is the intended monetary loss under a specified stop-fill model. Exposure is the position's market value. These are different: risking ₹1,000 does not mean investing only ₹1,000. Whole-share quantity must also respect cash and liquidity constraints.

**Calculation or rule:** Before costs: quantity=floor(capital×risk_fraction/(entry−stop)); this engine uses a cost-aware loss per share plus cash and previous-volume caps.

**Hypothetical worked example:** Capital ₹100,000, risk1%, entry₹200, stop₹195: gross quantity200, exposure₹40,000 and intended stop loss₹1,000 before fees/slippage.

**How to read it:** The lab uses the engine's sizing function and makes the cost assumptions visible.

**Common mistake:** Treating intended stop risk as a guaranteed upper bound when gaps or non-fills are possible.

**Try it yourself:** Raise the entry-to-stop distance without changing capital. Explain why quantity falls.

**Implementation reference:** `quant_engine/strategy.py: size_position`

## R, reward-to-risk and expectancy

**Category:** Risk and execution · **Application status:** Gross/net reference ratio and realized P&L expectancy available

One R is a declared initial risk unit. Gross reward/risk compares target distance with stop distance. Expectancy weights actual gains and losses by their frequencies; a high win rate alone is not sufficient.

**Calculation or rule:** Gross reward/risk=(target−entry)/(entry−stop). Expectancy=p×average_win−(1−p)×average_loss, using compatible net units.

**Hypothetical worked example:** A hypothetical 40% win rate, ₹200 average win and ₹100 average loss gives ₹20 average profit before any omitted costs. A nominal2R target is not proof of those realized averages.

**Common mistake:** Choosing a distant target to make a ratio attractive without testing whether it is reached.

## Basis points, charges, spread and slippage

**Category:** Risk and execution · **Application status:** Blended fees/slippage modeled; detailed Indian schedule pending

One basis point is 0.01%. Charges are monetary deductions; spread is the bid-ask difference; slippage is execution differing from a reference quote. These can vary with side, order type, size and market conditions.

**Calculation or rule:** bps/10,000 converts to a rate. Apply entry and exit charges to their respective notionals.

**Hypothetical worked example:** 10bps on ₹40,000 is ₹40 on that side. This prototype uses an illustrative blended rate per side, not an authoritative Indian statutory schedule.

**Common mistake:** Deducting costs only on entry, or assuming historical bar volume guarantees an immediate fill.

## Gap risk and same-bar ambiguity

**Category:** Risk and execution · **Application status:** Gap handling and stop-first ambiguity implemented

An opening gap can jump past a stop. A daily candle that touches both stop and target usually does not reveal which came first. A simulator must disclose how it resolves that uncertainty.

**Hypothetical worked example:** Entry₹100, stop₹95, next open₹90: assuming an exit at₹95 overstates protection. If high₹111 and low₹94 touch a₹110 target and₹95 stop, daily OHLC cannot order those touches.

**How to read it:** This engine uses the open for gap-through-stop exits and the stop first for ambiguous bars, then applies exit slippage and fees.

**Common mistake:** Claiming the simulator's conservative convention is the market's actual intraday sequence.

**Implementation reference:** `quant_engine/strategy.py: backtest`

## Backtest versus paper trading versus live trading

**Category:** Research and statistics · **Application status:** Exploratory historical baseline implemented; paper/live not implemented

A backtest simulates rules on historical data. Paper trading records decisions prospectively without real orders. Live trading adds real money, operational failures and actual fills. Software correctness does not establish a profitable strategy.

**Hypothetical worked example:** The same frozen breakout rule can be tested historically, then observed on future sessions without changing its rules after losses.

**Common mistake:** Calling performance on the same data used to design the strategy an untouched test.

## Equity, drawdown and maximum drawdown

**Category:** Research and statistics · **Application status:** Liquidation-cost marked equity and drawdown implemented

Equity includes cash plus the current value of open positions under a defined valuation convention. Drawdown is the percentage below the running peak; maximum drawdown is the worst observed decline from a prior peak, not a prediction of the worst future loss.

**Calculation or rule:** drawdown=equity/running_peak−1.

**Hypothetical worked example:** Equity100,000→110,000→99,000 has a−10% drawdown from110,000, even though it is only−1% from initial capital.

**Common mistake:** Using only closed-trade balances and ignoring losses while positions remain open.

## Look-ahead bias and data leakage

**Category:** Research and statistics · **Application status:** Starter indicator/pivot/signal invariance tests present; all future modules need their own checks

Leakage uses information unavailable at the decision time. It can enter through future prices, a weekly close known later, full-dataset normalization, revised data, or pivot confirmation. Preventing it requires availability times, not just sorting dates.

**Hypothetical worked example:** Training a scaler on the entire dataset before splitting leaks later distribution information into earlier training.

**Common mistake:** Assuming every feature is causal simply because a train/test split is chronological.

## Overfitting, multiple testing and validation

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Overfitting means a rule captures peculiarities of a sample rather than a robust relationship. Searching many configurations and presenting only the best hides selection. Chronological validation, recorded experiment counts and prospective tests help assess this risk, but do not guarantee future performance.

**Hypothetical worked example:** If you try 200 indicator combinations, the best historical curve has benefited from selection; it needs a genuinely new evaluation protocol.

**Common mistake:** Repeatedly checking the test period and still calling it untouched.

**Further reading:** [Bailey et al.: Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)

## Probability, heuristic score and calibration

**Category:** Research and statistics · **Application status:** No calibrated probability is produced in the prototype

A heuristic score summarizes rule satisfaction. A probability estimates how often a defined outcome occurs conditional on information. Calibration asks whether outcomes occur about as frequently as the stated probabilities across suitable future cases.

**Hypothetical worked example:** A geometric score80/100 does not imply an80% target-hit probability. For predictions near0.7, calibration asks whether about70% of comparable evaluated events realize the precisely defined outcome.

**Common mistake:** Displaying an arbitrary weighted indicator score with a percent sign as a win probability.

## Long, short and swing trading

**Category:** Foundations · **Application status:** Explained; engine extension pending

A long position gains when its exit value exceeds its entry cost; a short gains from a price decline but requires a permitted instrument/borrowing mechanism. Swing trading holds across sessions. The prototype is long-only; short examples are educational, not authorization to short Indian cash equities overnight.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Liquidity and turnover

**Category:** Foundations · **Application status:** Explained; engine extension pending

Liquidity is the ability to transact a given size with limited delay and price impact. Volume/turnover are activity measures, not complete liquidity measurements; spread, depth, circuits and order size also matter.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Market, limit, stop and stop-limit orders

**Category:** Foundations · **Application status:** Explained; engine extension pending

A market order prioritizes execution over a specified price; a limit constrains price but can remain unfilled; a stop activates after a trigger; a stop-limit then behaves as a limit. A simulated stop is not guaranteed protection.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Relative strength versus RSI

**Category:** Foundations · **Application status:** Two-stock indexed performance ratio; sector/benchmark research pending

Relative strength compares performance with another asset or benchmark, such as stock return minus sector return. RSI instead summarizes the stock's own recent gains and losses. Similar names do not make them interchangeable.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/comparison.py`

## WMA — Weighted Moving Average

**Category:** Trend indicators · **Application status:** Explained; engine extension pending

A moving average using explicit weights, often larger weights for newer observations. The weights must sum to one after normalization; more responsiveness does not imply better prediction.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## ADX and directional movement

**Category:** Trend indicators · **Application status:** Explained; engine extension pending

ADX smooths a normalized measure of directional-movement imbalance to describe trend strength. It does not by itself specify bullish versus bearish direction; +DI and −DI supply additional directional comparisons.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Parabolic SAR

**Category:** Trend indicators · **Application status:** Explained; engine extension pending

A recursive trailing reference built from extreme prices and an acceleration factor, with direction-switch rules. Specify initialization and bar-level reversal handling before testing it as an exit.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Supertrend

**Category:** Trend indicators · **Application status:** Explained; engine extension pending

A trend overlay based on ATR-related bands and state-dependent trailing/flip rules. Implementations differ in band persistence and initialization, so the precise variant matters.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Stochastic oscillator

**Category:** Momentum indicators · **Application status:** Fast %K14 and three-observation %D; zero range undefined

Compares the close with the recent high-low range: raw %K=100×(close−lowest_low)/(highest_high−lowest_low). Smoothing produces %K/%D variants; a zero range needs a declared policy.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/indicators.py`

## Stochastic RSI

**Category:** Momentum indicators · **Application status:** Explained; engine extension pending

Places RSI within its own recent minimum-to-maximum range, rather than placing price within a price range. It can react sharply; matching timeframe and smoothing conventions is essential.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## ROC — Rate of Change

**Category:** Momentum indicators · **Application status:** Ten-observation price ROC computed

Measures relative price change over N observations, commonly100×(close/close_N_ago−1). Unlike RSI, it is not bounded between0 and100.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/indicators.py`

## Williams %R

**Category:** Momentum indicators · **Application status:** Explained; engine extension pending

Measures where the close lies relative to a recent high-low range, commonly−100×(highest_high−close)/(highest_high−lowest_low). It is closely related to unsmoothed stochastic positioning.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## CCI — Commodity Channel Index

**Category:** Momentum indicators · **Application status:** Explained; engine extension pending

Compares typical price with its moving average, scaled by mean absolute deviation and a conventional factor. Despite its name it can be applied beyond commodities; its scale is not a probability.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Historical volatility

**Category:** Volatility indicators · **Application status:** Explained; engine extension pending

The dispersion of observed returns over a stated window. Annualization multiplies interval volatility by the square root of an assumed periods-per-year count; that scaling relies on assumptions and says nothing about direction.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Donchian channel

**Category:** Volatility indicators · **Application status:** Explained; engine extension pending

Upper/lower boundaries are rolling highest high and lowest low. For breakout testing, compare today's close with a channel based on prior bars, excluding the current high/low from its own trigger.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Keltner channel

**Category:** Volatility indicators · **Application status:** Explained; engine extension pending

A moving-average center with range/ATR-based envelopes under a specified variant. Its difference from standard-deviation bands can motivate a squeeze hypothesis, not a proven edge.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Volatility squeeze and expansion

**Category:** Volatility indicators · **Application status:** Explained; engine extension pending

A squeeze is a predeclared low-volatility condition, often using bandwidth or relative envelopes. Expansion means movement size grows; neither condition establishes the direction or profitability of a future trade.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## VWAP and anchored VWAP

**Category:** Volume indicators · **Application status:** Explained; engine extension pending

Volume-weighted average price is sum(price×volume)/sum(volume) over a stated anchor/session. Bar typical-price approximations differ from trade-level VWAP; an anchor must not be chosen with hindsight.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Accumulation/Distribution line

**Category:** Volume indicators · **Application status:** Explained; engine extension pending

Cumulatively weights volume by the close's position within each bar's range. It is a location-weighted volume proxy, not verified investor accumulation or delivery data.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Chaikin Money Flow

**Category:** Volume indicators · **Application status:** Explained; engine extension pending

Normalizes a rolling sum of close-location-weighted volume by rolling volume. Zero ranges and volume need an explicit convention; a positive value is not a measured net inflow of cash.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Money Flow Index

**Category:** Volume indicators · **Application status:** Explained; engine extension pending

An oscillator comparing positive and negative typical-price×volume flows across a window. Its name does not mean it measures actual deposits, ownership or institutional money.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Delivery quantity and delivery percentage

**Category:** Volume indicators · **Application status:** Explained; engine extension pending

Exchange-reported delivery-related quantities describe a different facet of activity than traded volume. Use the provider's exact definition, publication time and units; they do not identify investors or prove accumulation.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Triple bottom

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Three comparable troughs separated by rebounds, under explicit spacing/tolerance rules. A prospective neckline break and invalidation define separate states; three lows alone do not establish success.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Triple top

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Three comparable peaks separated by pullbacks. Define the lower boundary and when a break becomes knowable before assigning confirmation.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Head and shoulders

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Three swing peaks with a higher central head and two lower shoulders, separated by troughs defining a neckline. Symmetry, prominence, prior trend and neckline-break rules must be stated.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Inverse head and shoulders

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Three swing troughs with a deeper central head and higher shoulders. The intervening peaks define a neckline; a visible resemblance is not a validated reversal.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Rounding bottom

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A gradually flattening decline transitioning toward rising prices. Curvature, duration, scale and confirmation must be quantified rather than judged only by a U-shaped drawing.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Rounding top

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A gradually slowing advance transitioning toward declining prices. Its apparent curvature depends on chart scaling and needs a reproducible definition.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Broadening formation

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A sequence with expanding boundaries, often higher highs and lower lows. Specify minimum alternating pivots and boundary slopes; direction is not implied solely by expansion.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bullish flag

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A brief bounded consolidation following an upward impulse. A detector needs separate impulse, countertrend/channel, duration, breakout and invalidation rules.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bearish flag

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A brief bounded consolidation after a downward impulse, often drifting upward. Its traditional continuation interpretation remains a hypothesis to evaluate.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bullish pennant

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

An upward impulse followed by a small converging consolidation. Distinguish it from a large standalone triangle and predeclare the eligible breakout time.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bearish pennant

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A downward impulse followed by a small converging consolidation. Specify boundaries and expiry instead of waiting indefinitely for the desired breakdown.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Ascending triangle

**Category:** Chart patterns · **Application status:** Frozen confirmed-anchor geometry and break/expiry states implemented; statistical validation pending

Rising swing lows beneath approximately flat upper highs. Tolerances, minimum interactions and breakout criteria determine whether it qualifies; the name does not guarantee an upward break.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: chart_formations`

## Descending triangle

**Category:** Chart patterns · **Application status:** Frozen confirmed-anchor geometry and break/expiry states implemented; statistical validation pending

Falling swing highs above approximately flat lower lows. A lower-boundary breach is a separate event from a developing shape.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: chart_formations`

## Symmetrical triangle

**Category:** Chart patterns · **Application status:** Frozen confirmed-anchor geometry and break/expiry states implemented; statistical validation pending

Descending highs and ascending lows form converging boundaries. Boundary fitting must use only confirmed available anchors; either breakout direction is possible.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: chart_formations`

## Rising wedge

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Both boundaries slope upward while converging. The traditional weakening/reversal interpretation depends on context and must be tested against a precise definition.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Falling wedge

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Both boundaries slope downward while converging. A developing wedge is not the same event as an upward boundary break.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Rectangle consolidation

**Category:** Chart patterns · **Application status:** Frozen confirmed-anchor geometry and break/expiry states implemented; statistical validation pending

Repeated interactions with approximately horizontal upper and lower boundaries. Define width, minimum duration and independent interactions; bounded history does not guarantee a tradable range.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: chart_formations`

## Price channel

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Price oscillates between approximately parallel boundaries. Slopes, anchor selection and tolerance must be stated, especially when using a channel for projected support or targets.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Cup and handle

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

A rounded recovery toward a prior area followed by a smaller consolidation or pullback. Depth, duration, handle position and confirmation are necessary geometric constraints.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Inverse cup and handle

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

An inverted rounded structure followed by a smaller consolidation. The boundaries and prospective breakdown must be specified rather than selected after the decline.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Measured-move target

**Category:** Chart patterns · **Application status:** Explained; engine extension pending

Projects a predeclared pattern dimension from a breakout area, such as bottom-to-neckline height. It is a geometric reference, not an expected value or a guaranteed target.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Dragonfly Doji

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A near-zero body toward the high of the candle with a pronounced lower shadow. Prior trend and location matter; geometry alone does not prove rejection will persist.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Gravestone Doji

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A near-zero body toward the low with a pronounced upper shadow. Define small-body and shadow thresholds rather than requiring visually perfect equality.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Long-Legged Doji

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A small body with substantial excursions on both sides. It describes an interval of movement with little open-to-close change, not a guaranteed directional reversal.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Hammer

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

A small body near the upper range with a long lower shadow, interpreted as a bullish-reversal candidate only in appropriate declining context. Exact shadow/body ratios are configurable conventions.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Hanging Man

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

Hammer-like geometry in an advancing context. Its different traditional interpretation illustrates why shape and preceding trend must be separate parts of detection.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Inverted Hammer

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

A small body near the lower range with a long upper shadow following a decline. It needs context/confirmation rather than inheriting a bullish label from shape alone.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Shooting Star

**Category:** Candlestick patterns · **Application status:** Contextual detector implemented; statistical validation pending

Inverted-hammer-like geometry after an advance. A long upper shadow can motivate a rejection hypothesis, but it does not reveal investor identity or guarantee a fall.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/research.py: contextual_candles`

## Bullish Marubozu

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A substantial bullish body with little shadow under a declared tolerance. Open near low and close near high describes that bar, not certainty of continuation.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bearish Marubozu

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A substantial bearish body with little shadow. Use relative thresholds appropriate to price scale and tick size rather than exact arithmetic equalities.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Spinning Top

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A small real body with upper and lower shadows. It describes limited net change relative to excursions; a preceding trend and location are needed for a directional hypothesis.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Piercing Pattern

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A declining-context two-bar candidate where a bearish body is followed by a bullish recovery deep into that body, commonly beyond its midpoint. Gap and recovery thresholds need a declared variant.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Dark Cloud Cover

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

An advancing-context two-bar candidate where a bullish body is followed by a bearish penetration into it, commonly beyond its midpoint. Define the open-gap and penetration convention explicitly.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bullish Harami

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A smaller body inside a preceding larger bearish body, traditionally considered in declining context. Body containment differs from full-range containment.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bearish Harami

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A smaller body inside a preceding larger bullish body, traditionally considered in advancing context. It does not require the entire candle range to fit inside.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Tweezer Bottom

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

Adjacent or nearby candles interact with sufficiently similar lows under a declared tolerance. Specify candle count, preceding trend and how independent the interactions are.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Tweezer Top

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

Adjacent or nearby candles interact with sufficiently similar highs. Similarity should be defined relative to tick size or volatility rather than an arbitrary universal currency difference.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bullish Kicking

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A strong bearish candle followed by a bullish candle separated by an upward gap under a strict variant, often using near-marubozu bodies. Rare patterns require especially cautious sample-size claims.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bearish Kicking

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

The bearish counterpart with a strong bullish candle followed by a downward-gapped bearish candle. Body and gap definitions materially affect event counts.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Morning Doji Star

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A Morning Star variant whose middle candle qualifies as a doji under stated tolerances. The third candle and prior downtrend remain part of the full definition.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Evening Doji Star

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

An Evening Star variant with a doji middle candle. Calling it more reliable than another pattern requires comparable historical evidence, not its name.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three White Soldiers

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

Three successive substantial bullish bodies with rising closes, under explicit open/body/wick constraints. Distinguish healthy progression from unusually extended prices near an obstacle.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three Black Crows

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

Three successive substantial bearish bodies with falling closes and specified opening/wick conditions. Declining closes alone are too loose a complete definition.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three Inside Up

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A bullish-harami-style initial pair followed by a confirming bullish third bar under a specified close condition. State the third-bar requirement before testing.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three Inside Down

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A bearish-harami-style initial pair followed by a confirming bearish third bar. The detector becomes knowable only when all required bar conditions are observed.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three Outside Up

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A bullish engulfing-style pair followed by a higher confirming third close under the chosen variant. It is a separate event from the two-bar engulfing observation.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Three Outside Down

**Category:** Candlestick patterns · **Application status:** Explained; engine extension pending

A bearish engulfing-style pair followed by a lower confirming third close. Event overlap must be considered when counting historical independent opportunities.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Win rate and profit factor

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Win rate is the fraction of evaluated completed trades with positive net P&L. Profit factor is total positive P&L divided by absolute negative P&L. Both need sample size and conventions for break-even/open trades; neither is a calibrated forecast.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Sharpe, Sortino and Calmar

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Sharpe scales mean excess return by return volatility; Sortino uses a defined downside-deviation measure; Calmar compares annualized return with drawdown magnitude. Frequency, horizon, risk-free rate and annualization conventions matter.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## MFE and MAE

**Category:** Research and statistics · **Application status:** Complete-horizon event MFE/signed MAE computed; order execution remains separate

Maximum favorable/adverse excursion measures the best/worst observed movement during a defined trade/event interval relative to an entry/reference. The units, long/short direction and intrabar ambiguity must be explicit.

**Calculation or rule:** Use only complete post-detection windows t+1…t+h. Upward MFE=max(0,max(high)/reference−1), signed MAE=min(0,min(low)/reference−1). Bearish MFE=max(0,1−min(low)/reference), signed MAE=min(0,1−max(high)/reference).

**Hypothetical worked example:** Invented reference100, later maximum high108 and minimum low95 give upward MFE8% and signed MAE−5%; bearish MFE5% and signed MAE−8%. Daily OHLC cannot reveal which extreme occurred first.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/event_study.py`

## Survivorship bias

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Researching only today's surviving stocks excludes historical failures, delistings or removed index constituents. A credible universe needs time-specific membership and security histories.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Walk-forward evaluation

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Repeatedly train or choose rules on earlier periods and evaluate on the next eligible period. The retraining schedule and selection rules must be fixed before using the combined forward results.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Purging, embargo and overlapping labels

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

An outcome label can span future bars. Overlapping outcome intervals across split boundaries can contaminate evaluation. Purging removes intersecting training events; embargo adds a declared temporal separation. The exact scheme depends on label horizons.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Brier score and log loss

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

Brier score averages squared probability errors; log loss penalizes confident incorrect probability assignments. Both require correctly defined outcomes and held-out predictions; neither directly measures after-cost profitability.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Precision, recall, F1, ROC-AUC and PR-AUC

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

These assess classification/ranking under particular thresholds or across thresholds. Class balance and economic payoffs matter: high classification performance does not by itself imply a useful trading strategy.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Censoring and maximum holding horizon

**Category:** Research and statistics · **Application status:** Per-horizon event censoring and audited raw-action exclusions implemented

If the outcome horizon extends beyond available data, the outcome may be unknown rather than a failure. Expiry, neither-barrier-hit and forced end-of-data close need distinct documented labels.

**Calculation or rule:** A horizon extending beyond replay remains Incomplete horizon. Its return/MFE/MAE are null and it is omitted from averages, never converted to a loss or closed early. Complete raw-price windows crossing a known audited action are separately excluded.

**Hypothetical worked example:** An invented setup known two observations before the replay cutoff has a complete1-observation outcome and an incomplete5-observation outcome. These horizons have different complete counts.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Implementation reference:** `quant_engine/event_study.py`

## Market regime and concept drift

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

A regime is a declared grouping of market conditions, such as volatility/trend context. Drift means relationships or distributions change. Regime labels chosen using future outcomes can themselves leak information.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Benchmark, ablation and opportunity cost

**Category:** Research and statistics · **Application status:** Explained; engine extension pending

A benchmark is the comparison a strategy must justify its complexity against. Ablation removes one component to estimate its incremental contribution. Use comparable costs, exposure, universe and evaluation dates where appropriate.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Logistic regression, random forest and boosted trees

**Category:** AI and software · **Application status:** Explained; engine extension pending

Logistic regression is a useful interpretable probability baseline; forests average trees; boosted trees build sequential corrections. More complexity must justify itself on suitable unseen data, calibration and net economic outcomes.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Data provenance, run ID and reproducibility

**Category:** AI and software · **Application status:** Explained; engine extension pending

A reproducible run records data version/hash, source, adjustment policy, parameters, code/model version and decision time. A source hash identifies bytes; it does not prove those bytes are accurate.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## LLM narration versus numerical analysis

**Category:** AI and software · **Application status:** Explained; engine extension pending

A language model can explain a validated evidence bundle. It should not manufacture indicator values, price levels or win probabilities. Numeric engines, statistical evaluation and narrative generation remain separate components.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Git, GitHub, commits and continuous integration

**Category:** AI and software · **Application status:** Private repository, verified source upload and passing GitHub CI; local Git authentication is separate

Git records versioned snapshots; GitHub hosts repositories and collaboration. A commit identifies a snapshot/history record. CI runs specified checks remotely. A connected GitHub app and the computer's Git client can have different authentication contexts.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

**Try it yourself:** Open the source commit and its Actions run. Explain how a verified file snapshot differs from a passing test result.

**Implementation reference:** `docs/GITHUB_SYNC.md; .github/workflows/tests.yml`

## Screenshot observations versus structured data

**Category:** AI and software · **Application status:** Explained; engine extension pending

A screenshot shows rendered pixels and may omit axes, scale, timeframe or full history. Qualitative visual observations must be separated from exact computations on verified OHLCV.

**How to read it:** This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.

**Common mistake:** Confusing a traditional interpretation or an educational description with validated predictive performance.

## Bhavcopy and UDiFF daily reports

**Category:** Data quality · **Application status:** Offline CSV/ZIP schema-subset preview tested with synthetic reports; real-file acceptance pending

A daily exchange report contains records for many securities for one session. It is not already one stock's historical price table. UDiFF is a standardized exchange-file format; a matching header does not authenticate a file's origin.

**Calculation or rule:** Select the exact symbol and series across completed daily reports; map TradDt and quoted OHLCV without price repair.

**Hypothetical worked example:** Three invented daily reports each contain ALPHA and BETA. Selecting ALPHA EQ creates three daily bars, not six observations or an average of both stocks.

**Common mistake:** Uploading overlapping reports and silently removing duplicates, or assuming one report supplies months of history.

**Try it yourself:** Select DEMOBETA in the report walkthrough, then explain why its 80 bars came from 80 reports.

**Further reading:** [NSE: daily reports](https://www.nseindia.com/all-reports)

**Implementation reference:** `quant_engine/nse_files.py; tests/test_nse_files.py`

## Symbol, series, ISIN and security continuity

**Category:** Data quality · **Application status:** EQ selection and basic identity-consistency guards; listing-history resolver pending

A ticker is a market label, a series classifies a trading segment, and an ISIN identifies a security. Labels alone do not establish historical continuity through reorganizations or symbol changes.

**Hypothetical worked example:** Invented ALPHA EQ has ISIN ZZ0000000001 on one date and ZZ0000000002 later. This importer stops the combination for review instead of assuming continuity.

**How to read it:** This build checks ISIN structure and one-ISIN consistency, not the check digit, real listing or full corporate history. Only EQ series is imported.

**Try it yourself:** Explain why the synthetic ZZ identifiers passing a format check does not make them actual listed securities.

**Further reading:** [NSE: formats](https://www.nseindia.com/static/resources/forms-formats-members)

**Implementation reference:** `quant_engine/nse_files.py: ReportBundle.select`

## Data passport, source hash and analysis slice

**Category:** AI and software · **Application status:** JSON passport and analyzed-CSV exports; source and replay hashes included in analysis evidence

A data passport records instrument, source claim, raw-file hashes, normalized-data hash, date convention and adjustment declaration. It documents what was used without certifying authenticity or accuracy.

**Calculation or rule:** A dataset ID hashes stable input identity and declarations. Import time is recorded separately. Replaying a subset preserves the source ID and adds a separate analyzed-data hash.

**Hypothetical worked example:** Import 80 invented sessions, replay the first 40. Source rows remain 80, analyzed rows become 40, and the analyzed CSV hash changes while the original dataset ID stays fixed.

**Common mistake:** Treating matching hashes as proof of correct prices or confusing a full-source hash with the exported replay slice.

**Try it yourself:** Download a passport before and after replay. Compare source_rows, analyzed_rows and both normalized hashes.

**Implementation reference:** `quant_engine/datasets.py; quant_engine/data_ui.py`

## NSE stock-history CSV: close, LTP, volume and value

**Category:** Data quality · **Application status:** Automatic NSE security-history CSV/XLSX normalization; supplied real-file workflow checked locally

A security-history download contains one stock over many sessions. CLOSE is the reported closing price, LTP is the last traded price, PREV. CLOSE describes the preceding close, VOLUME is share quantity and VALUE is rupee turnover. These fields are not interchangeable.

**Calculation or rule:** The automatic stock-history adapter uses DATE/OPEN/HIGH/LOW/CLOSE/VOLUME, EQ series only. It converts explicit DD-Mon-YYYY dates and valid Indian or international comma grouping, then applies the usual OHLCV validation.

**Hypothetical worked example:** An invented row has CLOSE 1,240.00, LTP 1,248.00 and VOLUME 23,34,553. The analyzed close is 1240 and the traded quantity is 2334553 shares. VALUE is not substituted for volume.

**How to read it:** Keep the downloaded filename to retain its stock-label hint. The file may not contain a symbol or ISIN, so the filename is a declaration rather than independently verified security identity.

**Common mistake:** Renaming VALUE to volume, treating a missing dash as zero, or assuming formatting conversion also adjusts splits and dividends.

**Try it yourself:** Upload an original NSE stock-history CSV through Upload daily data. Find the detected format and warm-up warning, and explain why CLOSE and LTP can differ.

**Further reading:** [NSE: daily reports](https://www.nseindia.com/all-reports)

**Implementation reference:** `quant_engine/nse_quotes.py; quant_engine/data.py; tests/test_nse_quotes.py`

## Return correlation and matched intervals

**Category:** Research and statistics · **Application status:** Two-stock Pearson/Spearman return and rolling-correlation workspace

Pearson correlation describes linear co-movement between two return samples, from minus one to plus one. Stock price levels can trend together without providing a useful return relationship. Correlation is not causation, cointegration or a pairs-trading rule.

**Calculation or rule:** Compute each stock's simple returns on its native observation intervals. Pair only matching start and end dates; never forward-fill missing prices. The UI requires ten paired intervals for a coefficient and uses a configurable rolling count of pairs.

**Hypothetical worked example:** If A's Tuesday return starts Monday but B's Tuesday return starts Friday because Monday is absent, those returns are excluded from the paired sample. Two constant return series have undefined correlation, not zero.

**How to read it:** The coefficient depends on period, data basis and sample size. A short sample can be unstable. Spearman compares ranks; this build rounds returns to 12 decimals before ranking to stabilize numerical ties.

**Implementation reference:** `quant_engine/comparison.py; quant_engine/comparison_ui.py`

## Indexed performance and observed-date drawdown

**Category:** Research and statistics · **Application status:** Indexed two-stock performance, relative ratio and common-observation drawdowns

Rebasing two price series to 100 at a common starting observation makes their proportional price changes comparable. Drawdown is current indexed value divided by the maximum so far minus one.

**Hypothetical worked example:** A rises from index100 to110 then falls to88: its observed-date drawdown is 88/110−1=−20%. If B stays at100, A/B relative performance is0.88 at the final point.

**How to read it:** This comparison uses price returns, not dividend-inclusive total returns. Drawdowns use common observed dates and can miss extremes hidden by absent observations; return volatility is per matched interval, without annualization.

**Implementation reference:** `quant_engine/comparison.py`

## Forward outcomes and measurement timing

**Category:** Research and statistics · **Application status:** Versioned causal forward-outcome research workspace

A forward outcome measures price movement after an observation became knowable. Its reference price and horizon must be declared before interpreting the result. Formation time can precede the first moment the complete pattern was detectable.

**Calculation or rule:** For a pattern known at observation t, the default reference is open[t+1]. Horizon h ends at close[t+h]. The alternative reference is close[t]; it is an observational convention, not an available trading fill. Horizons count uploaded observations.

**Hypothetical worked example:** Invented example: a setup is known Monday, the next observed open is100, and the close at t+5 is104. The gross five-observation movement is104/100−1=4%. A 1-observation next-open result is the next bar's open-to-close change.

**How to read it:** Pattern-direction mode negates returns for bearish events. This makes favourable falls positive without simulating short selling, costs or share accounting. Neutral shapes use upward-price mode.

**Common mistake:** Measuring from a pivot's formation price, including the detection candle's extreme, or treating gross price movement as realized trading profit.

**Further reading:** [CFA Institute: Backtesting and Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation)

**Implementation reference:** `quant_engine/event_study.py`

## Matched non-event baseline and coverage

**Category:** Research and statistics · **Application status:** Auditable context-matched baseline pools and coverage counts implemented

A conditional baseline asks what happened on other dates with similar observable conditions. It gives context to a selected historical sample but does not by itself identify what would have happened without the pattern or establish a causal effect.

**Calculation or rule:** Match the same uploaded stock and date interval on close versus EMA50 and relative-volume bucket at the decision close. A baseline anchor has no selected eligible event that day; future events remain allowed. Compare each event with its matching pool's mean, then average those differences across covered events.

**Hypothetical worked example:** Invented example: two covered event returns are6% and−2%; their context-pool means are2% and1%. The event mean is2%, the event-weighted baseline is1.5%, and the difference is0.5 percentage points. An event lacking enough controls is omitted from both matched means.

**How to read it:** Controls are reused across events and may overlap their outcomes. This retrospective baseline uses the selected historical interval, including later dates. It is not an earlier-only forecast or the market-model abnormal return used in formal financial event studies.

**Common mistake:** Comparing a full-cohort event mean with a baseline covering only some events, or dropping controls because a future pattern occurred.

**Further reading:** [EventStudyTools: Introduction to event studies](https://www.eventstudytools.com/introduction-event-study-methodology)

**Implementation reference:** `quant_engine/event_study.py`

## Overlapping event windows and sample dependence

**Category:** Research and statistics · **Application status:** Deterministic cohort/context-pool spacing with retained exclusion ledger

Two signals can share the same future price path, so counting them separately can exaggerate the apparent amount of evidence. Distinct pattern names can also identify closely related observations.

**Calculation or rule:** Default thinning keeps the earliest occurrence within each event type/state and requires the next knowledge index to exceed the previous index plus the largest selected horizon. Apply this before checking outcome completeness. Baseline anchors are separately thinned within each context pool.

**Hypothetical worked example:** Invented knowledge indices1,2,4,5 with maximum horizon3 retain1 and5. Index4 is rejected because the closed windows share an endpoint. A different event type at index2 can remain and is not independent evidence.

**How to read it:** Thinning reduces direct window reuse; it does not remove market dependence, cross-cohort overlap or shared controls. Naive independent-sample confidence intervals would overstate precision.

**Implementation reference:** `quant_engine/event_study.py`

## Outcome distribution versus statistical uncertainty

**Category:** Research and statistics · **Application status:** Descriptive outcome distributions and small-sample labels implemented

Mean, median, quartiles and the fraction of positive observations summarize an observed distribution. A confidence interval concerns uncertainty about an estimated population quantity under stated sampling assumptions; these are different objects.

**Calculation or rule:** Show complete outcome counts, mean/median, 25th/75th percentiles, signed excursions and positive fraction. Zero is |movement|<=1e−12; positive means movement>1e−12. No complete outcomes means unavailable metrics. Counts below5 and30 receive descriptive caution labels, not statistical-validity guarantees.

**Hypothetical worked example:** Invented outcomes−2%,0%,4% have mean0.6667%, median0%, a positive fraction of1/3, and one flat result. These three observations do not establish a one-third future success probability.

**How to read it:** The current workspace supplies descriptive dispersion and sample warnings. Dependent-data uncertainty, multiple-testing correction and held-out predictive validation remain future work.

**Common mistake:** Calling a box plot a confidence interval or a historical positive fraction a calibrated forecast.

**Further reading:** [CFA Institute: Backtesting and Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation)

**Implementation reference:** `quant_engine/event_study.py; quant_engine/event_study_ui.py`
