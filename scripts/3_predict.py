"""Predict PM2.5 for every underground station (and every measured ride), from 5:00 to 23:00."""

import joblib

from pm25 import config
from pm25.data import load_measurements, load_stations
from pm25.features import build_features
from pm25.grid import build_grid

stations = load_stations()
grid = build_grid(stations, config.HOURS, load_measurements())
X = build_features(grid, stations)

model = joblib.load(config.MODEL_FILE)
grid["pm25_pred"] = model.predict(X[model.feature_names_in_]).clip(min=0).round(2)

config.RESULTS_DIR.mkdir(exist_ok=True)
grid.to_csv(config.PREDICTIONS_FILE, index=False)
print(f"{len(grid)} predictions")
