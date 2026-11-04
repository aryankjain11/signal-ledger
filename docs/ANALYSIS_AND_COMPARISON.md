# Analytical events and two-stock comparison

Implemented 2026-11-04. Scope is descriptive daily-data research; the new event
families do not replace the existing breakout strategy, create probabilities or
demonstrate an investment edge. Broader pattern/strategy catalogues remain pending.
Learning assignments remain paused. Rules and examples below are original.

## Where to find the features

- Research dashboard → **Analysis rules · breakout and retest**: reference lookback,
  breakout ATR buffer, relative-volume threshold and event expiry.
- Research dashboard → **Patterns & momentum**: breakout lifecycle, chart patterns,
  candle context, momentum facts, divergence observations and transition evidence.
- Workspace → **Compare two stocks**: synthetic preview or two CSV/XLSX uploads,
  including original NSE security-history downloads without manual edits.
- Report/evidence exports contain the new rules, events and momentum facts.
  Comparison exports contain source passports, alignment conventions and samples.

## Breakout/retest state machine (`research-events/1`)

Default reference is the previous 20 observations' highest high/lowest low,
excluding the candidate candle. A qualifying close must cross that level plus
0.1 previous-bar ATR and current volume must be at least 1.2 times its previous
20-observation mean. Lookback, close buffer, volume threshold and expiry are UI
controls; other exact parameters are recorded in the exported rules.

The reference level, previous ATR, break extreme and break RVOL freeze at that
event. A subsequent retest must touch the level's ±0.25 ATR band and close on the
held side. A close more than 0.5 frozen ATR on the wrong side fails the event.
Continuation requires a later close beyond the breakout candle's extreme plus
0.5 ATR, and cannot occur on the same candle as the first retest. The mirrored
rules describe downward breaks as observations; no new short strategy is added.

Failure takes precedence, then continuation, then expiry. At age 10 (default)
observations after the break, an unresolved event expires; a new retest is not
accepted on that deadline candle. Labels distinguish expiry with/without a held
retest. There is at most one active event per direction. A terminal bar cannot
simultaneously create another event of that direction. These are declared close-
based state conventions, not claims about the sequence of intrabar trades/fills.

Hypothetical: prior resistance 101, prior ATR2, qualifying close103 with RVOL2;
a later low101/close101.5 holds the retest. If a subsequent close exceeds the
break candle's high104 plus1, continuation is observed. A close below100 instead
fails the event. Reference prices are not recomputed from subsequent highs.

## Chart formations

New families: rectangle consolidation and ascending, descending and symmetrical
triangles. Use the latest three confirmed high and low pivots, alternating in
formation order. Anchor span must be 10–120 observations, using the existing
fixed three-right-bar pivot confirmation delay. Fit separate upper/lower lines.
Maximum anchor residual must be <=0.5 ATR at first eligibility. Initial width
must be >=2 ATR and width at detection >=0.5 ATR.

- Rectangle: each boundary's total fitted change over the anchor span <=0.5 ATR.
- Ascending triangle: upper change within0.5 ATR; lower rises >=1 ATR.
- Descending triangle: lower change within0.5 ATR; upper falls >=1 ATR.
- Symmetrical triangle: upper falls and lower rises by >=1 ATR each.
- Triangles must contract to less than85% of initial fitted width at detection.

Freeze both line fits and reference ATR at eligibility. A close beyond an extended
boundary by0.1 ATR confirms its direction. Crossing boundaries invalidate the
geometry; an unresolved shape expires at40 observations. A shape already outside
its boundary when its final anchor becomes knowable is reported then, not backdated.
Events store anchor and boundary coordinates, fitted slopes, residual and widths.
Existing double-top/bottom definitions remain separate. Head-and-shoulders,
flags, wedges and other requested families are not implemented by this increment.

## Candlestick context

Added Hammer, Hanging man, Inverted hammer, Shooting star, Morning Star and Evening
Star. Preceding context uses the close change from index i−5 to i−1, requiring
at least one preceding ATR in the relevant direction. It excludes the shape's
first candle. Body/wick variants require positive body <=35% of total range,
the long shadow >=2 bodies and the opposite shadow <=1 body. The preceding
direction distinguishes the paired names.

Stars require first body >=0.5 preceding ATR, middle body <=30% of first near its
appropriate half, and an opposite-color third body >=50% of first closing past
the first body's midpoint. This explicit variant does **not** require a gap.
All three candles must close before detection. Existing doji/engulfing observations
remain geometry-only; this increment does not silently add context to them.

## Momentum and divergence

Added ROC10 =100×(close/close ten observations earlier−1), fast stochastic %K14
=100×(close−14-bar low)/(14-bar high−14-bar low), and three-observation %D.
A zero stochastic range is undefined; no value is fabricated. The panel also
explains RSI bands (>55, <45, middle) and distinguishes MACD histogram sign from
its latest change. These descriptive thresholds are not calibrated probabilities.

RSI and MACD divergences compare successive same-kind confirmed pivots 5–60
observations apart. Price must extend by >0.25 ATR in one direction while RSI
moves >=2 points, or MACD >=0.02 ATR, oppositely. Indicator values are sampled
at pivot **formation**, with observation availability delayed until the second
pivot's **confirmation**. Event evidence records both values and dates. No reversal
or profitable entry is inferred from a divergence alone.

## Comparison and correlation

Accept two standard/NSE stock-history CSV/XLSX files. Require completed daily INR
observations and record each price-basis declaration. UDiFF ZIPs and action-ledger
application are not supported on this comparison page. Adjustments, identities,
calendar completeness and dividend treatment are not independently verified.

Select a common date interval. Shared price observations are rebased to100 at
the first common date. Relative performance is A's indexed series divided by B's;
above1 means A has outperformed B since that chosen start. Shared-observation
drawdown is value/running maximum−1. Missing observations can hide path extremes.

Compute each stock's simple returns on its **native** observation intervals,
then pair only returns with matching start **and** end dates. No filling, date
shifting or bridging an unmatched interval. For example, a Tuesday return starting
Monday must not be paired with one starting Friday because Monday was absent.
Matching multi-calendar-day intervals can occur across weekends/gaps; this method
does not claim complete exchange-session coverage.

Display Pearson correlation of paired returns, Spearman rank correlation and
rolling Pearson correlation (default20 paired intervals, configurable5–252).
Overall coefficients require ten matched returns. Effectively constant series
(sample standard deviation <=1e−12) return unavailable, not zero. Spearman ranks
returns rounded to12 decimals to stabilize numeric ties. Rolling coefficients
require a full window of nonconstant pairs. Fewer than60 pairs raises a small-
sample warning. Rank rounding is recorded in exported evidence.

Metrics: endpoint price return, observed-date drawdown and sample standard
deviation (ddof1) per matched return interval. Volatility is not annualized. The
comparison is not dividend-inclusive total return, a causation claim, a cointegration
test or a pairs-trading strategy. Both charts use the selected period; indicators
use each file's uploaded history through its end for causal warm-up. Charts are
independent, not synchronized crosshairs. Source and result exports stay local.

## References and verification

- [Fidelity: Fast Stochastic](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/fast-stochastic).
- [Fidelity: RSI and divergence](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI).
- [Zerodha Varsity: Morning/Evening Star](https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-3/).
- [NIST: correlation coefficient](https://www.itl.nist.gov/div898/software/dataplot/refman2/ch2/correlat.pdf).

Code and exact fixtures: `quant_engine/research.py`, `comparison.py` and their UI
modules; `tests/test_research.py` and `tests/test_comparison.py`. Tests include
positive/negative formations, close-time rules, volume filters, mirrored directions,
future-append invariance, exact return/drawdown arithmetic, missing-date alignment,
constant returns, warm-up, duplicate chart content and two native NSE uploads.
Actual measured test/browser/GitHub results are recorded in WORK_LOG.md.
