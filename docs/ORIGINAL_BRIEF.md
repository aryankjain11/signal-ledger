# PROJECT: AI-POWERED QUANTITATIVE TECHNICAL ANALYSIS & TRADING STRATEGY ENGINE

## 1. YOUR ROLE

Act as a senior quantitative researcher, financial data scientist, algorithmic trading engineer, technical analysis expert, machine learning engineer and full-stack software developer.

Your responsibility is to design and develop a sophisticated AI-powered financial analysis platform that can analyse historical stock market data, identify technical patterns and price-action trends, evaluate potential trading opportunities, formulate statistically informed trading strategies and visually explain its findings.

The application should combine:

1. Classical technical analysis.
2. Mathematical chart-pattern recognition.
3. Candlestick pattern recognition.
4. Trading volume and momentum analysis.
5. Multi-timeframe analysis.
6. Statistical analysis and quantitative research.
7. Machine learning and predictive modelling.
8. Risk management and position sizing.
9. Automated chart annotation and visual explanations.
10. AI-powered interpretation and reporting.

The objective is not merely to build a stock-price prediction model.

We are building an intelligent technical analysis and trading research platform that attempts to understand the underlying structure of stock-price movements, identify potentially exploitable market patterns, evaluate the strength of those patterns and translate the findings into well-defined trading strategies.

The system must prioritise analytical rigour, statistical validation, interpretability and reliability over impressive-looking predictions.

---

# 2. PROJECT VISION AND OBJECTIVE

Build an application where a user can provide stock market data in any of the following ways:

* Enter a stock ticker or company name.
* Upload historical OHLCV data in CSV or Excel format.
* Upload an image or screenshot of a stock chart.
* Eventually connect to a stock market data provider or broker API for automatic data retrieval.

The application should process the supplied information and perform a comprehensive technical analysis of the stock.

It should attempt to answer the following questions:

1. What is the current price trend?
2. Is the stock bullish, bearish or consolidating?
3. What are the significant support and resistance levels?
4. What chart patterns are currently developing?
5. Are there identifiable candlestick formations?
6. What does trading volume suggest about market participation?
7. Are there signs of accumulation or distribution?
8. Is momentum strengthening or weakening?
9. Are there divergences between price and technical indicators?
10. Are different timeframes supporting or contradicting one another?
11. Is there a potentially profitable trading opportunity?
12. Where would a sensible entry point be?
13. Where should the stop-loss be placed?
14. What are the potential profit targets?
15. What is the risk/reward ratio?
16. How strong is the evidence supporting the proposed trade?
17. How have historically similar setups performed?
18. Under what circumstances should the trade be avoided?

The output should be a comprehensive technical analysis report accompanied by an annotated chart and, where sufficient evidence exists, a structured trading strategy.

The application must also be capable of concluding that no attractive trading opportunity currently exists.

It should never force a buy or sell recommendation merely because the user has requested an analysis.

---

# 3. CORE SYSTEM ARCHITECTURE

Develop the application using a modular architecture.

The major components should operate independently but communicate through a common analytical pipeline.

The proposed workflow is:

USER INPUT
|
v
DATA ACQUISITION ENGINE
|
v
DATA CLEANING AND PREPROCESSING
|
v
TECHNICAL ANALYSIS ENGINE
|
+--------------------+
|                    |
v                    v
TREND ANALYSIS      PATTERN RECOGNITION
|                    |
v                    v
MOMENTUM AND        CANDLESTICK PATTERN
VOLUME ANALYSIS     RECOGNITION
|                    |
+--------------------+
|
v
MULTI-TIMEFRAME
ANALYSIS
|
v
QUANTITATIVE ANALYSIS
|
v
HISTORICAL PATTERN
PERFORMANCE
|
v
TRADING STRATEGY
GENERATION
|
v
RISK AND CONFIDENCE
EVALUATION
|
v
AI INTERPRETATION
|
v
VISUAL DASHBOARD
|
v
ANNOTATED CHART +
COMPREHENSIVE REPORT

Maintain strict separation between numerical analysis, statistical modelling and language-model interpretation.

The LLM must not independently invent indicator values, price levels, probabilities or trading signals. It must receive structured outputs from the underlying analytical engines and explain those outputs.

---

# 4. MODULE 1: MARKET DATA ACQUISITION

This module is responsible for obtaining and standardising stock market data.

## 4.1 Required input data

Use the OHLCV (Open, High, Low, Close, Volume) format.

Each observation should contain:

* Timestamp
* Open price
* High price
* Low price
* Close price
* Trading volume

Where available, additionally incorporate:

* Adjusted closing prices
* VWAP
* Number of trades
* Bid/ask spread
* Delivery volume and delivery percentage
* Market index data
* Sector index data

The system must validate the input data before analysing it.

Check for:

* Missing observations.
* Duplicate timestamps.
* Invalid OHLC relationships.
* Negative or missing volume.
* Incorrect date formats.
* Inconsistent sampling intervals.
* Incorrect timezone handling.
* Corporate actions that may distort historical price comparisons.

Do not silently replace missing observations with fabricated values.

## 4.2 Multiple timeframes

The system must support the following timeframes:

* 1 minute
* 5 minutes
* 15 minutes
* 30 minutes
* 1 hour
* 4 hours, where appropriate
* Daily
* Weekly
* Monthly

It must be possible to resample finer-grained data into higher timeframes.

Ensure that OHLCV aggregation is mathematically correct:

* Open = first opening price.
* High = maximum high.
* Low = minimum low.
* Close = last closing price.
* Volume = sum of volume.

Do not create higher-resolution data from lower-resolution observations.

## 4.3 Data sources

Initially, support CSV and Excel uploads.

Design a provider-independent data acquisition layer so that integrations can be introduced later.

Potential integrations include:

* Zerodha Kite Connect.
* Upstox API.
* DhanHQ API.
* Other reliable historical market data providers.

Keep API keys and credentials in environment variables or secure configuration files.

Never hardcode credentials.

Clearly identify the data source, its timestamp, its adjustment status and any known limitations.

For the initial implementation, prioritise reliable historical CSV-based analysis over complicated live-market integrations.

---

# 5. MODULE 2: TREND IDENTIFICATION AND PRICE-ACTION ANALYSIS

This is one of the most important modules.

The model must understand how prices evolve over time rather than simply calculate indicators.

## 5.1 Basic trend identification

Identify whether a stock is exhibiting:

* Bullish trend.
* Bearish trend.
* Sideways movement.
* Consolidation.
* Potential trend reversal.
* Strong momentum.
* Weakening momentum.

Use swing highs and swing lows to identify the market structure.

An uptrend should generally exhibit:

Higher Highs (HH) + Higher Lows (HL).

A downtrend should generally exhibit:

Lower Highs (LH) + Lower Lows (LL).

The system should distinguish between meaningful market-structure changes and insignificant short-term fluctuations.

Use configurable pivot or swing-point detection algorithms.

Where right-side observations are required to confirm a pivot, account for the confirmation delay. Never use future observations to claim that a pivot was known at an earlier historical timestamp.

## 5.2 Support and resistance identification

Detect potential:

* Horizontal support levels.
* Horizontal resistance levels.
* Dynamic support and resistance.
* Previous swing highs and lows.
* Psychological price levels.
* Breakout levels.
* Breakdown levels.
* Support/resistance role reversals.

Evaluate the significance of a level using:

* Number of historical price interactions.
* Rejection strength.
* Trading volume near the level.
* Duration of the level.
* Price movement following previous interactions.

Represent important support and resistance as zones where appropriate, rather than pretending every level has an exact, universal price.

## 5.3 Breakout and breakdown detection

Identify:

* Bullish breakouts.
* Bearish breakdowns.
* Failed breakouts.
* False breakdowns.
* Retests.
* Breakout-retest formations.
* Volume-confirmed breakouts.

A price moving marginally above resistance should not automatically be classified as a confirmed breakout.

Evaluate:

* Candle closing position.
* Price distance beyond resistance.
* Relative trading volume.
* Momentum.
* Market structure.
* Subsequent price confirmation.

Distinguish between developing, confirmed and invalidated formations.

## 5.4 Chart pattern recognition

Implement algorithms to detect the following patterns.

### Reversal formations

1. Double Bottom (W formation).
2. Double Top (M formation).
3. Triple Bottom.
4. Triple Top.
5. Head and Shoulders.
6. Inverse Head and Shoulders.
7. Rounding Bottom.
8. Rounding Top.
9. Broadening Formations.

### Continuation formations

1. Bullish Flag.
2. Bearish Flag.
3. Bullish Pennant.
4. Bearish Pennant.
5. Ascending Triangle.
6. Descending Triangle.
7. Symmetrical Triangle.
8. Rising Wedge.
9. Falling Wedge.
10. Rectangle Consolidation.
11. Channels.

### Additional price-action structures

1. Cup and Handle.
2. Inverse Cup and Handle.
3. Breakout Retest.
4. Bullish and Bearish Divergence.
5. Higher High / Higher Low formations.
6. Lower High / Lower Low formations.

For every detected pattern, determine:

* Pattern name.
* Formation start and end.
* Relevant price points.
* Pattern boundaries.
* Current formation status.
* Potential breakout direction.
* Confirmation conditions.
* Invalidation conditions.
* Historical performance, if available.

Do not classify a pattern merely because the chart visually resembles its shape.

Implement mathematical detection criteria wherever practical.

For example, a double-bottom detector should evaluate:

* Whether two meaningful swing lows exist.
* Whether their prices are sufficiently close.
* Whether a meaningful intervening recovery exists.
* Whether the distance between the troughs is reasonable.
* Whether a neckline can be identified.
* Whether the neckline has been broken.
* Whether volume supports the breakout.

Use configurable tolerances rather than arbitrary fixed thresholds.

The pattern-recognition engine should distinguish between:

* Developing pattern.
* Confirmed pattern.
* Invalidated pattern.
* Inconclusive formation.

Store the underlying detection evidence so that every classification can be explained and reproduced.

---

# 6. MODULE 3: CANDLESTICK PATTERN RECOGNITION

Develop a separate candlestick analysis engine.

The system should identify individual candles as well as multi-candle formations.

## 6.1 Single-candle patterns

Recognise:

* Doji.
* Dragonfly Doji.
* Gravestone Doji.
* Long-Legged Doji.
* Hammer.
* Hanging Man.
* Inverted Hammer.
* Shooting Star.
* Bullish Marubozu.
* Bearish Marubozu.
* Spinning Top.

## 6.2 Two-candle patterns

Recognise:

* Bullish Engulfing.
* Bearish Engulfing.
* Piercing Pattern.
* Dark Cloud Cover.
* Bullish Harami.
* Bearish Harami.
* Tweezer Bottom.
* Tweezer Top.
* Bullish Kicking.
* Bearish Kicking.

## 6.3 Three-candle patterns

Recognise:

* Morning Star.
* Evening Star.
* Morning Doji Star.
* Evening Doji Star.
* Three White Soldiers.
* Three Black Crows.
* Three Inside Up.
* Three Inside Down.
* Three Outside Up.
* Three Outside Down.

For every identified formation, provide:

1. Pattern name.
2. Candles involved.
3. Timestamp.
4. Bullish or bearish classification.
5. Pattern strength.
6. Context in which it appeared.
7. Volume confirmation.
8. Supporting or conflicting indicators.
9. Historical performance, if available.

An Evening Star appearing after a sustained uptrend should receive a different contextual interpretation from the same formation appearing during sideways movement.

Similarly, a Hammer near a significant support zone should be evaluated differently from one appearing randomly in the middle of a trend.

Use TA-Lib or another established technical-analysis library where appropriate.

Implement additional custom rules when necessary.

The candlestick engine must not treat every recognised formation as a reliable trading signal.

---

# 7. MODULE 4: TECHNICAL INDICATORS AND MOMENTUM ANALYSIS

Implement a comprehensive but configurable technical indicator engine.

## 7.1 Trend indicators

Calculate:

* Simple Moving Average (SMA).
* Exponential Moving Average (EMA).
* Weighted Moving Average (WMA).
* Moving Average Convergence Divergence (MACD).
* Average Directional Index (ADX).
* Parabolic SAR.
* Supertrend.

Suggested moving-average periods include:

* 9.
* 20.
* 50.
* 100.
* 200.

Do not assume these are universally optimal. Allow configuration.

## 7.2 Momentum indicators

Calculate:

* Relative Strength Index (RSI).
* Stochastic Oscillator.
* Stochastic RSI.
* Rate of Change.
* Williams %R.
* Commodity Channel Index.

Identify:

* Overbought conditions.
* Oversold conditions.
* Bullish divergence.
* Bearish divergence.
* Momentum acceleration.
* Momentum deterioration.

Do not assume an overbought stock must fall or an oversold stock must rise.

## 7.3 Volatility indicators

Calculate:

* Average True Range (ATR).
* Bollinger Bands.
* Standard deviation of returns.
* Historical volatility.
* Donchian Channels.
* Keltner Channels.

Use these measures to identify:

* Volatility expansion.
* Volatility contraction.
* Squeeze conditions.
* Abnormally large price movements.
* Potentially inappropriate stop-loss distances.

## 7.4 Volume indicators

Calculate:

* On-Balance Volume (OBV).
* Volume Weighted Average Price (VWAP).
* Accumulation/Distribution Line.
* Chaikin Money Flow.
* Money Flow Index.
* Relative Volume.
* Volume moving averages.

Detect:

* Volume breakouts.
* Volume contraction.
* Price-volume divergence.
* Buying pressure.
* Selling pressure.
* Potential accumulation.
* Potential distribution.

For intraday analysis, compare volume with historical volume at the same time of day.

Do not compare a 9:20 AM volume observation directly with an ordinary full-day average.

## 7.5 Indicator interpretation

Avoid generating a long list of indicator values without interpretation.

The system should explain what the indicators collectively suggest.

For instance:

* RSI indicates bullish momentum divergence.
* MACD histogram is expanding positively.
* Price is above the 50-period EMA.
* ADX indicates strengthening trend conditions.
* Relative volume is elevated.

The system should then identify whether these signals reinforce one another or contradict one another.

Avoid double-counting highly correlated indicators when calculating aggregate signal scores.

---

# 8. MODULE 5: MULTI-TIMEFRAME ANALYSIS

Implement a top-down analytical framework.

The system must examine multiple timeframes simultaneously.

For example:

| Timeframe | Primary purpose                              |
| --------- | -------------------------------------------- |
| Weekly    | Long-term market structure                   |
| Daily     | Medium-term trend and important price levels |
| 1-hour    | Intermediate market structure                |
| 15-minute | Short-term opportunities                     |
| 5-minute  | Entry timing                                 |

The system should identify:

* Whether the timeframes are aligned.
* Whether shorter-term momentum agrees with the broader trend.
* Whether a reversal on a shorter timeframe conflicts with the larger trend.
* Whether support or resistance levels coincide across timeframes.
* Whether a pattern is more significant because it appears on multiple timeframes.

For example:

Weekly: Bullish.

Daily: Consolidating.

1-hour: Bullish reversal developing.

15-minute: Resistance breakout.

5-minute: Pullback toward breakout level.

The system should explain that the short-term opportunity is developing within a broader bullish market structure.

It should also identify conflicting conditions.

A bullish 5-minute pattern against a strong weekly downtrend should not receive the same assessment as a bullish pattern aligned across all timeframes.

Do not invent higher-timeframe information when the uploaded dataset does not contain enough observations.

Clearly identify unavailable timeframes.

---

# 9. MODULE 6: QUANTITATIVE PATTERN PERFORMANCE RESEARCH

This module is particularly important.

The system should not merely identify patterns. It should investigate whether the identified patterns have historically demonstrated useful predictive value.

Build a historical pattern database using available OHLCV data.

## 9.1 Pattern occurrence database

Whenever a pattern is detected, record:

* Stock.
* Market.
* Timestamp.
* Timeframe.
* Pattern category.
* Pattern parameters.
* Relevant price levels.
* Technical indicators at detection.
* Volume characteristics.
* Broader market trend.
* Subsequent price movement.

This will gradually create a research dataset of historical technical formations.

## 9.2 Historical pattern evaluation

For each pattern, calculate:

* Number of occurrences.
* Number of successful formations.
* Number of failed formations.
* Percentage reaching target before stop-loss.
* Average favourable price movement.
* Average adverse price movement.
* Maximum favourable excursion.
* Maximum adverse excursion.
* Average time required to reach the target.
* Performance across different timeframes.
* Performance in bullish, bearish and sideways markets.

For example, investigate whether a Double Bottom formation performs better when:

* RSI exhibits bullish divergence.
* The second trough occurs near a major support zone.
* Volume increases during the recovery.
* The neckline breakout occurs on elevated volume.
* The broader timeframe is bullish.

The objective is to determine which combinations provide the strongest historical evidence.

## 9.3 Conditional pattern research

Test combinations such as:

Double Bottom + RSI Divergence.

Bullish Engulfing + Volume Expansion.

MACD Bullish Crossover + Price Above 50 EMA.

Ascending Triangle + Breakout Volume.

Falling Wedge + Support Confirmation.

Do not assume that these combinations are profitable.

Test them empirically.

---

# 10. MODULE 7: MACHINE LEARNING AND PREDICTIVE MODELLING

Introduce machine learning only after building the deterministic technical analysis engine.

The purpose of machine learning is to estimate the historical likelihood of different price outcomes, conditional on the features observed at the time a signal occurs.

## 10.1 Feature engineering

Create features using:

* Price returns.
* RSI.
* MACD.
* ADX.
* ATR.
* Moving-average distances.
* Volume ratios.
* Volatility.
* Trend classification.
* Pattern classification.
* Support/resistance proximity.
* Candlestick characteristics.
* Multi-timeframe alignment.
* Market index performance.

Avoid introducing features that accidentally contain future information.

## 10.2 Models to experiment with

Start with interpretable baseline models:

1. Logistic Regression.
2. Random Forest.
3. XGBoost.
4. LightGBM, where appropriate.

Compare their performance.

Do not introduce deep learning without demonstrating that simpler models are inadequate.

## 10.3 Prediction objectives

The model should eventually estimate probabilities such as:

* Probability of an upward movement over the next N candles.
* Probability of a downward movement.
* Probability of reaching a specified profit target before the stop-loss.
* Expected price movement over a specified horizon.
* Probability of a breakout being sustained.

The most useful initial objective should be:

P(Target reached before Stop-Loss | Current technical setup).

Define the target, stop-loss and maximum holding period before constructing the historical labels.

Use an appropriate event-based labelling methodology.

## 10.4 Model validation

Use chronological training and testing.

Never randomly shuffle time-series observations into conventional training and testing sets if that creates temporal leakage.

Implement:

* Training dataset.
* Validation dataset.
* Out-of-sample test dataset.
* Walk-forward validation.
* Appropriate treatment of overlapping future-return labels.

Where suitable, use purging and embargo techniques.

Evaluate:

* Precision.
* Recall.
* F1 score.
* ROC-AUC.
* PR-AUC.
* Brier score.
* Log loss.
* Probability calibration.

For trading applications, also evaluate the resulting strategy's performance after costs.

The model must not claim that it is highly accurate merely because it performs well on its training dataset.

---

# 11. MODULE 8: TRADING STRATEGY GENERATION

Once a potential trading opportunity has been identified, generate a structured trading plan.

The trading strategy generator should examine the combined evidence from the preceding modules.

It must be capable of proposing:

* Long positions.
* Short positions, where the market and trading instrument permit.
* Breakout trades.
* Reversal trades.
* Pullback entries.
* Momentum trades.
* Trend-following trades.
* No-trade decisions.

## 11.1 Entry identification

Determine potential entry conditions using:

* Breakout confirmation.
* Support/resistance interaction.
* Candlestick confirmation.
* Volume expansion.
* Momentum confirmation.
* Moving-average structure.
* Multi-timeframe alignment.

Differentiate between:

* Immediate market entry.
* Limit entry.
* Breakout entry.
* Pullback entry.
* Conditional entry.

Whenever possible, favour clearly defined conditional entry rules rather than recommending an arbitrary current price.

## 11.2 Stop-loss calculation

Develop a systematic stop-loss mechanism.

Potential methods include:

* Previous swing high/low.
* Support/resistance invalidation.
* ATR-based stop-loss.
* Pattern invalidation level.
* Volatility-adjusted stop-loss.

The system should explain why a particular stop-loss method was selected.

Avoid placing stop-losses at arbitrary fixed percentages without considering volatility and market structure.

## 11.3 Target calculation

Identify potential targets using:

* Previous resistance/support.
* Chart-pattern measured moves.
* Fibonacci extensions.
* ATR multiples.
* Historical price levels.
* Risk/reward requirements.

Allow multiple targets.

For example:

* Target 1: Conservative.
* Target 2: Base case.
* Target 3: Extended target.

## 11.4 Position sizing

Calculate position size from the user's predefined risk budget.

For a long position:

Risk per share = Entry Price - Stop-Loss Price.

Position Quantity = Maximum Acceptable Monetary Loss / Risk per Share.

Account for transaction costs, expected slippage and any applicable trading restrictions.

Do not assume the full calculated position can always be executed at the intended price.

## 11.5 Trading plan output

Generate a structured table:

| Parameter       | Analysis                             |
| --------------- | ------------------------------------ |
| Stock           | Stock identifier                     |
| Direction       | Bullish / Bearish / Neutral          |
| Trading style   | Intraday / Swing / Positional        |
| Entry condition | Exact trigger                        |
| Entry range     | Proposed price range                 |
| Stop-loss       | Price level                          |
| Target 1        | Price level                          |
| Target 2        | Price level                          |
| Target 3        | Price level                          |
| Risk per share  | Calculated value                     |
| Risk/reward     | Calculated ratio                     |
| Position size   | Calculated quantity                  |
| Setup validity  | Conditions required                  |
| Invalidation    | Conditions that invalidate the setup |
| Holding period  | Expected horizon                     |

If the evidence is insufficient, explicitly state:

NO TRADE — INSUFFICIENT EVIDENCE.

---

# 12. MODULE 9: CONFIDENCE SCORING AND RISK EVALUATION

Do not generate arbitrary confidence percentages.

Implement three distinct measures.

## 12.1 Pattern confidence

Measures the quality of pattern identification.

Potential components:

* Geometric fit.
* Swing-point significance.
* Price-level similarity.
* Pattern completeness.
* Volume confirmation.
* Breakout confirmation.

## 12.2 Trend confidence

Measures how strongly the available technical evidence supports the identified trend.

Potential components:

* Higher-high/higher-low structure.
* Moving-average alignment.
* ADX.
* Momentum indicators.
* Volume characteristics.
* Multi-timeframe agreement.

## 12.3 Trading probability

This is the most important measure.

It estimates the probability of achieving the proposed trading objective before the stop-loss, based on historical comparable observations and a validated predictive model.

The model should disclose:

* Estimated probability.
* Number of comparable historical observations.
* Relevant historical evaluation period.
* Validation methodology.
* Calibration performance.
* Uncertainty or confidence interval, where statistically justified.

If there is insufficient historical data, the model must report that the probability cannot be reliably estimated.

Do not substitute an arbitrary confidence score for a statistically estimated probability.

## 12.4 Risk classification

Classify each proposed setup as:

* Low risk.
* Moderate risk.
* High risk.
* Extremely high risk.

This classification must be based on clearly defined criteria and should not be confused with the probability of success.

Also identify:

* High volatility.
* Poor liquidity.
* Unfavourable risk/reward.
* Conflicting technical signals.
* Significant resistance near the entry.
* Unusually large spreads.
* Potential overnight or event-related gaps, where relevant data is available.

---

# 13. MODULE 10: VISUAL CHART ANNOTATION AND IMAGE ANALYSIS

This is a major functional requirement.

The application must support uploading a screenshot or image of a stock chart.

It should use a vision-capable model where available to interpret the visible chart.

## 13.1 Screenshot analysis

When the user uploads an image:

1. Identify the chart type.
2. Identify the visible timeframe, if displayed.
3. Identify the stock price axis.
4. Identify the time axis.
5. Examine visible price formations.
6. Identify potential support and resistance zones.
7. Recognise visible candlestick formations.
8. Identify apparent trendlines.
9. Identify potential breakouts and reversals.
10. Generate a visual annotation layer.

Do not pretend that exact numerical prices or timestamps can be extracted from every screenshot.

If the chart is cropped, distorted, low-resolution or missing axis labels, explicitly disclose this limitation.

Screenshot-only findings must be distinguished from findings verified against structured OHLCV data.

## 13.2 Annotated chart output

The application should return the uploaded chart with informative annotations.

Use the following visual conventions:

* Green horizontal lines: Support zones.
* Red horizontal lines: Resistance zones.
* Blue lines: Pattern boundaries and necklines.
* Green circles: Relevant swing lows.
* Red circles: Relevant swing highs.
* Yellow markers: Candlestick formations.
* Arrows: Potential directional movement.
* Highlighted regions: Consolidation zones.
* Shaded region: Potential entry zone.
* Red shaded region: Stop-loss zone.
* Green shaded region: Profit target zone.

These colours are conventions and should be consistently applied.

Every annotation should have a corresponding text explanation.

For example:

DOUBLE BOTTOM — POTENTIAL BULLISH REVERSAL

First trough: Identified swing low.

Second trough: Similar price level to the first trough.

Neckline: Intervening swing high.

Breakout status: Not yet confirmed.

Interpretation: A potential bullish reversal is developing. Confirmation requires a valid neckline breakout.

## 13.3 Interactive annotations

Users should be able to interact with the chart.

Clicking an annotation should reveal:

* Pattern name.
* Detection time.
* Price coordinates.
* Pattern status.
* Detection evidence.
* Technical interpretation.
* Supporting indicators.
* Trading implications.

Ensure the visual chart and numerical report use the same underlying analytical results.

Do not implement a chart annotation that is disconnected from the actual data used by the model.

## 13.4 Screenshot mode versus structured-data mode

Maintain two distinct analysis modes.

MODE A: IMAGE-BASED ANALYSIS

The system analyses the information visibly available in the screenshot.

It should provide qualitative observations and approximate measurements only where defensible.

MODE B: DATA-BASED ANALYSIS

The system receives structured OHLCV data and performs numerical analysis.

This is the authoritative analytical mode.

Whenever both an image and structured data are available, use structured data for calculations and the image as a visual reference.

---

# 14. MODULE 11: USER INTERFACE AND DASHBOARD

Build an interactive and professionally designed application.

The interface should feel like a combination of a financial research terminal and an intelligent trading analysis platform.

Avoid unnecessary visual clutter.

Use a clean, modern financial dashboard.

## 14.1 Main navigation

Create the following sections.

### A. Chart Analyzer

Primary interface.

Allow the user to:

* Enter a stock symbol.
* Select an exchange.
* Upload a CSV or Excel file.
* Upload a chart screenshot.
* Select a timeframe.
* Select a historical period.
* Configure technical indicators.
* Run the analysis.

Display:

* Candlestick chart.
* Volume chart.
* Technical indicators.
* Support and resistance levels.
* Trendlines.
* Pattern annotations.
* Historical signals.

### B. Technical Analysis Report

Display a detailed report containing:

1. Overall trend.
2. Market structure.
3. Support and resistance.
4. Detected chart patterns.
5. Candlestick formations.
6. Technical indicator readings.
7. Momentum analysis.
8. Volume analysis.
9. Multi-timeframe analysis.
10. Bullish evidence.
11. Bearish evidence.
12. Conflicting evidence.
13. Overall interpretation.

### C. Trading Strategy

Display:

* Potential trading direction.
* Entry conditions.
* Stop-loss.
* Profit targets.
* Risk/reward ratio.
* Position sizing.
* Pattern confidence.
* Trend confidence.
* Historical probability, if validated.
* Trade invalidation conditions.

### D. Pattern Research Lab

This should be a dedicated research interface.

Allow the user to select a technical pattern and investigate its historical performance.

For example:

Select: Double Bottom.

The application should display:

* Total occurrences detected.
* Confirmed occurrences.
* Failed occurrences.
* Target-hit percentage.
* Stop-loss-hit percentage.
* Average favourable movement.
* Average adverse movement.
* Average time to target.
* Performance by timeframe.
* Performance across different market regimes.

Allow filtering by:

* Stock.
* Timeframe.
* Historical period.
* Market condition.
* Pattern subtype.
* Supporting indicators.

### E. Backtesting Lab

Allow users to:

* Select a trading strategy.
* Configure entry conditions.
* Configure exit conditions.
* Select stop-loss and target methods.
* Configure holding periods.
* Set capital and risk parameters.
* Include transaction costs and slippage.
* Run historical backtests.

Display:

* Equity curve.
* Drawdown curve.
* Win rate.
* Profit factor.
* Sharpe ratio.
* Maximum drawdown.
* Expectancy.
* Number of trades.
* Average holding period.
* Performance by market condition.

### F. Analysis History

Maintain a record of previous analyses.

Allow users to revisit:

* Previous stocks.
* Previous charts.
* Earlier technical reports.
* Historical trading setups.
* Model predictions.
* Subsequent realised outcomes.

This is important for evaluating the system's real-world usefulness over time.

---

# 15. MODULE 12: AI-POWERED INTERPRETATION AND REPORT GENERATION

Integrate an LLM as an analytical communication layer.

The LLM should receive structured outputs from the technical and quantitative engines.

Its responsibility is to:

* Explain technical patterns.
* Interpret indicator readings.
* Connect different observations.
* Explain conflicting signals.
* Describe potential trading opportunities.
* Explain risk and reward.
* Generate comprehensive reports.
* Answer user questions about the analysis.

For example, when the technical analysis engine identifies a bearish head-and-shoulders formation, the LLM should explain:

* How the pattern developed.
* Where the neckline is located.
* Whether the neckline has been broken.
* Whether selling volume is increasing.
* Whether momentum supports the bearish interpretation.
* What would invalidate the bearish thesis.
* What trading opportunities may emerge.

The LLM should not independently calculate or invent market prices, indicator values, probabilities or trade levels.

Use validated values received from the underlying Python modules.

If a language-model API is unavailable, the application should still perform deterministic technical analysis and generate reports using templates.

---

# 16. BACKTESTING, VALIDATION AND RELIABILITY

This section is fundamental to the project's credibility.

The platform must not simply identify patterns and assume they are profitable.

Every proposed strategy must be capable of historical testing.

## 16.1 Historical testing

Use a chronological split.

For example:

* Development period: 2020–2023.
* Validation period: 2024.
* Out-of-sample testing: 2025.
* Subsequent evaluation: 2026, depending on available data.

The dates above are illustrative. Adjust them according to the actual dataset.

Never use future data when constructing historical trading signals.

## 16.2 Backtesting assumptions

Explicitly model:

* Brokerage.
* Exchange and statutory transaction charges.
* Taxes where applicable.
* Slippage.
* Bid/ask spread, where available.
* Liquidity constraints.
* Position sizing.
* Partial exits.
* Gap risk.
* Corporate actions.

When a historical candle touches both the stop-loss and target but the available data cannot establish which occurred first, adopt a conservative assumption or use finer-resolution data.

## 16.3 Performance metrics

Calculate:

* Total return.
* Annualised return, where meaningful.
* Win rate.
* Average winning trade.
* Average losing trade.
* Profit factor.
* Expectancy.
* Maximum drawdown.
* Sharpe ratio.
* Sortino ratio.
* Calmar ratio.
* Average holding period.
* Number of trades.

Never evaluate a strategy solely using win rate.

A strategy with a 40% win rate can be profitable if its reward-to-risk characteristics are favourable. A strategy with a 75% win rate can still lose money if its occasional losses are sufficiently large.

## 16.4 Paper trading

Create a future extension for paper trading.

Record each proposed trade at the time it is generated.

Track whether:

* Entry was triggered.
* Stop-loss was reached.
* Target was reached.
* The trade expired.
* The setup was invalidated.

This allows the system's predictions to be evaluated prospectively instead of relying exclusively on historical backtests.

Do not implement live order execution in the initial project.

---

# 17. TECHNOLOGY STACK

Use a modular Python-first architecture.

Recommended technologies:

### Backend and analytical engine

* Python.
* Pandas.
* NumPy.
* SciPy.
* Scikit-learn.
* XGBoost or LightGBM.
* TA-Lib, where available.
* Pydantic for data validation.

### Charting and visualisation

* Plotly for candlestick and analytical charts.
* TradingView Lightweight Charts as an optional advanced charting component.
* Matplotlib for research visualisations.

### Frontend

Use Streamlit for the initial application because it allows rapid development of an interactive analytical dashboard.

The architecture should permit migration to a more customised React-based frontend later without rewriting the underlying analytical engine.

### Database

Start with SQLite.

Keep the database abstraction compatible with PostgreSQL for future expansion.

Store:

* Stock information.
* Historical OHLCV data.
* Indicator values, if cached.
* Pattern detections.
* Trading signals.
* Backtesting results.
* User analysis history.

### Backtesting

Evaluate:

* Backtesting.py.
* VectorBT.

Choose the most suitable framework based on the strategy requirements.

### AI integration

Create a provider-independent interface for connecting an LLM.

Keep credentials in environment variables.

Do not make the core analytical engine dependent on a paid LLM API.

### Software engineering

* Modular codebase.
* Clear separation of concerns.
* Type hints.
* Meaningful comments.
* Logging.
* Unit tests.
* Error handling.
* Configuration management.
* Dependency pinning.
* Documentation.

Use currently maintained, compatible package versions and verify library documentation before implementation.

---

# 18. PROPOSED PROJECT DIRECTORY STRUCTURE

Keep the codebase organised.

A suggested structure is:

technical-analysis-engine/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── config/
│   ├── settings.py
│   └── indicator_config.py
│
├── data/
│   ├── uploads/
│   ├── processed/
│   └── historical/
│
├── data_engine/
│   ├── ingestion.py
│   ├── validation.py
│   ├── preprocessing.py
│   ├── resampling.py
│   └── providers/
│
├── analysis/
│   ├── indicators.py
│   ├── trend_analysis.py
│   ├── support_resistance.py
│   ├── volume_analysis.py
│   ├── momentum_analysis.py
│   └── multi_timeframe.py
│
├── patterns/
│   ├── swing_detection.py
│   ├── chart_patterns.py
│   ├── candlestick_patterns.py
│   ├── breakout_detection.py
│   └── pattern_scoring.py
│
├── quantitative/
│   ├── feature_engineering.py
│   ├── historical_patterns.py
│   ├── probability_estimation.py
│   ├── model_training.py
│   └── model_validation.py
│
├── strategies/
│   ├── strategy_generator.py
│   ├── entry_rules.py
│   ├── exit_rules.py
│   ├── stop_loss.py
│   ├── position_sizing.py
│   └── risk_management.py
│
├── backtesting/
│   ├── engine.py
│   ├── execution_model.py
│   ├── performance_metrics.py
│   └── walk_forward.py
│
├── vision/
│   ├── image_processing.py
│   ├── chart_interpretation.py
│   └── image_annotation.py
│
├── ai/
│   ├── llm_client.py
│   ├── report_generation.py
│   └── interpretation.py
│
├── visualization/
│   ├── candlestick_charts.py
│   ├── annotations.py
│   ├── dashboards.py
│   └── research_plots.py
│
├── database/
│   ├── models.py
│   ├── repository.py
│   └── database.py
│
└── tests/
├── test_data.py
├── test_indicators.py
├── test_patterns.py
├── test_strategies.py
└── test_backtesting.py

You may modify this structure where technically appropriate, but maintain modularity.

Do not place the entire application inside one large Python file.

---

# 19. DEVELOPMENT ROADMAP

Develop the project incrementally.

Do not attempt to implement every sophisticated feature simultaneously.

The objective is to produce a reliable working application at each stage.

## PHASE 1: CORE TECHNICAL ANALYSIS ENGINE

Priority: Highest.

Implement:

1. OHLCV data ingestion.
2. Data validation and preprocessing.
3. Multiple timeframe support.
4. Trend identification.
5. Swing high/low identification.
6. Support and resistance.
7. Technical indicators.
8. Candlestick recognition.
9. Basic chart-pattern detection.
10. Basic volume and momentum analysis.

Deliverable:

A working application where a user uploads stock market data and receives a detailed technical analysis.

## PHASE 2: VISUAL ANALYSIS AND DASHBOARD

Implement:

1. Interactive candlestick charts.
2. Volume visualisation.
3. Technical indicator overlays.
4. Pattern annotations.
5. Support/resistance lines.
6. Trendlines.
7. Screenshot uploads.
8. Image-based chart interpretation.
9. Interactive chart annotations.

Deliverable:

An application that visually identifies and explains relevant price-action patterns.

## PHASE 3: TRADING STRATEGY GENERATION

Implement:

1. Entry-condition identification.
2. Stop-loss calculation.
3. Profit-target calculation.
4. Risk/reward analysis.
5. Position sizing.
6. Multi-timeframe confirmation.
7. Pattern and trend scoring.
8. Structured trading recommendations.
9. No-trade classification.

Deliverable:

A trading strategy engine capable of generating conditional trade plans.

## PHASE 4: QUANTITATIVE RESEARCH AND MACHINE LEARNING

Implement:

1. Historical pattern database.
2. Pattern-performance analysis.
3. Feature engineering.
4. Machine learning models.
5. Historical outcome estimation.
6. Probability calibration.
7. Walk-forward testing.
8. Out-of-sample validation.

Deliverable:

A statistically validated predictive layer that estimates the historical likelihood of different trading outcomes.

## PHASE 5: ADVANCED INTEGRATION

Implement:

1. LLM-powered interpretation.
2. Comprehensive research reports.
3. Paper trading.
4. Analysis history.
5. Market data API integration.
6. Enhanced dashboard.
7. Performance monitoring.

Deliverable:

A fully integrated AI-powered technical analysis and trading research platform.

---

# 20. IMPORTANT DESIGN PRINCIPLES AND CONSTRAINTS

These instructions must be followed throughout development.

### A. Analytical reliability

Do not sacrifice correctness for feature quantity.

A smaller number of properly implemented pattern detectors is preferable to dozens of unreliable detectors.

### B. No arbitrary confidence percentages

Never generate probabilities without statistical evidence.

Explicitly distinguish between heuristic pattern scores and calibrated statistical probabilities.

### C. No look-ahead bias

Historical signals must only use information available at the time they would have been generated.

### D. No repainting

A pattern should not appear historically confirmed before the required confirmation data existed.

Store both its formation time and the time at which it became identifiable.

### E. No forced trading recommendations

The system must be able to recommend avoiding a trade.

### F. Explainability

Every technical signal should have a traceable explanation.

The user should be able to understand exactly why the system classified a stock as bullish, bearish or neutral.

### G. No fabricated data

Never invent prices, volume, indicator values, market conditions or historical results.

### H. Separation of analytical components

Keep technical analysis, quantitative research, machine learning and LLM interpretation independent.

### I. Realistic backtesting

Always consider costs, slippage, execution assumptions and liquidity.

### J. Security

Never expose API credentials.

Do not store sensitive broker credentials in source code or uploaded project files.

### K. Financial disclaimer

Position the application as a quantitative research and decision-support tool.

It must clearly communicate uncertainty and must not guarantee trading profits or imply that its estimates are certain investment outcomes.

---

# 21. INITIAL ACCEPTANCE CRITERIA

Before considering the first usable version complete, verify the following.

1. A user can upload a valid OHLCV CSV file.
2. The system correctly validates and processes the data.
3. The application can construct a candlestick chart.
4. The application can calculate the principal technical indicators.
5. The system can identify higher highs, higher lows, lower highs and lower lows.
6. The system can detect relevant support and resistance zones.
7. The system can recognise the initial set of candlestick patterns.
8. The system can detect basic formations such as double tops, double bottoms, triangles and head-and-shoulders patterns.
9. Each detected formation has identifiable price coordinates and a detection status.
10. Multiple timeframes can be analysed where sufficient data exists.
11. The application generates a coherent technical analysis report.
12. The application can identify potential trading opportunities and explain its entry, stop-loss and target logic.
13. Risk/reward calculations are mathematically correct.
14. Charts display analytical annotations corresponding to the actual underlying data.
15. The system clearly identifies insufficient or unreliable data.
16. Historical testing does not use future information.
17. The application runs locally using documented installation instructions.
18. Automated tests cover important analytical and financial calculations.

---

# 22. HOW I WANT YOU TO APPROACH THE DEVELOPMENT

Before writing code:

1. Understand the entire project architecture.
2. Identify potential technical limitations.
3. Evaluate the proposed libraries and tools.
4. Identify which features are feasible for the initial implementation.
5. Create a detailed implementation plan.
6. Establish the data structures and interfaces connecting the modules.

Then begin implementation.

Do not spend the entire development process writing theoretical explanations or producing architecture documents without building a functional application.

Build the project incrementally.

For each phase:

* Implement the required functionality.
* Test the code.
* Verify numerical calculations.
* Identify bugs and limitations.
* Document completed functionality.
* Maintain a working application.

Do not leave critical functions as empty placeholders or pretend that an unimplemented feature works.

Where a sophisticated feature cannot yet be implemented reliably, clearly identify it as a future extension.

If something in the proposed architecture is technically inefficient or unnecessarily complicated, you may improve it. However, preserve the project's central objective.

Prioritise a reliable, usable application over unnecessary complexity.

## FINAL OBJECTIVE

The final product should function as an intelligent financial technical analysis and trading research assistant.

A user should be able to provide stock market data or upload a stock chart and receive:

1. A comprehensive understanding of the stock's current price structure.
2. Identification of relevant chart and candlestick formations.
3. Analysis of trading volume, momentum and volatility.
4. Multi-timeframe trend evaluation.
5. Visually annotated charts explaining the detected patterns.
6. Potential trading opportunities with defined entry conditions.
7. Stop-loss and profit-target calculations.
8. Risk/reward and position-sizing analysis.
9. Statistically informed confidence estimates, where sufficient evidence exists.
10. Historical research showing how similar setups have performed.
11. A clear explanation of the reasoning behind every important conclusion.

The application should not simply tell the user what to trade.

It should explain what the market appears to be doing, why the identified pattern matters, what evidence supports the interpretation, what could invalidate it and how a trader could potentially capitalise on the opportunity.

The ultimate goal is to build a rigorous, interpretable and continuously improvable quantitative technical analysis platform that combines classical technical analysis, statistical research, machine learning and AI-powered interpretation.
