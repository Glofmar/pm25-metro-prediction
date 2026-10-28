"""Cross-validation of the model."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from pm25.model import make_model


def evaluate(X, y, splits):
    """
    Train and test a fresh model on each split. Returns the scores of each split, and for
    each measurement its average prediction over the splits where it was in the test set.
    """
    y = np.asarray(y)
    scores = []
    predictions = [[] for _ in y]
    for train, test in splits:
        model = make_model().fit(X.iloc[train], y[train])
        predicted = model.predict(X.iloc[test]).clip(min=0)
        for row, value in zip(test, predicted):
            predictions[row].append(value)
        scores.append({
            "r2": r2_score(y[test], predicted),
            "rmse": np.sqrt(mean_squared_error(y[test], predicted)),
            "mae": mean_absolute_error(y[test], predicted),
        })
    average = np.array([np.mean(p) if p else np.nan for p in predictions])
    return pd.DataFrame(scores), average
