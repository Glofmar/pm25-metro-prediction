"""The model used everywhere in the project."""

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pm25.config import SEED


def make_model():
    # Missing station characteristics are replaced by the median of the training data
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("forest", RandomForestRegressor(n_estimators=200, random_state=SEED, n_jobs=1)),
    ])
