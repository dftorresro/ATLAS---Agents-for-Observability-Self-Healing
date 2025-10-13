from atlas.data.simulated_metrics import generate_cpu_series
from atlas.models.anomaly import rolling_zscore_anomalies

def test_rolling_zscore_finds_spike():
    df = generate_cpu_series(minutes=120, spike_at=60, drift_at=None, seed=42)
    res = rolling_zscore_anomalies(df["cpu_util"], window=20, threshold=2.5)
    assert len(res.indices) >= 1
