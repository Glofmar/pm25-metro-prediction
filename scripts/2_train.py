"""Train the model on all the measurements and save it."""

import joblib

from pm25 import config
from pm25.data import load_dataset
from pm25.model import make_model

_, X, y = load_dataset()
model = make_model().fit(X, y)

config.MODEL_FILE.parent.mkdir(exist_ok=True)
joblib.dump(model, config.MODEL_FILE, compress=3)
print(f"Model trained on {len(y)} measurements")
