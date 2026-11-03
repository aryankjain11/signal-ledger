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


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.DataFrame
    metrics: dict

