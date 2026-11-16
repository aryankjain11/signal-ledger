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
    return extended_indicators(frame, tr)


def supertrend(frame: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> tuple[pd.Series, pd.Series]:
    """Standard final-band recursion; direction +1 (line below price) / -1 (above).

    Each value uses only the current and earlier bars.
    """
    tr = pd.concat([frame.high - frame.low, (frame.high - frame.close.shift()).abs(),
                    (frame.low - frame.close.shift()).abs()], axis=1).max(axis=1)
    atr = wilder(tr, period).to_numpy()
    mid = ((frame.high + frame.low) / 2).to_numpy()
    close = frame.close.to_numpy()
    n = len(frame)
    line = np.full(n, np.nan)
    direction = np.full(n, np.nan)
    upper = lower = np.nan
    for i in range(n):
        if not np.isfinite(atr[i]):
            continue
        basic_upper, basic_lower = mid[i] + multiplier * atr[i], mid[i] - multiplier * atr[i]
        if not np.isfinite(upper):  # seed
            upper, lower, d = basic_upper, basic_lower, 1 if close[i] >= mid[i] else -1
        else:
            upper = basic_upper if basic_upper < upper or close[i - 1] > upper else upper
            lower = basic_lower if basic_lower > lower or close[i - 1] < lower else lower
            prev = direction[i - 1]
            d = (1 if close[i] > upper else -1) if prev == -1 else (-1 if close[i] < lower else 1)
        direction[i] = d
        line[i] = lower if d == 1 else upper
    return pd.Series(line, frame.index), pd.Series(direction, frame.index)


def extended_indicators(frame: pd.DataFrame, tr: pd.Series) -> pd.DataFrame:
    """Second-wave indicator catalogue (trend strength, volatility channels, money flow).

    All are trailing calculations: value at row i uses rows <= i only.
    """
    close, high, low, volume = frame.close, frame.high, frame.low, frame.volume
    # ADX / directional movement (Wilder, 14)
    up, down = high.diff(), -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0).where(up.notna())
    minus_dm = down.where((down > up) & (down > 0), 0.0).where(down.notna())
    atr = frame.atr_14
    frame["plus_di_14"] = 100 * wilder(plus_dm, 14) / atr.replace(0, np.nan)
    frame["minus_di_14"] = 100 * wilder(minus_dm, 14) / atr.replace(0, np.nan)
    di_sum = (frame.plus_di_14 + frame.minus_di_14).replace(0, np.nan)
    dx = 100 * (frame.plus_di_14 - frame.minus_di_14).abs() / di_sum
    frame["adx_14"] = wilder(dx, 14)
    frame["supertrend"], frame["supertrend_dir"] = supertrend(frame)
    # Channels
    frame["donchian_high_20"] = high.rolling(20).max()
    frame["donchian_low_20"] = low.rolling(20).min()
    frame["keltner_upper"] = frame.ema_20 + 2 * atr
    frame["keltner_lower"] = frame.ema_20 - 2 * atr
    frame["squeeze_on"] = ((frame.bb_upper < frame.keltner_upper) & (frame.bb_lower > frame.keltner_lower)).astype(float).where(
        frame.bb_upper.notna() & frame.keltner_upper.notna())
    # Money flow
    span = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / span).fillna(0.0)
    flow = multiplier * volume
    frame["ad_line"] = flow.cumsum()
    frame["cmf_20"] = flow.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)
    typical = (high + low + close) / 3
    raw_flow = typical * volume
    positive = raw_flow.where(typical.diff() > 0, 0.0).where(typical.diff().notna())
    negative = raw_flow.where(typical.diff() < 0, 0.0).where(typical.diff().notna())
    pos, neg = positive.rolling(14).sum(), negative.rolling(14).sum()
    frame["mfi_14"] = (100 - 100 / (1 + pos / neg.replace(0, np.nan))).where(neg != 0, 100.0).where(pos.notna())
    frame.loc[(pos == 0) & (neg == 0), "mfi_14"] = 50.0
    frame["vwap_20"] = raw_flow.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)
    # Oscillators
    hh, ll = high.rolling(14).max(), low.rolling(14).min()
    frame["williams_r_14"] = -100 * (hh - close) / (hh - ll).replace(0, np.nan)
    tp_mean = typical.rolling(20).mean()
    mad = typical.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    frame["cci_20"] = (typical - tp_mean) / (0.015 * mad.replace(0, np.nan))
    rsi_low, rsi_high = frame.rsi_14.rolling(14).min(), frame.rsi_14.rolling(14).max()
    frame["stoch_rsi_14"] = 100 * (frame.rsi_14 - rsi_low) / (rsi_high - rsi_low).replace(0, np.nan)
    # Volatility and range position
    log_returns = np.log(close).diff()
    frame["hv_20"] = log_returns.rolling(20).std() * np.sqrt(252) * 100
    frame["atr_pct"] = 100 * atr / close
    frame["high_52w"] = high.rolling(252, min_periods=252).max()
    frame["low_52w"] = low.rolling(252, min_periods=252).min()
    return frame
