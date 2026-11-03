"""Generate a repeatable software fixture. Never present this as market data."""
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    rng = np.random.default_rng(73021)
    n = 600
    t = np.arange(n)
    returns = 0.0003 + 0.002 * np.sin(t / 35) + rng.normal(0, 0.012, n)
    close = 100 * np.exp(np.cumsum(returns))
    opening = np.r_[close[0], close[:-1]] * np.exp(rng.normal(0, 0.003, n))
    width = rng.uniform(0.002, 0.018, n)
    high = np.maximum(opening, close) * (1 + width)
    low = np.minimum(opening, close) * (1 - width)
    volume = (rng.lognormal(12.8, 0.4, n) * (1 + np.abs(returns) * 30)).astype(int)
    frame = pd.DataFrame({"date": pd.bdate_range("2023-01-02", periods=n).strftime("%Y-%m-%d"),
                          "open": opening.round(4), "high": high.round(4), "low": low.round(4),
                          "close": close.round(4), "volume": volume})
    target = Path(__file__).resolve().parents[1] / "data" / "synthetic_daily.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)


if __name__ == "__main__":
    main()
