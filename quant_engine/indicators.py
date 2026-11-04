import numpy as np
import pandas as pd


def wilder(series: pd.Series, period: int) -> pd.Series:
    """Arithmetic seed of first period valid observations, then Wilder recursion."""
    output = pd.Series(np.nan, index=series.index, dtype=float)
    valid = series.dropna()
    if len(valid) < period:
        return output
    start = series.index.get_loc(valid.index[period - 1])
    value = float(valid.iloc[:period].mean())
    output.iloc[start] = value
    for i in range(start + 1, len(series)):
        value = (value * (period - 1) + series.iloc[i]) / period
        output.iloc[i] = value
    return output


def indicators(bars: pd.DataFrame) -> pd.DataFrame:
    frame = bars.copy()
    close = frame.close
    for period in (20, 50, 200):
        frame[f"sma_{period}"] = close.rolling(period).mean()
    for period in (20, 50):
        frame[f"ema_{period}"] = close.ewm(span=period, adjust=False, min_periods=period).mean()
    delta = close.diff()
    gain = wilder(delta.clip(lower=0), 14)
    loss = wilder(-delta.clip(upper=0), 14)
    frame["rsi_14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    frame.loc[(loss == 0) & (gain > 0), "rsi_14"] = 100.0
    frame.loc[(loss == 0) & (gain == 0), "rsi_14"] = 50.0
    tr = pd.concat([frame.high - frame.low, (frame.high - close.shift()).abs(),
                    (frame.low - close.shift()).abs()], axis=1).max(axis=1)
    frame["atr_14"] = wilder(tr, 14)
    fast = close.ewm(span=12, adjust=False, min_periods=12).mean()
    slow = close.ewm(span=26, adjust=False, min_periods=26).mean()
    frame["macd"] = fast - slow
    frame["macd_signal"] = frame.macd.ewm(span=9, adjust=False, min_periods=9).mean()
    frame["macd_histogram"] = frame.macd - frame.macd_signal
    std = close.rolling(20).std(ddof=0)
    frame["bb_upper"] = frame.sma_20 + 2 * std
    frame["bb_lower"] = frame.sma_20 - 2 * std
    prior_volume = frame.volume.shift().rolling(20).mean()
    frame["relative_volume"] = frame.volume / prior_volume.replace(0, np.nan)
    frame["obv"] = (np.sign(delta).fillna(0) * frame.volume).cumsum()
    frame["roc_10"] = 100 * (close / close.shift(10) - 1)
    lowest, highest = frame.low.rolling(14).min(), frame.high.rolling(14).max()
    frame["stoch_k_14"] = 100 * (close - lowest) / (highest - lowest).replace(0, np.nan)
    frame["stoch_d_3"] = frame.stoch_k_14.rolling(3).mean()
    return frame
