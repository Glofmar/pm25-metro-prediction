"""
Ways of splitting the measurements into training and test sets.

random         plain shuffled K-fold. Optimistic: other measurements of a test station
               are usually in the training set.
revisit        for each place measured more than once, one measurement is kept for testing.
station_group  K-fold over stations: all the measurements of a station are on the same side,
               whatever the line. A ride is tested only if both its stations are test
               stations, and used for training only if neither is.

Each split is repeated N_REPEATS times with a different seed, because with a few hundred
stations the scores change a lot from one draw to another.
"""

import numpy as np
from sklearn.model_selection import KFold

from pm25 import config


def make_splits(measurements, mode):
    """List of (train rows, test rows) pairs."""
    measurements = measurements.reset_index(drop=True)
    splits = []
    for repeat in range(config.N_REPEATS):
        seed = config.SEED + repeat
        if mode == "random":
            splits += list(KFold(config.N_FOLDS, shuffle=True, random_state=seed).split(measurements))
        elif mode == "revisit":
            splits.append(revisit_split(measurements, seed))
        elif mode == "station_group":
            splits += station_splits(measurements, seed)
        else:
            raise ValueError(f"unknown validation mode: {mode}")
    return splits


def revisit_split(measurements, seed):
    rng = np.random.default_rng(seed)
    places = measurements.fillna({"station_b": ""}).groupby(["station_a", "station_b", "line"])
    test = [rng.choice(rows) for rows in places.indices.values() if len(rows) > 1]
    train = np.setdiff1d(np.arange(len(measurements)), test)
    return train, np.sort(test)


def station_splits(measurements, seed):
    # Grouped by station name only: a station served by two lines has close readings
    # on both, so its lines must not end up on different sides
    start = measurements["station_a"]
    end = measurements["station_b"].fillna(start)
    stations = np.array(sorted(set(start) | set(end)))
    np.random.default_rng(seed).shuffle(stations)

    splits = []
    for test_stations in np.array_split(stations, config.N_FOLDS):
        start_in_test, end_in_test = start.isin(test_stations), end.isin(test_stations)
        train = np.flatnonzero(~start_in_test & ~end_in_test)
        test = np.flatnonzero(start_in_test & end_in_test)
        splits.append((train, test))
    return splits
