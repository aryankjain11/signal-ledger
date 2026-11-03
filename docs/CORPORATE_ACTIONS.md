# Split/bonus action ledger and adjusted research

Implemented scope: optional user-reviewed split/bonus events, consistent OHLCV
normalization, cutoff-aware replay and auditable exports. No exchange action feed
is connected. Dividend/total-return calculations, rights, mergers/demergers,
automatic ratio parsing and portfolio entitlement/settlement accounting remain pending.

## Use the feature

Keep the original NSE price CSV unchanged. Upload it normally, then open
**Corporate actions · splits and bonus issues → Use a corporate-action ledger**.
Upload a separate reviewed CSV using the format below. Choose Original prices
for an audit or Split/bonus adjusted research for normalized charts/indicators.
Adjusted mode requires the input price basis to be declared Unadjusted OHLC;
unknown/already-adjusted sources are rejected to prevent double adjustment.

```csv
action_id,symbol,ex_date,known_on,action_type,shares_before,shares_after,source
demo-split,DEMOCA,2026-06-03,2026-05-29,split,1,2,Synthetic fixture
demo-bonus,DEMOCA,2026-06-05,2026-06-04,bonus,1,2,Synthetic fixture
```

These rows are invented fixtures, not actual events. The UI provides both this
ledger and matching synthetic price data for functional preview. A ledger can
contain other symbols, but selected actions must match the dataset's passport
symbol/research label exactly (case-insensitive). That label can originate in a
filename and is not independent proof of listing identity.

`shares_after` is **total resulting shares**, not additional bonus shares. A 1:1
bonus therefore has before=1, after=2; a 2:1 bonus has before=1, after=3. A split
from one share into two has before=1, after=2. Reverse splits are supported by
the inverse ratio. Each event needs a unique ID, explicit ex-date and source.

`known_on` is a user declaration of the first date this exact event record became
knowable, available at that day's close. It is not independently verified. A late
correction can have known_on after its ex-date; earlier replay must not use it.
Date-only declarations do not provide intraday point-in-time guarantees.

## Calculation and replay contract

Let q = shares_after / shares_before. For each known event effective by the
selected cutoff, every **pre-ex-date** open/high/low/close is divided by q and
share volume is multiplied by q. The ex-date and later bars remain in their new
units. Multiple actions compose multiplicatively. All dates and values stay
unaltered in the preserved original source; transformed results are separate.

Hypothetical six-session raw closes 200, 204, 102, 104, 52, 54, with a 2-for-1
split on session 3 and 1:1 bonus on session 5, normalize to 50, 51, 51, 52, 52, 54
at the final cutoff. Earlier equivalent-share volumes scale inversely to prices.
The price-times-volume product is preserved under the normalization convention;
this is not a claim about exact future trading prices or economic return.

Only events with known_on <= cutoff are considered. Announced events whose
ex-date is later than the cutoff are disclosed but not applied. Events not yet
known at the cutoff are excluded from the numerical result and visible event
details. Replaying to session 3 uses only the split, with closes 100, 102, 102.
No later bonus is used to rebase that earlier research view.

The full source dataset ID and normalized source hash remain unchanged. A separate
research-view ID records the source ID, action adapter/version, mode, cutoff,
ledger hash and result hash. The passport's analyzed-data hash fingerprints the
actual transformed slice. Raw-visible data, audit JSON and per-date factors can
be downloaded independently. Original input warnings remain in the audit metadata;
adjusted price-jump warnings are recomputed from the transformed series.

## Guards and limitations

- Reject duplicate IDs, simultaneous same-symbol/ex-date events, unsupported
  action types, malformed dates/ratios, missing references and unobserved effective
  ex-dates inside the visible range. Simultaneous split-plus-bonus needs a later
  explicit composite-event design; a guessed event order is not accepted.
- CSV limit: 1 MB and 1,000 events. Ratio counts are positive integers at most
  one million, with a nontrivial resulting ratio between 0.0001 and 10,000.
- No split/dividend detection from price jumps. No completeness or source
  authentication claim. An incomplete ledger can still produce misleading research.
- Applying an action-audited dataset twice is rejected. Input price-basis claims
  still need review; the application cannot detect a false unadjusted declaration.
- No interpolation or duplicate dropping, and no assumption that a bonus share
  is tradable immediately when credited/listed. This is a normalization layer.
- Adjusted research **disables trade sizing/plans and backtests**. Original-price
  views with known effective events in their range also disable execution. The
  current simulator does not model changing holdings/lot units or entitlements.
  Engine-level guards accompany the UI restriction. Original workflows without an
  action ledger retain their documented exploratory/unverified-action limitations.

## References and verification

- [NSE corporate-action records](https://www.nseindia.com/companies-listing/corporate-filings-actions): reference point for reviewing real actions and ex-dates.
- [NSE investor material on bonus, splits and dividends](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Corporate_Action_Dividends_Bonus_splits_etc.pdf): distinguishes resulting share counts and bonus ratios. Explanations and examples above are original; the source document is not bundled.

`tests/test_corporate_actions.py` covers exact and reverse ratios, cumulative
factors, all OHLC plus volume, unchanged raw inputs, cutoff isolation, late-known
corrections, bad/ambiguous files, missing ex-date bars, repeated adjustment,
passport/hash consistency and UI/engine execution restrictions. Actual results
are recorded in WORK_LOG.md after execution. Learning assignments remain paused.
