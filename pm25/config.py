"""Paths and settings shared by the whole project."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEASUREMENTS_FILE = ROOT / "data" / "raw" / "measurements.csv"
STATIONS_FILE = ROOT / "data" / "raw" / "stations.csv"

MODEL_FILE = ROOT / "models" / "model.joblib"
RESULTS_DIR = ROOT / "results"
EVALUATION_FILE = RESULTS_DIR / "evaluation.csv"
OUT_OF_FOLD_FILE = RESULTS_DIR / "out_of_fold.csv"
PREDICTIONS_FILE = RESULTS_DIR / "predictions.csv"
MAP_FILE = ROOT / "docs" / "map.html"  # docs/ is what GitHub Pages publishes

TARGET = "pm25"

# Station characteristics given to the model, taken from stations.csv
NUMERIC_FEATURES = [
    "n_connections", "n_exits", "latitude", "longitude",
    "platform_length", "depth", "station_area", "opening_year",
]
# Text columns turned into 0/1: the value given here becomes 1
BINARY_FEATURES = {"platform_layout": "island"}

# Columns that describe a measurement but are not features
ID_COLUMNS = ["type", "station_a", "station_b", "line", "hour"]

SEED = 42
N_FOLDS = 3
N_REPEATS = 10
VALIDATION_MODES = ["random", "revisit", "station_group"]

HOURS = list(range(5, 24))
