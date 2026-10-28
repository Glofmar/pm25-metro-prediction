"""Draw the predictions on an interactive map."""

import pandas as pd

from pm25 import config
from pm25.maps import make_map

predictions = pd.read_csv(config.PREDICTIONS_FILE, dtype={"line": str})
make_map(predictions, config.MAP_FILE)
print(f"Map saved to {config.MAP_FILE.relative_to(config.ROOT)}")
