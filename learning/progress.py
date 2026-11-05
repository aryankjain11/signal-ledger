"""Original five-phase brief mapped to current implementation, independent of exercises."""
from collections import Counter

from .roadmap import TASKS

# Complete means the stated current behavior exists; partial never claims the full
# original feature catalogue or empirical validity. Keep original phase item order.
PHASES = [
    ("1", "Core technical analysis engine", [
        ("done", "OHLCV data ingestion", "Single-stock standard CSV/XLSX and native NSE history downloads; UDiFF import is a separate preview."),
        ("partial", "Data validation and preprocessing", "Strict OHLCV, NSE CM 2026 calendar audit and reviewed split/bonus research adjustments; broader calendars, automatic action reconciliation and provider checks remain."),
        ("partial", "Multiple timeframe support", "Daily plus conservative prior-week context; configurable intraday/monthly alignment pending."),
        ("partial", "Trend identification", "Basic confirmed HH/HL/LH/LL; richer strength/range/reversal classifications pending."),
        ("done", "Swing high/low identification", "Confirmed fixed three-left/right pivots with formation and knowability dates."),
        ("partial", "Support and resistance", "Pivot-cluster zones; dynamic levels, trendlines and advanced scoring pending."),
        ("partial", "Technical indicators", "Starter averages/RSI/MACD/ATR/Bollinger/OBV/RVOL plus ROC10 and fast stochastic; complete catalogue pending."),
        ("partial", "Candlestick recognition", "Doji/engulfing plus six contextual shadow/star variants; remaining families and validation pending."),
        ("partial", "Basic chart-pattern detection", "Double top/bottom, triangle/rectangle prototypes and breakout/retest states; head-and-shoulders and broader validation pending."),
        ("partial", "Basic volume and momentum analysis", "RSI/MACD/ROC/stochastic context and delayed pivot divergences; broader volume/divergence research pending."),
    ]),
    ("2", "Visual analysis and dashboard", [
        ("done", "Interactive candlestick charts", "Plotly zoom, hover and replay."),
        ("done", "Volume visualisation", "Daily share-volume bars."),
        ("done", "Technical indicator overlays", "Supported averages/bands and indicator panels."),
        ("partial", "Pattern annotations", "Supported events and pivots; full pattern catalogue pending."),
        ("partial", "Support/resistance lines", "Clustered zones displayed; expanded level/line system pending."),
        ("planned", "Trendlines", "Causal trendline/channel fitting not implemented."),
        ("planned", "Screenshot uploads", "No image-ingestion workflow yet."),
        ("planned", "Image-based chart interpretation", "No screenshot analysis yet."),
        ("partial", "Interactive chart annotations", "Hover reveals evidence; editing annotations/history pending."),
    ]),
    ("3", "Trading strategy generation", [
        ("partial", "Entry-condition identification", "One explicit long breakout rule; wider strategy catalogue pending."),
        ("partial", "Stop-loss calculation", "Fixed-at-entry ATR stop; other stop methods pending."),
        ("partial", "Profit-target calculation", "Fixed reward multiple; structural/alternative targets pending."),
        ("done", "Risk/reward analysis", "Gross and cost-aware reward/risk for the baseline."),
        ("done", "Position sizing", "Whole-share cash, risk and prior-volume caps with estimated costs."),
        ("planned", "Multi-timeframe confirmation", "Weekly context exists, but no completed strategy confirmation framework."),
        ("planned", "Pattern and trend scoring", "No validated score or calibrated probability."),
        ("partial", "Structured trading recommendations", "Conditional baseline plan and limitations; broader plan catalogue pending."),
        ("done", "No-trade classification", "Explicit unavailable/no-executable-baseline outcomes."),
    ]),
    ("4", "Quantitative research and machine learning", [
        ("planned", "Historical pattern database", "No persisted occurrence/outcome store."),
        ("partial", "Pattern-performance analysis", "Auditable single-stock forward outcomes, MFE/MAE, context baselines, overlap/censoring and descriptive distributions; dependent uncertainty and held-out validation pending."),
        ("partial", "Feature engineering", "Deterministic indicator/event outputs; versioned training labels/datasets pending."),
        ("planned", "Machine learning models", "Not implemented."),
        ("partial", "Historical outcome estimation", "Versioned 1/5/10/20-observation default pattern-outcome studies and portable records; target/stop labels, database and predictive validation pending."),
        ("planned", "Probability calibration", "No success probabilities are supplied."),
        ("planned", "Walk-forward testing", "No frozen walk-forward selection/evaluation pipeline."),
        ("planned", "Out-of-sample validation", "No held-out performance study; software tests are separate evidence."),
    ]),
    ("5", "Advanced integration", [
        ("planned", "LLM-powered interpretation", "Reports are deterministic; no LLM provider is connected."),
        ("partial", "Comprehensive research reports", "Starter Markdown/JSON exports; broader integrated research report pending."),
        ("planned", "Paper trading", "No prospective paper ledger."),
        ("planned", "Analysis history", "No saved-run database/history workflow."),
        ("planned", "Market data API integration", "Offline uploads only; typing a ticker does not fetch data."),
        ("partial", "Enhanced dashboard", "Research, pattern/momentum panels and two-stock comparison/correlation plus reference/build workspaces; full requested dashboard pending."),
        ("planned", "Performance monitoring", "No production operational/model-drift monitoring."),
    ]),
]


def progress_rows():
    return [{"Phase": f"{number} · {name}", "Status": status.title(), "Feature": title, "Current scope / remaining": detail}
            for number, name, items in PHASES for status, title, detail in items]


def progress_markdown():
    counts = Counter(t["status"] for t in TASKS)
    lines = ["# Project status against the original plan", "Updated: 2026-11-05",
        "Current position: working local daily-data research prototype. Parts of original phases 1, 2 and 3 are usable, and phase 4 now includes descriptive pattern-outcome research. No complete original phase or final-product acceptance is claimed. Phase 4 databases/ML/validation and most phase 5 integration remain pending.",
        "Learning assignments are paused at the owner's request. Product implementation, testing, records and GitHub synchronization continue. Existing reference pages remain available.",
        f"Expanded master checklist: {len(TASKS)} work items — {counts['done']} done, {counts['partial']} partial, {counts['planned']} planned, {counts['optional']} optional. Counts are not effort estimates or a meaningful project-completion percentage.",
        "This document maps every one of the original five-phase roadmap's 43 implementation bullets (brief §19). Detailed subfeatures and the original acceptance-criteria audit are in MASTER_CHECKLIST.md; the complete brief is ORIGINAL_BRIEF.md.",
        "Calendar scope: offline NSE CM 2026 snapshot with specified amendments and special sessions. Missing observations are review candidates, not a claim of broken source data. Reviewed split/bonus ledgers support research normalization; automatic action reconciliation, dividends/total returns, share-accounting execution, other calendar years/exchanges and live updates remain pending."]
    for number, title, items in PHASES:
        lines += [f"## Phase {number} · {title}"]
        lines += [f"- [{'x' if status == 'done' else ' '}] **{status.title()} · {name}** — {scope}" for status, name, scope in items]
    lines += ["## Build support and immediate sequence",
        "- [x] Local app, source/tests, private GitHub repository and automated test workflow.",
        "- [x] Original NSE security-history CSV support, data passports and source/replay hashes.",
        "- [x] Reviewed split/bonus action ledger, replay-aware adjusted research, raw/factor/audit exports and execution restrictions.",
        "- [x] Build journal, detailed checklist and downloadable status records.",
        "- [x] Initial breakout/retest, chart/candle/momentum feature bundle and matched-interval two-stock comparison.",
        "- [x] After the pattern workspace: causal forward outcomes, MFE/MAE, retrospective context baselines, per-horizon censoring, overlap spacing, occurrence inspection and portable study exports.",
        "- [ ] Full real-file acceptance for UDiFF report import; separate from security-history CSV support.",
        "- [ ] Wider historical calendars; automatic corporate-action feeds, dividends/total returns and share-accounting backtests.",
        "- [ ] Continue structure/indicator improvements, then one pattern/strategy family at a time.",
        "- [ ] Persist research events/results, freeze validation, then add statistical/model layers.",
        "Actual local/remote checks and verified source commits are recorded in WORK_LOG.md and GITHUB_SYNC.md. A test workflow is not proof of investment performance. Live execution is outside the authorized scope."]
    return "\n\n".join(lines) + "\n"
