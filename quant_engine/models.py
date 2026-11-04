from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class Settings:
    capital: float = 100_000.0
    risk_fraction: float = 0.01
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    participation: float = 0.01
    lookback: int = 20
    stop_atr: float = 2.0
    reward_risk: float = 2.0
    max_hold: int = 10
    pivot_window: int = 3

    def __post_init__(self):
        import math

        values = (self.capital, self.risk_fraction, self.fee_bps,
                  self.slippage_bps, self.participation, self.stop_atr,
                  self.reward_risk, self.lookback, self.max_hold, self.pivot_window)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Settings must be finite numbers.")
        if self.capital <= 0 or not 0 < self.risk_fraction <= 0.1:
            raise ValueError("Capital must be positive; risk must be in (0, 10%].")
        if not 0 <= self.fee_bps <= 100 or not 0 <= self.slippage_bps <= 100:
            raise ValueError("Costs must be between 0 and 100 basis points per side.")
        if not 0 < self.participation <= 0.1:
            raise ValueError("Participation must be in (0, 10%].")
        if self.stop_atr <= 0 or self.reward_risk <= 0:
            raise ValueError("Stop and reward multiples must be positive.")
        if any(type(x) is not int or x < 1 for x in
               (self.lookback, self.max_hold, self.pivot_window)):
            raise ValueError("Lookback, holding period and pivot window must be positive integers.")


@dataclass
class ValidatedData:
    bars: pd.DataFrame
    warnings: list[str]
    source_hash: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Pivot:
    kind: str
    index: int
    confirmed_at: int
    price: float
    timestamp: str
    detected_at: str


@dataclass
class Analysis:
    frame: pd.DataFrame
    pivots: list[Pivot]
    events: list[dict]
    zones: list[dict]
    trend: str
    structure: str
    evidence: list[str]
    weekly: dict
    setup: dict
    warnings: list[str] = field(default_factory=list)
    momentum: dict = field(default_factory=dict)
    rules: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchRules:
    lookback: int = 20
    breakout_buffer_atr: float = 0.1
    min_relative_volume: float = 1.2
    retest_tolerance_atr: float = 0.25
    invalidation_atr: float = 0.5
    retest_window: int = 10
    continuation_atr: float = 0.5
    candle_trend_bars: int = 5

    def __post_init__(self):
        import math
        if type(self.lookback) is not int or not 5 <= self.lookback <= 252:
            raise ValueError("Breakout lookback must be 5–252 observations.")
        if type(self.retest_window) is not int or not 2 <= self.retest_window <= 60:
            raise ValueError("Retest window must be 2–60 observations.")
        if type(self.candle_trend_bars) is not int or not 3 <= self.candle_trend_bars <= 30:
            raise ValueError("Candle context must be 3–30 observations.")
        for value in (self.breakout_buffer_atr, self.min_relative_volume, self.retest_tolerance_atr,
                      self.invalidation_atr, self.continuation_atr):
            if not math.isfinite(value) or not 0 <= value <= 10:
                raise ValueError("Research thresholds must be finite and between 0 and 10.")
        if self.invalidation_atr < self.breakout_buffer_atr:
            raise ValueError("Invalidation buffer must be at least the breakout buffer.")


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.DataFrame
    metrics: dict

