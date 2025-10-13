from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass
class AnomalyResult:
    indices: list[int]
    scores: np.ndarray
    threshold: float

def rolling_zscore_anomalies(series: pd.Series, window: int = 30, threshold: float = 3.0) -> AnomalyResult:
    """Simple rolling z-score anomaly detector.

    z_t = (x_t - mean_{t-window:t}) / std_{t-window:t}
    Flags anomalies where |z_t| >= threshold.

    Returns indices (int positions), all scores array, and the threshold used.
    """
    x = series.astype(float).to_numpy()
    if len(x) < window + 2:
        raise ValueError("Series too short for chosen window.")

    means = pd.Series(x).rolling(window=window, min_periods=window).mean().to_numpy()
    stds = pd.Series(x).rolling(window=window, min_periods=window).std(ddof=0).to_numpy()
    z = np.zeros_like(x)
    valid = stds > 1e-6
    z[valid] = (x[valid] - means[valid]) / stds[valid]
    z[~valid] = 0.0

    anomalies = np.where(np.abs(z) >= threshold)[0].tolist()
    return AnomalyResult(indices=anomalies, scores=z, threshold=threshold)

def naive_forecast(series: pd.Series, horizon: int = 10, window: int = 30) -> np.ndarray:
    """Naive rolling-mean forecast for baseline comparison."""
    rolling_mean = series.rolling(window=window, min_periods=min(window, len(series))).mean()
    last = float(rolling_mean.iloc[-1])
    return np.full(horizon, last, dtype=float)
