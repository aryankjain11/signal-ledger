# Upload an original NSE stock-history download

Use **Research dashboard → Upload daily data**, choose the original CSV, and
confirm that its rows are completed daily sessions. No renaming, date conversion,
comma removal, column deletion or row reversal is required. Keep the downloaded
`Quote-Equity-…-EQ-…csv` filename so the stock label can be inferred.

This path accepts the security-history format supplied by the owner, with DATE,
SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, CLOSE, VWAP, 52 WEEK HIGH/LOW, VOLUME,
VALUE and NO. OF TRADES. Header case/whitespace and a UTF-8 BOM are tolerated.
Long OHLC Price names and Total Traded Quantity are recognized in this format too.

## Automatic interpretation

1. Detect the security-history header signature, distinct from standard OHLCV.
2. Convert explicit DD-Mon-YYYY or ISO dates without guessing numeric locale.
3. Validate Indian/international comma grouping before converting OHLCV to numbers.
4. Use CLOSE, not LTP or PREV. CLOSE; use VOLUME/traded quantity, not VALUE/turnover.
5. Require EQ series throughout, reject conflicting identity and duplicate dates,
   validate OHLCV, and sort observations from oldest to newest.
6. Record the original file hash and conversion policy in the data passport.

Hypothetical example: CLOSE `1,240.00` becomes 1240.00; VOLUME `23,34,553`
becomes 2334553 shares. If LTP says 1248, the analyzed close is still 1240.
Commas are presentation characters; removing valid grouping changes the encoding,
not the quoted economic value. A malformed `12,34` is rejected, not guessed.

Missing dashes, invalid dates/numbers, mixed series and impossible OHLC are errors.
No zero replacement, interpolation, duplicate dropping or corporate-action
adjustment is performed. Extra columns are ignored rather than misinterpreted.

## Identity and history length

The observed export has no symbol/ISIN field. A recognized filename supplies a
stock-label hint only; it cannot authenticate origin or security continuity.
If renamed, enter a research label yourself. A supplied symbol column must contain
one nonblank symbol and agree with a recognized filename.

Three observations allow analysis, but each indicator has its own warm-up. One
month cannot supply long moving averages or all baseline-strategy context.
Download a longer period for those features. Adjustment basis remains a user
declaration: recognizing formatting does not certify a split/dividend policy.

## Different from UDiFF

Security-history CSV = one stock across many dates → **Upload daily data**.
UDiFF bhavcopy CSV/ZIP = many stocks for one date → **Import NSE daily reports**.
The latter's full current-schema/real-report acceptance gate remains pending.
Acceptance of a stock-history CSV does not close the UDiFF gate.

## Learning and evidence

The concept library entry **NSE stock-history CSV: close, LTP, volume and value**
explains the fields. Fixtures contain invented values in the observed schema;
the owner's downloaded data stays outside source control. Local verification uses
the supplied file without modifying or redistributing it. Actual results are
recorded in WORK_LOG.md after observation.

Exercise: inspect Data & exports → How this upload was interpreted. Explain which
price and volume fields were used and why formatting conversion is not a corporate
action adjustment. Learner mastery is never automatically marked complete.
