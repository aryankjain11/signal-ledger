"""Original learning notes shared by the application and exported handbook.

Definitions describe conventions, not validated predictive power. All numeric
examples are hypothetical. 'Explained' and 'computed/detected' are separate states.
"""

FIDELITY = "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/"
SOURCES = {
    "nse-reports": ("NSE: daily reports", "https://www.nseindia.com/all-reports"),
    "nse-formats": ("NSE: formats", "https://www.nseindia.com/static/resources/forms-formats-members"),
    "rsi": ("Fidelity: RSI", FIDELITY + "RSI"),
    "macd": ("Fidelity: MACD", FIDELITY + "macd"),
    "atr": ("Fidelity: ATR", FIDELITY + "atr"),
    "star": ("Zerodha Varsity: Morning and Evening Star", "https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/"),
    "ta": ("Fidelity: technical analysis introduction", "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/what-is-technical-analysis"),
    "overfit": ("Bailey et al.: Probability of Backtest Overfitting", "https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf"),
    "research-bias": ("CFA Institute: Backtesting and Simulation", "https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation"),
    "event-method": ("EventStudyTools: Introduction to event studies", "https://www.eventstudytools.com/introduction-event-study-methodology"),
    "nse": ("NSE: corporate actions", "https://www.nseindia.com/companies-listing/corporate-filings-actions"),
}

CONCEPTS = []


def add(key, title, category, definition, rule="", example="", interpretation="", mistake="",
        status="Explained; engine extension pending", source=None, code="", exercise=""):
    CONCEPTS.append({"id": key, "title": title, "category": category, "definition": definition,
                     "rule": rule, "example": example, "interpretation": interpretation,
                     "mistake": mistake, "app_status": status, "source": source,
                     "code": code, "exercise": exercise})


add("ohlcv", "OHLCV and the anatomy of a candle", "Foundations",
    "One bar summarizes one interval: open is its first traded price, high/low are its extremes, close is its last price, and volume is traded quantity. The body spans open to close; shadows extend to high and low. A daily candle hides the sequence of trades inside that day.",
    "Body = |close − open|; range = high − low; upper shadow = high − max(open,close); lower shadow = min(open,close) − low.",
    "Open ₹100, high ₹108, low ₹98, close ₹105: body ₹5, upper shadow ₹3, lower shadow ₹2, range ₹10. Volume 50,000 means shares traded in this example, not 50,000 unique investors.",
    "A green candle says close exceeded open; it can still close below yesterday's close.",
    "Inferring whether the high or low occurred first from daily OHLC alone.",
    "Validated and charted", "ta", "quant_engine/data.py; quant_engine/charts.py",
    "Draw the candle for O=105, H=109, L=99, C=101. Explain what cannot be known from it.")
add("timeframe", "Timeframe, session and resampling", "Foundations",
    "A timeframe is the interval represented by a bar. An exchange session is a trading period, not necessarily a whole calendar day. Weekly OHLCV must be built from eligible daily bars, with clear handling of incomplete weeks.",
    "Aggregate open=first, high=max, low=min, close=last, volume=sum.",
    "Two bars (O100,H105,L99,C104,V10) and (O104,H108,L102,C103,V20) aggregate to O100,H108,L99,C103,V30.",
    "Higher-timeframe context becomes usable only after its required information is available.",
    "Using Friday's completed weekly close to explain a trade made on Monday of that same week.",
    "Daily plus conservative completed-prior-week context", code="quant_engine/data.py: completed_weeks")
add("price-return", "Price, simple return and total return", "Foundations",
    "Price is a currency amount per share. Simple return measures relative change. Total return also includes distributions under a defined reinvestment convention; it cannot be inferred from an unadjusted closing-price ratio alone.",
    "Simple price return = new_price / old_price − 1.",
    "₹200 to ₹210 is +5%. A ₹4 dividend requires separate treatment when measuring total return.",
    mistake="Treating a 2-for-1 split as a 50% economic loss.", status="Price-return comparison available; total-return engine pending")
add("adjustments", "Corporate actions and adjusted prices", "Data quality",
    "Splits, bonus issues, dividends and reorganizations can change the meaning of historical prices. A consistent adjustment policy preserves comparability. Price and share-volume transformations must agree with the event type; dividend adjustment is different from split adjustment.",
    example="In a hypothetical 2-for-1 split, ₹200 with one share becomes about ₹100 with two shares before other market movement. Splits alone do not halve portfolio value.",
    interpretation="Keep the raw series, event record, adjusted series, method and version. Back-adjustment can revise old numbers, so research needs a point-in-time policy.",
    mistake="Combining adjusted close with unadjusted open/high/low, or assuming every sharp move is a split.",
    status="Reviewed split/bonus ledger and replay-aware OHLCV research normalization; dividend/total-return and execution accounting pending", source="nse",
    code="quant_engine/corporate_actions.py; quant_engine/actions_ui.py")
add("trend", "Trend and market structure: HH, HL, LH, LL", "Price structure",
    "Higher high (HH) and higher low (HL) mean successive meaningful highs and lows are rising. Lower high (LH) and lower low (LL) mean they are falling. Mixed sequences need a mixed/range interpretation rather than a forced direction.",
    example="Confirmed highs 100→110 and lows 90→96 give HH+HL. Highs 110→104 with lows 96→92 give LH+LL.",
    mistake="Using an unconfirmed final swing as if it were already knowable.",
    status="Basic confirmed-pivot structure implemented", code="quant_engine/patterns.py: market_structure")
add("pivot", "Swing pivot, confirmation delay and repainting", "Price structure",
    "A local swing high exceeds nearby highs; a swing low is below nearby lows. If a detector requires three right-hand bars, the pivot at bar t cannot be confirmed until bar t+3 closes. Repainting means later information changes a historically displayed conclusion.",
    example="A peak on session 10 with a three-bar right window is first knowable after session 13. Plotting the marker at 10 is fine only if its later detection time is disclosed.",
    mistake="Backtesting an entry on session 10 using the confirmation that requires session 13.",
    status="Delayed pivots and knowability dates implemented", code="quant_engine/patterns.py: swings",
    exercise="Move replay across a peak; find the first date it becomes confirmed.")
add("zones", "Support, resistance and zones", "Price structure",
    "Support is an area where declines have previously encountered buying; resistance is an area where advances have encountered selling. These are descriptive historical areas, not barriers that prices must respect. Nearby levels are often more honestly represented as zones.",
    example="Lows near ₹99.4, ₹100.0 and ₹100.5 may motivate a zone around ₹100, not a universally exact ₹100.00 support.",
    mistake="Calling every clustered pivot an independent successful test, or treating a zone as guaranteed protection.",
    status="As-of approximate pivot clusters implemented", code="quant_engine/patterns.py: support_resistance")
add("breakout", "Breakout, breakdown, retest and false breakout", "Strategies",
    "A breakout moves beyond a defined upper boundary; a breakdown moves below a lower one. A retest revisits a breached boundary. A false breakout fails a predeclared continuation/invalidation rule. The rule must state whether it uses a touch, completed close, distance or volume.",
    example="A prior high is ₹100. A close at ₹101.2 with eligible volume may qualify under one rule, while an intraday high of ₹100.1 followed by a ₹99 close may not.",
    mistake="Changing the confirmation threshold after seeing which trades won.",
    status="One close/volume/EMA breakout rule implemented; general lifecycle pending", code="quant_engine/strategy.py")
add("sma", "SMA — Simple Moving Average", "Trend indicators",
    "SMA is the equal-weight average of the last N observations. It smooths fluctuations but reacts after prices change. A 20-session average describes a different horizon from a 200-session average.",
    "SMA_N = sum(last N closes) / N.", "Closes 100,102,104 have a three-bar SMA of 102.",
    mistake="Assuming price crossing an average is automatically a profitable entry.",
    status="SMA20/50/200 computed", code="quant_engine/indicators.py")
add("ema", "EMA — Exponential Moving Average", "Trend indicators",
    "EMA assigns recursively declining weight to older observations. The smoothing constant and initial seed both matter when comparing implementations.",
    "alpha=2/(N+1); EMA_today=alpha×close+(1−alpha)×EMA_previous.",
    "With N=3, alpha=0.5, previous EMA=100 and close=104, the next EMA is 102.",
    "This app seeds with the first observation and hides values until the requested warm-up length; some other implementations seed with an SMA.",
    "Comparing early EMA values across libraries without checking seeds.", "EMA20/50 and MACD EMAs computed", code="quant_engine/indicators.py")
add("rsi", "RSI — Relative Strength Index", "Momentum indicators",
    "RSI summarizes the balance of recent upward and downward price changes on a 0–100 scale. It measures momentum, not the probability of a profitable trade. The common 70/30 reference levels are conventions; strong trends can remain beyond them.",
    "RS=smoothed average gain / smoothed average loss; RSI=100−100/(1+RS). Wilder14 seeds with 14 changes then uses (13×previous average+new change)/14.",
    "If smoothed gain is ₹2 and loss ₹1, RS=2 and RSI≈66.67. In this implementation, both zero gives 50; loss zero with positive gain gives 100.",
    "Use trend, price structure and a tested rule for decisions; an RSI level alone is not an entry rule.",
    "RSI80 does not mean an 80% win probability or a guaranteed imminent fall.",
    "Wilder RSI14 computed and numerically tested", "rsi", "quant_engine/indicators.py; tests/test_engine.py",
    "Use the lab with gain=3 and loss=1; explain why the result is 75 rather than a forecast.")
add("macd", "MACD — Moving Average Convergence/Divergence", "Momentum indicators",
    "MACD compares a faster and slower EMA to describe momentum relative to trend. The signal line smooths MACD; the histogram is their difference. MACD has price units, so raw magnitudes are not directly comparable across differently priced stocks.",
    "MACD=EMA12−EMA26; signal=EMA9(MACD); histogram=MACD−signal.",
    "Fast EMA=105, slow EMA=101 gives MACD=4. If signal=3, histogram=1. The histogram can shrink while MACD remains positive.",
    "Zero-line and signal-line crossings answer different questions; neither establishes an edge without evaluation.",
    "Reading a positive histogram as guaranteed positive next-day returns.",
    "MACD12/26/9 computed; contextual strategy extension pending", "macd", "quant_engine/indicators.py",
    "If MACD=−2 and signal=−3, calculate the histogram and explain the negative MACD/positive histogram combination.")
add("atr", "ATR — Average True Range", "Volatility indicators",
    "ATR summarizes bar ranges while accounting for gaps from the previous close. It describes movement size, not direction. Larger ATR means a fixed cash-risk budget generally buys fewer shares when stop distance is tied to ATR.",
    "TR=max(high−low, |high−previous close|, |low−previous close|). Wilder ATR=(13×previous ATR+new TR)/14.",
    "Previous close ₹100, high ₹108 and low ₹104 produce TR=max(4,8,4)=₹8. A 2 ATR stop at ATR=₹3 has ₹6 gross distance.",
    "The app seeds from the first 14 true ranges, using high−low for the first bar.",
    "Calling rising ATR bullish, or treating a 2 ATR stop as a guaranteed maximum loss.",
    "ATR14 computed and used in fixed-at-entry stops", "atr", "quant_engine/indicators.py; quant_engine/strategy.py")
add("bollinger", "Bollinger Bands", "Volatility indicators",
    "Bands surround a moving average with a multiple of rolling standard deviation. They describe relative dispersion around that average. Bandwidth contraction can describe quieter recent prices without determining the direction of the next move.",
    "Middle=SMA20; upper/lower=middle±2×rolling standard deviation. This app uses population standard deviation (ddof=0).",
    "Middle ₹100 and standard deviation ₹2 give bands ₹96 and ₹104.",
    mistake="Treating an upper-band touch as an automatic short or assuming a normal-distribution coverage guarantee.",
    status="Bollinger20 computed; optional chart overlay", code="quant_engine/indicators.py")
add("rvol", "Relative volume (RVOL)", "Volume indicators",
    "Relative volume compares observed volume with a specified historical baseline. The baseline must match timeframe and session position. This daily app uses the mean of the preceding 20 daily volumes, excluding today's bar from the denominator.",
    "Daily RVOL=today volume / mean(previous 20 daily volumes).",
    "300,000 shares versus a previous-20 mean of 200,000 gives 1.5×.",
    mistake="Comparing the first five minutes of a session with average full-day volume, or interpreting volume alone as net buying.",
    status="Daily prior-20 RVOL computed; time-of-day baseline pending", code="quant_engine/indicators.py")
add("obv", "OBV — On-Balance Volume", "Volume indicators",
    "OBV cumulatively adds a bar's volume when its close rises, subtracts it when its close falls, and leaves it unchanged for an equal close. It is a signed-volume proxy, not a measurement of which investors accumulated shares.",
    example="Starting OBV=0: an up-close bar with V100 followed by a down-close bar with V40 yields OBV60.",
    mistake="Calling OBV proof of institutional accumulation or comparing arbitrary starting levels across datasets.",
    status="OBV computed; contextual divergence rules pending", code="quant_engine/indicators.py")
add("doji", "Doji", "Candlestick patterns",
    "A doji has a small body relative to its full high-low range. It says open and close were close together, while the shadows describe excursions. Trend and location are needed before giving the shape a directional interpretation.",
    "Prototype rule: positive range and |close−open| ≤ 10% of range.",
    "O100, H105, L95, C100.5 has body0.5 and range10, so it qualifies under the prototype's tolerance.",
    mistake="Claiming a doji necessarily predicts a reversal.", status="Geometry detected; context/research extensions pending", code="quant_engine/patterns.py")
add("engulfing", "Bullish and bearish engulfing", "Candlestick patterns",
    "An engulfing observation has an opposite-color body that covers the prior candle's body. Body coverage does not require the entire high-low range to be covered. The traditional bullish/bearish interpretation depends on preceding movement and confirmation rules.",
    example="Prior O105,C101; next O100,C106: the new bullish body covers the old bearish body. This alone does not define an executable trade.",
    mistake="Confusing body engulfment with range engulfment, or ignoring that the second bar must close before a close-based signal is known.",
    status="Both body-geometry observations detected; contextual validation pending", code="quant_engine/patterns.py")
add("evening-star", "Evening Star", "Candlestick patterns",
    "A traditional three-candle bearish reversal candidate after an uptrend: a substantial bullish body, a small body near the top, then a bearish body moving back into the first body. Gap requirements and penetration thresholds vary across definitions and must be specified before coding.",
    "Implemented variant: preceding five-bar rise >=1 prior ATR; bullish first body >=0.5 ATR; middle body <=30% of first near its upper half; bearish third body >=50% of first closing below first midpoint. Gaps are not required. Detection waits for the third close.",
    "After an illustrative rise: candle1 O104,C110; candle2 O110.5,C111; candle3 O110.5,C106. The first midpoint is107; third close106 is below it. Use the lab to inspect the geometry.",
    "It is a hypothesis of weakening buying pressure, not proof of future decline. The current application does not permit overnight short-stock execution.",
    "Calling any three candles an Evening Star without prior trend, or assuming a source's entry convention is this simulator's rule.",
    "Contextual detector implemented; statistical validation pending", "star", code="quant_engine/research.py: contextual_candles")
add("morning-star", "Morning Star", "Candlestick patterns",
    "The traditional bullish counterpart to Evening Star: declining context, a substantial bearish body, a small middle body near the low, then a bullish body recovering into the first body. Precise gaps and penetration need a declared convention.",
    mistake="Describing the completed pattern before the third candle has closed.", source="star")
add("double-pattern", "Double top, double bottom and neckline", "Chart patterns",
    "A double bottom has two sufficiently similar lows separated by a meaningful rebound; its neckline is the intervening high. A double top reverses that geometry. A developing shape and a neckline-confirmed event are different states.",
    "Prototype: consecutive same-kind confirmed pivots 5–60 sessions apart, price difference ≤0.75 ATR and recovery ≥1.5 ATR. Confirmation uses a close beyond the neckline by >0.1 ATR.",
    "Lows ₹90 and ₹90.2 with an intervening high ₹105 motivate a potential bottom; it is not confirmed merely because the second low exists.",
    mistake="Reporting a historic shape's detection at its second trough when right-hand pivot confirmation came later.",
    status="Prototype geometry/state events implemented; predictive validation pending", code="quant_engine/patterns.py: double_patterns")
add("divergence", "Bullish and bearish divergence", "Price structure",
    "Bullish divergence commonly means price makes a lower low while a chosen momentum measure makes a higher low; bearish divergence reverses those comparisons. The paired pivots, tolerance, spacing and confirmation time must be defined.",
    mistake="Pairing whichever price and oscillator points make the hindsight chart look persuasive.")
add("risk-sizing", "Position sizing, risk budget and exposure", "Risk and execution",
    "A risk budget is the intended monetary loss under a specified stop-fill model. Exposure is the position's market value. These are different: risking ₹1,000 does not mean investing only ₹1,000. Whole-share quantity must also respect cash and liquidity constraints.",
    "Before costs: quantity=floor(capital×risk_fraction/(entry−stop)); this engine uses a cost-aware loss per share plus cash and previous-volume caps.",
    "Capital ₹100,000, risk1%, entry₹200, stop₹195: gross quantity200, exposure₹40,000 and intended stop loss₹1,000 before fees/slippage.",
    "The lab uses the engine's sizing function and makes the cost assumptions visible.",
    "Treating intended stop risk as a guaranteed upper bound when gaps or non-fills are possible.",
    "Cost-aware whole-share sizing implemented", code="quant_engine/strategy.py: size_position",
    exercise="Raise the entry-to-stop distance without changing capital. Explain why quantity falls.")
add("reward-risk", "R, reward-to-risk and expectancy", "Risk and execution",
    "One R is a declared initial risk unit. Gross reward/risk compares target distance with stop distance. Expectancy weights actual gains and losses by their frequencies; a high win rate alone is not sufficient.",
    "Gross reward/risk=(target−entry)/(entry−stop). Expectancy=p×average_win−(1−p)×average_loss, using compatible net units.",
    "A hypothetical 40% win rate, ₹200 average win and ₹100 average loss gives ₹20 average profit before any omitted costs. A nominal2R target is not proof of those realized averages.",
    mistake="Choosing a distant target to make a ratio attractive without testing whether it is reached.",
    status="Gross/net reference ratio and realized P&L expectancy available")
add("costs", "Basis points, charges, spread and slippage", "Risk and execution",
    "One basis point is 0.01%. Charges are monetary deductions; spread is the bid-ask difference; slippage is execution differing from a reference quote. These can vary with side, order type, size and market conditions.",
    "bps/10,000 converts to a rate. Apply entry and exit charges to their respective notionals.",
    "10bps on ₹40,000 is ₹40 on that side. This prototype uses an illustrative blended rate per side, not an authoritative Indian statutory schedule.",
    mistake="Deducting costs only on entry, or assuming historical bar volume guarantees an immediate fill.",
    status="Blended fees/slippage modeled; detailed Indian schedule pending")
add("gaps", "Gap risk and same-bar ambiguity", "Risk and execution",
    "An opening gap can jump past a stop. A daily candle that touches both stop and target usually does not reveal which came first. A simulator must disclose how it resolves that uncertainty.",
    example="Entry₹100, stop₹95, next open₹90: assuming an exit at₹95 overstates protection. If high₹111 and low₹94 touch a₹110 target and₹95 stop, daily OHLC cannot order those touches.",
    interpretation="This engine uses the open for gap-through-stop exits and the stop first for ambiguous bars, then applies exit slippage and fees.",
    mistake="Claiming the simulator's conservative convention is the market's actual intraday sequence.",
    status="Gap handling and stop-first ambiguity implemented", code="quant_engine/strategy.py: backtest")
add("backtest", "Backtest versus paper trading versus live trading", "Research and statistics",
    "A backtest simulates rules on historical data. Paper trading records decisions prospectively without real orders. Live trading adds real money, operational failures and actual fills. Software correctness does not establish a profitable strategy.",
    example="The same frozen breakout rule can be tested historically, then observed on future sessions without changing its rules after losses.",
    mistake="Calling performance on the same data used to design the strategy an untouched test.",
    status="Exploratory historical baseline implemented; paper/live not implemented")
add("drawdown", "Equity, drawdown and maximum drawdown", "Research and statistics",
    "Equity includes cash plus the current value of open positions under a defined valuation convention. Drawdown is the percentage below the running peak; maximum drawdown is the worst observed decline from a prior peak, not a prediction of the worst future loss.",
    "drawdown=equity/running_peak−1.", "Equity100,000→110,000→99,000 has a−10% drawdown from110,000, even though it is only−1% from initial capital.",
    mistake="Using only closed-trade balances and ignoring losses while positions remain open.",
    status="Liquidation-cost marked equity and drawdown implemented")
add("leakage", "Look-ahead bias and data leakage", "Research and statistics",
    "Leakage uses information unavailable at the decision time. It can enter through future prices, a weekly close known later, full-dataset normalization, revised data, or pivot confirmation. Preventing it requires availability times, not just sorting dates.",
    example="Training a scaler on the entire dataset before splitting leaks later distribution information into earlier training.",
    mistake="Assuming every feature is causal simply because a train/test split is chronological.",
    status="Starter indicator/pivot/signal invariance tests present; all future modules need their own checks")
add("overfitting", "Overfitting, multiple testing and validation", "Research and statistics",
    "Overfitting means a rule captures peculiarities of a sample rather than a robust relationship. Searching many configurations and presenting only the best hides selection. Chronological validation, recorded experiment counts and prospective tests help assess this risk, but do not guarantee future performance.",
    example="If you try 200 indicator combinations, the best historical curve has benefited from selection; it needs a genuinely new evaluation protocol.",
    mistake="Repeatedly checking the test period and still calling it untouched.", source="overfit")
add("calibration", "Probability, heuristic score and calibration", "Research and statistics",
    "A heuristic score summarizes rule satisfaction. A probability estimates how often a defined outcome occurs conditional on information. Calibration asks whether outcomes occur about as frequently as the stated probabilities across suitable future cases.",
    example="A geometric score80/100 does not imply an80% target-hit probability. For predictions near0.7, calibration asks whether about70% of comparable evaluated events realize the precisely defined outcome.",
    mistake="Displaying an arbitrary weighted indicator score with a percent sign as a win probability.",
    status="No calibrated probability is produced in the prototype")

# Compact glossary entries extend the curriculum. Every future implementation must
# replace the brief note with a fully specified rule, fixture and worked lesson.
COMPACT = {
    "Foundations": [
        ("long-short", "Long, short and swing trading", "A long position gains when its exit value exceeds its entry cost; a short gains from a price decline but requires a permitted instrument/borrowing mechanism. Swing trading holds across sessions. The prototype is long-only; short examples are educational, not authorization to short Indian cash equities overnight."),
        ("liquidity", "Liquidity and turnover", "Liquidity is the ability to transact a given size with limited delay and price impact. Volume/turnover are activity measures, not complete liquidity measurements; spread, depth, circuits and order size also matter."),
        ("orders", "Market, limit, stop and stop-limit orders", "A market order prioritizes execution over a specified price; a limit constrains price but can remain unfilled; a stop activates after a trigger; a stop-limit then behaves as a limit. A simulated stop is not guaranteed protection."),
        ("relative-strength", "Relative strength versus RSI", "Relative strength compares performance with another asset or benchmark, such as stock return minus sector return. RSI instead summarizes the stock's own recent gains and losses. Similar names do not make them interchangeable."),
    ],
    "Trend indicators": [
        ("wma", "WMA — Weighted Moving Average", "A moving average using explicit weights, often larger weights for newer observations. The weights must sum to one after normalization; more responsiveness does not imply better prediction."),
        ("adx", "ADX and directional movement", "ADX smooths a normalized measure of directional-movement imbalance to describe trend strength. It does not by itself specify bullish versus bearish direction; +DI and −DI supply additional directional comparisons."),
        ("sar", "Parabolic SAR", "A recursive trailing reference built from extreme prices and an acceleration factor, with direction-switch rules. Specify initialization and bar-level reversal handling before testing it as an exit."),
        ("supertrend", "Supertrend", "A trend overlay based on ATR-related bands and state-dependent trailing/flip rules. Implementations differ in band persistence and initialization, so the precise variant matters."),
    ],
    "Momentum indicators": [
        ("stochastic", "Stochastic oscillator", "Compares the close with the recent high-low range: raw %K=100×(close−lowest_low)/(highest_high−lowest_low). Smoothing produces %K/%D variants; a zero range needs a declared policy."),
        ("stoch-rsi", "Stochastic RSI", "Places RSI within its own recent minimum-to-maximum range, rather than placing price within a price range. It can react sharply; matching timeframe and smoothing conventions is essential."),
        ("roc", "ROC — Rate of Change", "Measures relative price change over N observations, commonly100×(close/close_N_ago−1). Unlike RSI, it is not bounded between0 and100."),
        ("williams", "Williams %R", "Measures where the close lies relative to a recent high-low range, commonly−100×(highest_high−close)/(highest_high−lowest_low). It is closely related to unsmoothed stochastic positioning."),
        ("cci", "CCI — Commodity Channel Index", "Compares typical price with its moving average, scaled by mean absolute deviation and a conventional factor. Despite its name it can be applied beyond commodities; its scale is not a probability."),
    ],
    "Volatility indicators": [
        ("historical-vol", "Historical volatility", "The dispersion of observed returns over a stated window. Annualization multiplies interval volatility by the square root of an assumed periods-per-year count; that scaling relies on assumptions and says nothing about direction."),
        ("donchian", "Donchian channel", "Upper/lower boundaries are rolling highest high and lowest low. For breakout testing, compare today's close with a channel based on prior bars, excluding the current high/low from its own trigger."),
        ("keltner", "Keltner channel", "A moving-average center with range/ATR-based envelopes under a specified variant. Its difference from standard-deviation bands can motivate a squeeze hypothesis, not a proven edge."),
        ("squeeze", "Volatility squeeze and expansion", "A squeeze is a predeclared low-volatility condition, often using bandwidth or relative envelopes. Expansion means movement size grows; neither condition establishes the direction or profitability of a future trade."),
    ],
    "Volume indicators": [
        ("vwap", "VWAP and anchored VWAP", "Volume-weighted average price is sum(price×volume)/sum(volume) over a stated anchor/session. Bar typical-price approximations differ from trade-level VWAP; an anchor must not be chosen with hindsight."),
        ("ad-line", "Accumulation/Distribution line", "Cumulatively weights volume by the close's position within each bar's range. It is a location-weighted volume proxy, not verified investor accumulation or delivery data."),
        ("cmf", "Chaikin Money Flow", "Normalizes a rolling sum of close-location-weighted volume by rolling volume. Zero ranges and volume need an explicit convention; a positive value is not a measured net inflow of cash."),
        ("mfi", "Money Flow Index", "An oscillator comparing positive and negative typical-price×volume flows across a window. Its name does not mean it measures actual deposits, ownership or institutional money."),
        ("delivery", "Delivery quantity and delivery percentage", "Exchange-reported delivery-related quantities describe a different facet of activity than traded volume. Use the provider's exact definition, publication time and units; they do not identify investors or prove accumulation."),
    ],
    "Chart patterns": [
        ("triple-bottom", "Triple bottom", "Three comparable troughs separated by rebounds, under explicit spacing/tolerance rules. A prospective neckline break and invalidation define separate states; three lows alone do not establish success."),
        ("triple-top", "Triple top", "Three comparable peaks separated by pullbacks. Define the lower boundary and when a break becomes knowable before assigning confirmation."),
        ("head-shoulders", "Head and shoulders", "Three swing peaks with a higher central head and two lower shoulders, separated by troughs defining a neckline. Symmetry, prominence, prior trend and neckline-break rules must be stated."),
        ("inverse-head-shoulders", "Inverse head and shoulders", "Three swing troughs with a deeper central head and higher shoulders. The intervening peaks define a neckline; a visible resemblance is not a validated reversal."),
        ("rounding-bottom", "Rounding bottom", "A gradually flattening decline transitioning toward rising prices. Curvature, duration, scale and confirmation must be quantified rather than judged only by a U-shaped drawing."),
        ("rounding-top", "Rounding top", "A gradually slowing advance transitioning toward declining prices. Its apparent curvature depends on chart scaling and needs a reproducible definition."),
        ("broadening", "Broadening formation", "A sequence with expanding boundaries, often higher highs and lower lows. Specify minimum alternating pivots and boundary slopes; direction is not implied solely by expansion."),
        ("bull-flag", "Bullish flag", "A brief bounded consolidation following an upward impulse. A detector needs separate impulse, countertrend/channel, duration, breakout and invalidation rules."),
        ("bear-flag", "Bearish flag", "A brief bounded consolidation after a downward impulse, often drifting upward. Its traditional continuation interpretation remains a hypothesis to evaluate."),
        ("bull-pennant", "Bullish pennant", "An upward impulse followed by a small converging consolidation. Distinguish it from a large standalone triangle and predeclare the eligible breakout time."),
        ("bear-pennant", "Bearish pennant", "A downward impulse followed by a small converging consolidation. Specify boundaries and expiry instead of waiting indefinitely for the desired breakdown."),
        ("ascending-triangle", "Ascending triangle", "Rising swing lows beneath approximately flat upper highs. Tolerances, minimum interactions and breakout criteria determine whether it qualifies; the name does not guarantee an upward break."),
        ("descending-triangle", "Descending triangle", "Falling swing highs above approximately flat lower lows. A lower-boundary breach is a separate event from a developing shape."),
        ("symmetrical-triangle", "Symmetrical triangle", "Descending highs and ascending lows form converging boundaries. Boundary fitting must use only confirmed available anchors; either breakout direction is possible."),
        ("rising-wedge", "Rising wedge", "Both boundaries slope upward while converging. The traditional weakening/reversal interpretation depends on context and must be tested against a precise definition."),
        ("falling-wedge", "Falling wedge", "Both boundaries slope downward while converging. A developing wedge is not the same event as an upward boundary break."),
        ("rectangle", "Rectangle consolidation", "Repeated interactions with approximately horizontal upper and lower boundaries. Define width, minimum duration and independent interactions; bounded history does not guarantee a tradable range."),
        ("channel", "Price channel", "Price oscillates between approximately parallel boundaries. Slopes, anchor selection and tolerance must be stated, especially when using a channel for projected support or targets."),
        ("cup-handle", "Cup and handle", "A rounded recovery toward a prior area followed by a smaller consolidation or pullback. Depth, duration, handle position and confirmation are necessary geometric constraints."),
        ("inverse-cup-handle", "Inverse cup and handle", "An inverted rounded structure followed by a smaller consolidation. The boundaries and prospective breakdown must be specified rather than selected after the decline."),
        ("measured-move", "Measured-move target", "Projects a predeclared pattern dimension from a breakout area, such as bottom-to-neckline height. It is a geometric reference, not an expected value or a guaranteed target."),
    ],
    "Candlestick patterns": [
        ("dragonfly-doji", "Dragonfly Doji", "A near-zero body toward the high of the candle with a pronounced lower shadow. Prior trend and location matter; geometry alone does not prove rejection will persist."),
        ("gravestone-doji", "Gravestone Doji", "A near-zero body toward the low with a pronounced upper shadow. Define small-body and shadow thresholds rather than requiring visually perfect equality."),
        ("long-legged-doji", "Long-Legged Doji", "A small body with substantial excursions on both sides. It describes an interval of movement with little open-to-close change, not a guaranteed directional reversal."),
        ("hammer", "Hammer", "A small body near the upper range with a long lower shadow, interpreted as a bullish-reversal candidate only in appropriate declining context. Exact shadow/body ratios are configurable conventions."),
        ("hanging-man", "Hanging Man", "Hammer-like geometry in an advancing context. Its different traditional interpretation illustrates why shape and preceding trend must be separate parts of detection."),
        ("inverted-hammer", "Inverted Hammer", "A small body near the lower range with a long upper shadow following a decline. It needs context/confirmation rather than inheriting a bullish label from shape alone."),
        ("shooting-star", "Shooting Star", "Inverted-hammer-like geometry after an advance. A long upper shadow can motivate a rejection hypothesis, but it does not reveal investor identity or guarantee a fall."),
        ("bull-marubozu", "Bullish Marubozu", "A substantial bullish body with little shadow under a declared tolerance. Open near low and close near high describes that bar, not certainty of continuation."),
        ("bear-marubozu", "Bearish Marubozu", "A substantial bearish body with little shadow. Use relative thresholds appropriate to price scale and tick size rather than exact arithmetic equalities."),
        ("spinning-top", "Spinning Top", "A small real body with upper and lower shadows. It describes limited net change relative to excursions; a preceding trend and location are needed for a directional hypothesis."),
        ("piercing", "Piercing Pattern", "A declining-context two-bar candidate where a bearish body is followed by a bullish recovery deep into that body, commonly beyond its midpoint. Gap and recovery thresholds need a declared variant."),
        ("dark-cloud", "Dark Cloud Cover", "An advancing-context two-bar candidate where a bullish body is followed by a bearish penetration into it, commonly beyond its midpoint. Define the open-gap and penetration convention explicitly."),
        ("bull-harami", "Bullish Harami", "A smaller body inside a preceding larger bearish body, traditionally considered in declining context. Body containment differs from full-range containment."),
        ("bear-harami", "Bearish Harami", "A smaller body inside a preceding larger bullish body, traditionally considered in advancing context. It does not require the entire candle range to fit inside."),
        ("tweezer-bottom", "Tweezer Bottom", "Adjacent or nearby candles interact with sufficiently similar lows under a declared tolerance. Specify candle count, preceding trend and how independent the interactions are."),
        ("tweezer-top", "Tweezer Top", "Adjacent or nearby candles interact with sufficiently similar highs. Similarity should be defined relative to tick size or volatility rather than an arbitrary universal currency difference."),
        ("bull-kicking", "Bullish Kicking", "A strong bearish candle followed by a bullish candle separated by an upward gap under a strict variant, often using near-marubozu bodies. Rare patterns require especially cautious sample-size claims."),
        ("bear-kicking", "Bearish Kicking", "The bearish counterpart with a strong bullish candle followed by a downward-gapped bearish candle. Body and gap definitions materially affect event counts."),
        ("morning-doji-star", "Morning Doji Star", "A Morning Star variant whose middle candle qualifies as a doji under stated tolerances. The third candle and prior downtrend remain part of the full definition."),
        ("evening-doji-star", "Evening Doji Star", "An Evening Star variant with a doji middle candle. Calling it more reliable than another pattern requires comparable historical evidence, not its name."),
        ("three-soldiers", "Three White Soldiers", "Three successive substantial bullish bodies with rising closes, under explicit open/body/wick constraints. Distinguish healthy progression from unusually extended prices near an obstacle."),
        ("three-crows", "Three Black Crows", "Three successive substantial bearish bodies with falling closes and specified opening/wick conditions. Declining closes alone are too loose a complete definition."),
        ("three-inside-up", "Three Inside Up", "A bullish-harami-style initial pair followed by a confirming bullish third bar under a specified close condition. State the third-bar requirement before testing."),
        ("three-inside-down", "Three Inside Down", "A bearish-harami-style initial pair followed by a confirming bearish third bar. The detector becomes knowable only when all required bar conditions are observed."),
        ("three-outside-up", "Three Outside Up", "A bullish engulfing-style pair followed by a higher confirming third close under the chosen variant. It is a separate event from the two-bar engulfing observation."),
        ("three-outside-down", "Three Outside Down", "A bearish engulfing-style pair followed by a lower confirming third close. Event overlap must be considered when counting historical independent opportunities."),
    ],
    "Research and statistics": [
        ("win-rate", "Win rate and profit factor", "Win rate is the fraction of evaluated completed trades with positive net P&L. Profit factor is total positive P&L divided by absolute negative P&L. Both need sample size and conventions for break-even/open trades; neither is a calibrated forecast."),
        ("sharpe-sortino", "Sharpe, Sortino and Calmar", "Sharpe scales mean excess return by return volatility; Sortino uses a defined downside-deviation measure; Calmar compares annualized return with drawdown magnitude. Frequency, horizon, risk-free rate and annualization conventions matter."),
        ("mfe-mae", "MFE and MAE", "Maximum favorable/adverse excursion measures the best/worst observed movement during a defined trade/event interval relative to an entry/reference. The units, long/short direction and intrabar ambiguity must be explicit."),
        ("survivorship", "Survivorship bias", "Researching only today's surviving stocks excludes historical failures, delistings or removed index constituents. A credible universe needs time-specific membership and security histories."),
        ("walk-forward", "Walk-forward evaluation", "Repeatedly train or choose rules on earlier periods and evaluate on the next eligible period. The retraining schedule and selection rules must be fixed before using the combined forward results."),
        ("purge-embargo", "Purging, embargo and overlapping labels", "An outcome label can span future bars. Overlapping outcome intervals across split boundaries can contaminate evaluation. Purging removes intersecting training events; embargo adds a declared temporal separation. The exact scheme depends on label horizons."),
        ("brier-logloss", "Brier score and log loss", "Brier score averages squared probability errors; log loss penalizes confident incorrect probability assignments. Both require correctly defined outcomes and held-out predictions; neither directly measures after-cost profitability."),
        ("classification", "Precision, recall, F1, ROC-AUC and PR-AUC", "These assess classification/ranking under particular thresholds or across thresholds. Class balance and economic payoffs matter: high classification performance does not by itself imply a useful trading strategy."),
        ("censoring", "Censoring and maximum holding horizon", "If the outcome horizon extends beyond available data, the outcome may be unknown rather than a failure. Expiry, neither-barrier-hit and forced end-of-data close need distinct documented labels."),
        ("regime", "Market regime and concept drift", "A regime is a declared grouping of market conditions, such as volatility/trend context. Drift means relationships or distributions change. Regime labels chosen using future outcomes can themselves leak information."),
        ("benchmark", "Benchmark, ablation and opportunity cost", "A benchmark is the comparison a strategy must justify its complexity against. Ablation removes one component to estimate its incremental contribution. Use comparable costs, exposure, universe and evaluation dates where appropriate."),
    ],
    "AI and software": [
        ("ml-baselines", "Logistic regression, random forest and boosted trees", "Logistic regression is a useful interpretable probability baseline; forests average trees; boosted trees build sequential corrections. More complexity must justify itself on suitable unseen data, calibration and net economic outcomes."),
        ("provenance", "Data provenance, run ID and reproducibility", "A reproducible run records data version/hash, source, adjustment policy, parameters, code/model version and decision time. A source hash identifies bytes; it does not prove those bytes are accurate."),
        ("llm", "LLM narration versus numerical analysis", "A language model can explain a validated evidence bundle. It should not manufacture indicator values, price levels or win probabilities. Numeric engines, statistical evaluation and narrative generation remain separate components."),
        ("git-github", "Git, GitHub, commits and continuous integration", "Git records versioned snapshots; GitHub hosts repositories and collaboration. A commit identifies a snapshot/history record. CI runs specified checks remotely. A connected GitHub app and the computer's Git client can have different authentication contexts."),
        ("image-data", "Screenshot observations versus structured data", "A screenshot shows rendered pixels and may omit axes, scale, timeframe or full history. Qualitative visual observations must be separated from exact computations on verified OHLCV."),
    ],
}
for category, rows in COMPACT.items():
    for key, title, definition in rows:
        add(key, title, category, definition,
            interpretation="This is a curriculum definition. Before implementing a detector or strategy, specify its exact rules and evaluate them on appropriate data.",
            mistake="Confusing a traditional interpretation or an educational description with validated predictive performance.")

add("bhavcopy", "Bhavcopy and UDiFF daily reports", "Data quality",
    "A daily exchange report contains records for many securities for one session. It is not already one stock's historical price table. UDiFF is a standardized exchange-file format; a matching header does not authenticate a file's origin.",
    rule="Select the exact symbol and series across completed daily reports; map TradDt and quoted OHLCV without price repair.",
    example="Three invented daily reports each contain ALPHA and BETA. Selecting ALPHA EQ creates three daily bars, not six observations or an average of both stocks.",
    mistake="Uploading overlapping reports and silently removing duplicates, or assuming one report supplies months of history.",
    status="Offline CSV/ZIP schema-subset preview tested with synthetic reports; real-file acceptance pending", source="nse-reports",
    code="quant_engine/nse_files.py; tests/test_nse_files.py",
    exercise="Select DEMOBETA in the report walkthrough, then explain why its 80 bars came from 80 reports.")
add("security-identity", "Symbol, series, ISIN and security continuity", "Data quality",
    "A ticker is a market label, a series classifies a trading segment, and an ISIN identifies a security. Labels alone do not establish historical continuity through reorganizations or symbol changes.",
    example="Invented ALPHA EQ has ISIN ZZ0000000001 on one date and ZZ0000000002 later. This importer stops the combination for review instead of assuming continuity.",
    interpretation="This build checks ISIN structure and one-ISIN consistency, not the check digit, real listing or full corporate history. Only EQ series is imported.",
    status="EQ selection and basic identity-consistency guards; listing-history resolver pending", source="nse-formats",
    code="quant_engine/nse_files.py: ReportBundle.select",
    exercise="Explain why the synthetic ZZ identifiers passing a format check does not make them actual listed securities.")
add("data-passport", "Data passport, source hash and analysis slice", "AI and software",
    "A data passport records instrument, source claim, raw-file hashes, normalized-data hash, date convention and adjustment declaration. It documents what was used without certifying authenticity or accuracy.",
    rule="A dataset ID hashes stable input identity and declarations. Import time is recorded separately. Replaying a subset preserves the source ID and adds a separate analyzed-data hash.",
    example="Import 80 invented sessions, replay the first 40. Source rows remain 80, analyzed rows become 40, and the analyzed CSV hash changes while the original dataset ID stays fixed.",
    mistake="Treating matching hashes as proof of correct prices or confusing a full-source hash with the exported replay slice.",
    status="JSON passport and analyzed-CSV exports; source and replay hashes included in analysis evidence",
    code="quant_engine/datasets.py; quant_engine/data_ui.py",
    exercise="Download a passport before and after replay. Compare source_rows, analyzed_rows and both normalized hashes.")

add("nse-quote-export", "NSE stock-history CSV: close, LTP, volume and value", "Data quality",
    "A security-history download contains one stock over many sessions. CLOSE is the reported closing price, LTP is the last traded price, PREV. CLOSE describes the preceding close, VOLUME is share quantity and VALUE is rupee turnover. These fields are not interchangeable.",
    rule="The automatic stock-history adapter uses DATE/OPEN/HIGH/LOW/CLOSE/VOLUME, EQ series only. It converts explicit DD-Mon-YYYY dates and valid Indian or international comma grouping, then applies the usual OHLCV validation.",
    example="An invented row has CLOSE 1,240.00, LTP 1,248.00 and VOLUME 23,34,553. The analyzed close is 1240 and the traded quantity is 2334553 shares. VALUE is not substituted for volume.",
    interpretation="Keep the downloaded filename to retain its stock-label hint. The file may not contain a symbol or ISIN, so the filename is a declaration rather than independently verified security identity.",
    mistake="Renaming VALUE to volume, treating a missing dash as zero, or assuming formatting conversion also adjusts splits and dividends.",
    status="Automatic NSE security-history CSV/XLSX normalization; supplied real-file workflow checked locally", source="nse-reports",
    code="quant_engine/nse_quotes.py; quant_engine/data.py; tests/test_nse_quotes.py",
    exercise="Upload an original NSE stock-history CSV through Upload daily data. Find the detected format and warm-up warning, and explain why CLOSE and LTP can differ.")

add("correlation", "Return correlation and matched intervals", "Research and statistics",
    "Pearson correlation describes linear co-movement between two return samples, from minus one to plus one. Stock price levels can trend together without providing a useful return relationship. Correlation is not causation, cointegration or a pairs-trading rule.",
    rule="Compute each stock's simple returns on its native observation intervals. Pair only matching start and end dates; never forward-fill missing prices. The UI requires ten paired intervals for a coefficient and uses a configurable rolling count of pairs.",
    example="If A's Tuesday return starts Monday but B's Tuesday return starts Friday because Monday is absent, those returns are excluded from the paired sample. Two constant return series have undefined correlation, not zero.",
    interpretation="The coefficient depends on period, data basis and sample size. A short sample can be unstable. Spearman compares ranks; this build rounds returns to 12 decimals before ranking to stabilize numerical ties.",
    status="Two-stock Pearson/Spearman return and rolling-correlation workspace", code="quant_engine/comparison.py; quant_engine/comparison_ui.py")
add("indexed-performance", "Indexed performance and observed-date drawdown", "Research and statistics",
    "Rebasing two price series to 100 at a common starting observation makes their proportional price changes comparable. Drawdown is current indexed value divided by the maximum so far minus one.",
    example="A rises from index100 to110 then falls to88: its observed-date drawdown is 88/110−1=−20%. If B stays at100, A/B relative performance is0.88 at the final point.",
    interpretation="This comparison uses price returns, not dividend-inclusive total returns. Drawdowns use common observed dates and can miss extremes hidden by absent observations; return volatility is per matched interval, without annualization.",
    status="Indexed two-stock performance, relative ratio and common-observation drawdowns", code="quant_engine/comparison.py")

add("forward-outcomes", "Forward outcomes and measurement timing", "Research and statistics",
    "A forward outcome measures price movement after an observation became knowable. Its reference price and horizon must be declared before interpreting the result. Formation time can precede the first moment the complete pattern was detectable.",
    rule="For a pattern known at observation t, the default reference is open[t+1]. Horizon h ends at close[t+h]. The alternative reference is close[t]; it is an observational convention, not an available trading fill. Horizons count uploaded observations.",
    example="Invented example: a setup is known Monday, the next observed open is100, and the close at t+5 is104. The gross five-observation movement is104/100−1=4%. A 1-observation next-open result is the next bar's open-to-close change.",
    interpretation="Pattern-direction mode negates returns for bearish events. This makes favourable falls positive without simulating short selling, costs or share accounting. Neutral shapes use upward-price mode.",
    mistake="Measuring from a pivot's formation price, including the detection candle's extreme, or treating gross price movement as realized trading profit.",
    status="Versioned causal forward-outcome research workspace", source="research-bias", code="quant_engine/event_study.py")
add("conditional-baseline", "Matched non-event baseline and coverage", "Research and statistics",
    "A conditional baseline asks what happened on other dates with similar observable conditions. It gives context to a selected historical sample but does not by itself identify what would have happened without the pattern or establish a causal effect.",
    rule="Match the same uploaded stock and date interval on close versus EMA50 and relative-volume bucket at the decision close. A baseline anchor has no selected eligible event that day; future events remain allowed. Compare each event with its matching pool's mean, then average those differences across covered events.",
    example="Invented example: two covered event returns are6% and−2%; their context-pool means are2% and1%. The event mean is2%, the event-weighted baseline is1.5%, and the difference is0.5 percentage points. An event lacking enough controls is omitted from both matched means.",
    interpretation="Controls are reused across events and may overlap their outcomes. This retrospective baseline uses the selected historical interval, including later dates. It is not an earlier-only forecast or the market-model abnormal return used in formal financial event studies.",
    mistake="Comparing a full-cohort event mean with a baseline covering only some events, or dropping controls because a future pattern occurred.",
    status="Auditable context-matched baseline pools and coverage counts implemented", source="event-method", code="quant_engine/event_study.py")
add("event-overlap", "Overlapping event windows and sample dependence", "Research and statistics",
    "Two signals can share the same future price path, so counting them separately can exaggerate the apparent amount of evidence. Distinct pattern names can also identify closely related observations.",
    rule="Default thinning keeps the earliest occurrence within each event type/state and requires the next knowledge index to exceed the previous index plus the largest selected horizon. Apply this before checking outcome completeness. Baseline anchors are separately thinned within each context pool.",
    example="Invented knowledge indices1,2,4,5 with maximum horizon3 retain1 and5. Index4 is rejected because the closed windows share an endpoint. A different event type at index2 can remain and is not independent evidence.",
    interpretation="Thinning reduces direct window reuse; it does not remove market dependence, cross-cohort overlap or shared controls. Naive independent-sample confidence intervals would overstate precision.",
    status="Deterministic cohort/context-pool spacing with retained exclusion ledger", code="quant_engine/event_study.py")
add("sample-dispersion", "Outcome distribution versus statistical uncertainty", "Research and statistics",
    "Mean, median, quartiles and the fraction of positive observations summarize an observed distribution. A confidence interval concerns uncertainty about an estimated population quantity under stated sampling assumptions; these are different objects.",
    rule="Show complete outcome counts, mean/median, 25th/75th percentiles, signed excursions and positive fraction. Zero is |movement|<=1e−12; positive means movement>1e−12. No complete outcomes means unavailable metrics. Counts below5 and30 receive descriptive caution labels, not statistical-validity guarantees.",
    example="Invented outcomes−2%,0%,4% have mean0.6667%, median0%, a positive fraction of1/3, and one flat result. These three observations do not establish a one-third future success probability.",
    interpretation="The current workspace supplies descriptive dispersion and sample warnings. Dependent-data uncertainty, multiple-testing correction and held-out predictive validation remain future work.",
    mistake="Calling a box plot a confidence interval or a historical positive fraction a calibrated forecast.",
    status="Descriptive outcome distributions and small-sample labels implemented", source="research-bias", code="quant_engine/event_study.py; quant_engine/event_study_ui.py")

BY_ID = {c["id"]: c for c in CONCEPTS}
BY_ID["mfe-mae"].update(
    rule="Use only complete post-detection windows t+1…t+h. Upward MFE=max(0,max(high)/reference−1), signed MAE=min(0,min(low)/reference−1). Bearish MFE=max(0,1−min(low)/reference), signed MAE=min(0,1−max(high)/reference).",
    example="Invented reference100, later maximum high108 and minimum low95 give upward MFE8% and signed MAE−5%; bearish MFE5% and signed MAE−8%. Daily OHLC cannot reveal which extreme occurred first.",
    app_status="Complete-horizon event MFE/signed MAE computed; order execution remains separate", code="quant_engine/event_study.py")
BY_ID["censoring"].update(
    rule="A horizon extending beyond replay remains Incomplete horizon. Its return/MFE/MAE are null and it is omitted from averages, never converted to a loss or closed early. Complete raw-price windows crossing a known audited action are separately excluded.",
    example="An invented setup known two observations before the replay cutoff has a complete1-observation outcome and an incomplete5-observation outcome. These horizons have different complete counts.",
    app_status="Per-horizon event censoring and audited raw-action exclusions implemented", code="quant_engine/event_study.py")
for key in ("hammer", "hanging-man", "inverted-hammer", "shooting-star", "morning-star"):
    BY_ID[key].update(app_status="Contextual detector implemented; statistical validation pending", code="quant_engine/research.py: contextual_candles")
for key in ("ascending-triangle", "descending-triangle", "symmetrical-triangle", "rectangle"):
    BY_ID[key].update(app_status="Frozen confirmed-anchor geometry and break/expiry states implemented; statistical validation pending", code="quant_engine/research.py: chart_formations")
BY_ID["breakout"].update(app_status="Configurable frozen-range breakout/retest/failure/continuation observations; baseline strategy remains separate", code="quant_engine/research.py: breakout_events")
BY_ID["divergence"].update(app_status="Delayed confirmed-pivot RSI and MACD divergence observations implemented", code="quant_engine/research.py: momentum_analysis")
BY_ID["roc"].update(app_status="Ten-observation price ROC computed", code="quant_engine/indicators.py")
BY_ID["stochastic"].update(app_status="Fast %K14 and three-observation %D; zero range undefined", code="quant_engine/indicators.py")
BY_ID["relative-strength"].update(app_status="Two-stock indexed performance ratio; sector/benchmark research pending", code="quant_engine/comparison.py")
BY_ID["timeframe"].update(
    app_status="Daily/prior-week context; bounded NSE CM 2026 calendar and freshness checks",
    code="quant_engine/data.py: completed_weeks; quant_engine/calendar.py")
BY_ID["git-github"].update(
    app_status="Private repository, verified source upload and passing GitHub CI; local Git authentication is separate",
    code="docs/GITHUB_SYNC.md; .github/workflows/tests.yml",
    exercise="Open the source commit and its Actions run. Explain how a verified file snapshot differs from a passing test result.")
CURRENT_BEHAVIOR_IDS = {
    "forward-outcomes", "conditional-baseline", "event-overlap", "sample-dispersion", "mfe-mae", "censoring",
    "correlation", "indexed-performance", "relative-strength", "roc", "stochastic", "divergence", "evening-star", "morning-star",
    "hammer", "hanging-man", "inverted-hammer", "shooting-star", "ascending-triangle", "descending-triangle", "symmetrical-triangle", "rectangle",
    "bhavcopy", "security-identity", "data-passport", "nse-quote-export",
    "ohlcv", "timeframe", "price-return", "adjustments", "trend", "pivot", "zones", "breakout",
    "sma", "ema", "rsi", "macd", "atr", "bollinger", "rvol", "obv", "doji", "engulfing",
    "double-pattern", "risk-sizing", "reward-risk", "costs", "gaps", "backtest", "drawdown", "leakage",
}


def find_concepts(query="", category="All categories", implementation="All implementation states"):
    query = query.strip().casefold()
    return [c for c in CONCEPTS
            if (category == "All categories" or c["category"] == category)
            and (implementation == "All implementation states" or
                 (implementation == "Has current engine behavior" and c["id"] in CURRENT_BEHAVIOR_IDS))
            and (not query or query in " ".join(str(c[k]) for k in ("title", "definition", "rule", "example")).casefold())]


def concept_markdown(concept, builder_details=True):
    c = concept
    lines = [f"## {c['title']}", f"**Category:** {c['category']} · **Application status:** {c['app_status']}", c["definition"]]
    for key, label in (("rule", "Calculation or rule"), ("example", "Hypothetical worked example"),
                       ("interpretation", "How to read it"), ("mistake", "Common mistake"), ("exercise", "Try it yourself")):
        if c[key]:
            lines += [f"**{label}:** {c[key]}"]
    if c["source"]:
        title, url = SOURCES[c["source"]]
        lines.append(f"**Further reading:** [{title}]({url})")
    if builder_details and c["code"]:
        lines.append(f"**Implementation reference:** `{c['code']}`")
    return "\n\n".join(lines)


def handbook_markdown():
    intro = ["# Education and Concepts", "Updated: 2026-11-05",
             f"{len(CONCEPTS)} entries. Source of truth: `learning/concepts.py`; the app and this handbook share it.",
             "All numerical examples are invented teaching examples, explicitly not market observations or performance claims. A traditional pattern description does not demonstrate a trading edge. A glossary entry is not proof that its detector exists.",
             "Start with OHLCV → returns/adjustments → confirmed structure → SMA/EMA → RSI/MACD → ATR/risk → backtesting/leakage → probability calibration. Use the app's Learning lab and `docs/lessons/01_from_prices_to_evidence.md`.",
             "The concise catalogue establishes vocabulary now. Detailed calculations and tested implementation lessons expand one milestone at a time. External links are further reading, not endorsement of their trading-entry conventions. These notes and examples are original explanations, not copied chapters."]
    return "\n\n".join(intro + [concept_markdown(c) for c in CONCEPTS]) + "\n"
