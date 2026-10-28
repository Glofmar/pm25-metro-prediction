"""Reading the input files."""

import pandas as pd

from pm25 import config
from pm25.features import build_features


def load_measurements():
    # station_b is empty for platform measurements, so force it to text
    return pd.read_csv(config.MEASUREMENTS_FILE, dtype={"line": str, "station_a": str, "station_b": str})


def load_stations():
    return pd.read_csv(config.STATIONS_FILE, dtype={"line": str})


def load_dataset():
    """Return the measurements, their features X and the target y."""
    measurements = load_measurements()[config.ID_COLUMNS + [config.TARGET]]
    X = build_features(measurements, load_stations())
    y = measurements[config.TARGET].to_numpy()
    return measurements, X, y
