"""Modul mit vektorisierten numerischen Berechnungen fuer CityBike-Daten."""

import numpy as np


def compute_distances_between_stations(
    latitudes: np.ndarray, longitudes: np.ndarray
) -> np.ndarray:
    """Berechnet eine paarweise Distanzmatrix aus Breiten- und Laengengraden."""
    lat = np.asarray(latitudes, dtype=float)
    lon = np.asarray(longitudes, dtype=float)
    if lat.ndim != 1 or lon.ndim != 1:
        raise ValueError("latitudes and longitudes must be 1D arrays")
    if lat.size != lon.size:
        raise ValueError("latitudes and longitudes must have the same length")

    lat_diff = lat[:, np.newaxis] - lat[np.newaxis, :]
    lon_diff = lon[:, np.newaxis] - lon[np.newaxis, :]
    return np.sqrt(lat_diff**2 + lon_diff**2)


def compute_trip_vectorized_stats(
    durations: np.ndarray, distances: np.ndarray
) -> dict[str, dict[str, float]]:
    """Berechnet zentrale Statistikkennzahlen fuer Dauer- und Distanzarrays."""
    dur = np.asarray(durations, dtype=float)
    dist = np.asarray(distances, dtype=float)
    if dur.ndim != 1 or dist.ndim != 1:
        raise ValueError("durations and distances must be 1D arrays")

    def _stats(values: np.ndarray) -> dict[str, float]:
        return {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "p25": float(np.percentile(values, 25)),
            "p50": float(np.percentile(values, 50)),
            "p75": float(np.percentile(values, 75)),
        }

    return {"durations": _stats(dur), "distances": _stats(dist)}


def compute_batch_fares(
    distances: np.ndarray, base_fare: float = 1.0, per_km_rate: float = 0.5
) -> np.ndarray:
    """Berechnet Tarifkosten fuer mehrere Distanzen in einem vektorisierten Schritt."""
    dist = np.asarray(distances, dtype=float)
    return base_fare + dist * per_km_rate


def zscore_outlier_mask(values: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """Liefert eine boolesche Maske fuer Ausreisser auf Basis des Z-Scores."""
    arr = np.asarray(values, dtype=float)
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0:
        return np.zeros(arr.shape, dtype=bool)
    z = (arr - mean) / std
    return np.abs(z) > threshold
