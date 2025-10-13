from __future__ import annotations
import numpy as np
import pandas as pd

def generate_cpu_series(minutes: int = 180, spike_at: int | None = 60, drift_at: int | None = 120, seed: int = 7) -> pd.DataFrame:
    """Generate a synthetic CPU utilization time series with optional anomalies.

    - Baseline: ~40% CPU with noise.
    - Spike anomaly: brief spike to ~95% around `spike_at` minute.
    - Drift anomaly: gradual linear drift upward after `drift_at` minute.

    Returns a DataFrame with columns: ['minute', 'cpu_util'].
    """
    rng = np.random.default_rng(seed)
    t = np.arange(minutes, dtype=float)
    noise = rng.normal(0, 2.0, size=minutes)
    base = 40 + 2*np.sin(2*np.pi*t/60.0) + noise  # diurnal-ish wiggle
    cpu = base.copy()

    if spike_at is not None and 0 <= spike_at < minutes:
        width = 4
        for i in range(spike_at, min(spike_at + width, minutes)):
            cpu[i] += 50 * np.exp(-0.5 * ((i - spike_at)/1.0) ** 2)  # sharp spike

    if drift_at is not None and 0 <= drift_at < minutes:
        drift = np.linspace(0, 25, minutes - drift_at)
        cpu[drift_at:] += drift

    cpu = np.clip(cpu, 0, 100)
    df = pd.DataFrame({'minute': t.astype(int), 'cpu_util': cpu.astype(float)})
    return df

def save_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
