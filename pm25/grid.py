"""What the model is asked to predict."""

import pandas as pd


def build_grid(stations, hours, measurements=None):
    """
    Every underground station at every hour, plus the rides found in the measurements.
    Elevated stations are left out since the model only learned from underground ones.
    Rides that were never measured cannot be added: the code does not know which
    stations follow each other on a line.
    """
    places = stations.loc[~stations["outdoor"], ["name", "line"]]
    places = places.rename(columns={"name": "station_a"}).assign(type="platform", station_b=None)
    if measurements is not None:
        rides = measurements.loc[measurements["type"] == "onboard", ["type", "station_a", "station_b", "line"]]
        places = pd.concat([places, rides.drop_duplicates()], ignore_index=True)
    grid = places[["type", "station_a", "station_b", "line"]].merge(pd.DataFrame({"hour": hours}), how="cross")

    # Coordinates of both ends, for the map
    coords = stations[["name", "line", "latitude", "longitude"]]
    start = coords.rename(columns={"name": "station_a", "latitude": "lat_a", "longitude": "lon_a"})
    end = coords.rename(columns={"name": "station_b", "latitude": "lat_b", "longitude": "lon_b"})
    grid = grid.merge(start, on=["station_a", "line"], how="left")
    grid = grid.merge(end, on=["station_b", "line"], how="left")
    return grid
