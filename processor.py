"""
Consolidated processing: validation, feature extraction (statistical + frequency),
and CSV save/format helpers. Keeps existing functionality intact.
"""

from typing import Dict, List
import numpy as np
import pandas as pd


# Configuration-like constants
REQUIRED_COLUMNS = ["timestamp", "x", "y", "z"]
MIN_SAMPLES_REQUIRED = 5
EPS = 1e-12


def _validate(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if len(df) < MIN_SAMPLES_REQUIRED:
        raise ValueError("Insufficient data for processing")


def _compute_statistical(df: pd.DataFrame) -> Dict[str, float]:
    feats: Dict[str, float] = {}
    for col, prefix in [("x", "X"), ("y", "Y"), ("z", "Z")]:
        series = df[col]
        feats[f"mean_{prefix}"] = float(series.mean())
        feats[f"std_{prefix}"] = float(series.std())
        feats[f"min_{prefix}"] = float(series.min())
        feats[f"max_{prefix}"] = float(series.max())
        # Use float64 and add small epsilon for numerical stability
        arr = series.values.astype(np.float64, copy=False)
        rms = float(np.sqrt(np.mean(arr * arr) + EPS))
        feats[f"rms_{prefix}"] = rms
        feats[f"p2p_{prefix}"] = float(series.max() - series.min())
        feats[f"crest_{prefix}"] = float(max(abs(series.max()), abs(series.min())) / rms) if rms > 0 else 0.0
    feats["sample_count"] = int(len(df))
    return feats


def _compute_frequency(df: pd.DataFrame, sampling_rate_hz: float) -> Dict[str, float]:
    feats: Dict[str, float] = {}
    for col, prefix in [("x", "X"), ("y", "Y"), ("z", "Z")]:
        data = df[col].values.astype(np.float64, copy=False)
        if len(data) < 2:
            continue
        window = np.hanning(len(data))
        windowed = data * window
        # Use rfft for real-input FFT (half-spectrum) for performance
        fft_vals = np.fft.rfft(windowed)
        n = len(data)
        freqs = np.fft.rfftfreq(n, d=1.0 / sampling_rate_hz)
        mags = np.abs(fft_vals) / (np.sum(window) + EPS)
        if len(mags) == 0:
            continue
        feats[f"fft_{prefix}_max"] = float(np.max(mags))
        dom_idx = int(np.argmax(mags))
        feats[f"freq_{prefix}_dominant"] = float(freqs[dom_idx])
        denom = float(np.sum(mags) + EPS)
        feats[f"freq_{prefix}_mean"] = float(np.sum(freqs * mags) / denom)
        for low, high in [(0, 10), (10, 50), (50, 100)]:
            mask = (freqs >= low) & (freqs < high)
            energy = float(np.sum((mags[mask]) ** 2))
            feats[f"energy_{prefix}_{low}_{high}Hz"] = energy
    return feats


def process_batch(readings: List[Dict], sampling_rate_hz: float) -> Dict[str, float]:
    if not readings:
        return {}
    df = pd.DataFrame(readings)
    # Normalize names from sensor readings to expected columns
    df = df.rename(columns={"x_axis": "x", "y_axis": "y", "z_axis": "z"})
    # Ensure numeric
    for c in ["x", "y", "z"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    _validate(df)
    feats = {}
    feats.update(_compute_statistical(df))
    feats.update(_compute_frequency(df, sampling_rate_hz))
    feats["timestamp_start"] = float(df["timestamp"].min())
    feats["timestamp_end"] = float(df["timestamp"].max())
    feats["duration"] = float(df["timestamp"].max() - df["timestamp"].min())
    return feats


def format_csv(features: Dict[str, float]) -> str:
    if not features:
        return ""
    keys = sorted(features.keys())
    header = ",".join(keys)
    row = ",".join(str(features[k]) for k in keys)
    return f"{header}\n{row}"



