"""
Cross-validate the model with each validation mode. Also saves, for station_group, the
prediction of every measurement by models that never saw its station.
"""

import pandas as pd

from pm25 import config
from pm25.data import load_dataset
from pm25.evaluation import evaluate
from pm25.validation import make_splits

measurements, X, y = load_dataset()
summary = []
for mode in config.VALIDATION_MODES:
    scores, predictions = evaluate(X, y, make_splits(measurements, mode))
    summary.append({"mode": mode, "mae": scores["mae"].mean(), "rmse": scores["rmse"].mean(),
                    "r2": scores["r2"].mean(), "r2_std": scores["r2"].std(ddof=0)})
    if mode == "station_group":
        out_of_fold = measurements.assign(pm25_pred=predictions.round(2))

summary = pd.DataFrame(summary).round(3)
print(summary.to_string(index=False))

config.RESULTS_DIR.mkdir(exist_ok=True)
summary.to_csv(config.EVALUATION_FILE, index=False)
out_of_fold.to_csv(config.OUT_OF_FOLD_FILE, index=False)
