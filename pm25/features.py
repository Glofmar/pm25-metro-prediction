"""
Turn measurements into the numbers given to the model.

The same function is used for training and for prediction. A platform measurement
gets the characteristics of its station; an onboard measurement (a ride from
station_a to station_b) gets the average of its two stations.
"""

import numpy as np
import pandas as pd

from pm25 import config


def build_features(measurements, stations):
    measurements = measurements.reset_index(drop=True)
    table = station_table(stations)

    # For a platform, both ends of the "ride" are the same station
    end = measurements["station_b"].where(measurements["type"] == "onboard", measurements["station_a"])
    start_features = lookup(table, measurements["station_a"], measurements["line"])
    end_features = lookup(table, end, measurements["line"])
    # If one station is missing from stations.csv, the other one is used alone
    X = (start_features.fillna(end_features) + end_features.fillna(start_features)) / 2

    # One column per line of stations.csv, so the columns are the same whatever the data
    lines = pd.Categorical(measurements["line"], categories=sorted(stations["line"].unique()))
    line_columns = pd.get_dummies(lines, prefix="line").astype(int)

    angle = 2 * np.pi * measurements["hour"] / 24
    X["hour_sin"] = np.sin(angle)
    X["hour_cos"] = np.cos(angle)
    X["onboard"] = (measurements["type"] == "onboard").astype(int)
    return pd.concat([line_columns, X], axis=1)


def station_table(stations):
    """Station characteristics as numbers, one row per (name, line)."""
    table = stations[["name", "line"] + config.NUMERIC_FEATURES].copy()
    for column, value in config.BINARY_FEATURES.items():
        table[column] = (stations[column] == value).astype(float).where(stations[column].notna())
    return table


def lookup(table, names, lines):
    """Characteristics of the given stations, in the same order."""
    wanted = pd.DataFrame({"name": names.to_numpy(), "line": lines.to_numpy()})
    found = wanted.merge(table, on=["name", "line"], how="left")
    return found.drop(columns=["name", "line"]).astype(float)
