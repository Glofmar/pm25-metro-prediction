# Data

The code reads two CSV files from `data/raw/`: `measurements.csv`, with one row per PM2.5 measurement, and `stations.csv`, with one row per station and line. Both are in this repository. This page first describes the format the code expects, for anyone who wants to use their own data, then how the Seoul files were built.

## Expected format

### Platform and onboard measurements

A measurement is either taken in a station (`platform`) or inside a train between two stations (`onboard`). A platform measurement describes one station, `station_a`, and gets that station's characteristics. An onboard measurement describes the ride from `station_a` to the next station `station_b`; it gets the average of the two stations' characteristics, and a feature called `onboard` tells the model that the air was measured in a train, which can differ from the air on a platform.

Onboard measurements come from field campaigns where a portable sensor is carried along the lines, one reading on the platform and one during the ride to the next station. That is how the code was first used, in Paris. The Seoul data only has fixed monitors in stations, so all its measurements are platform measurements (the exact position of each monitor in the station is not published).

Both kinds can be mixed. In cross-validation a ride counts for both of its stations, so it is never tested on a station the model has already seen. On the map, rides are drawn as segments between their two stations. Only rides that appear in the measurements can be predicted, since the code does not know which stations follow each other.

### measurements.csv

| Column | Type | Content |
|---|---|---|
| `type` | text | `platform` or `onboard` |
| `station_a` | text | the station, or the departure station of a ride |
| `station_b` | text | the arrival station of a ride; empty for a platform |
| `line` | text | the line, for example `2` or `7bis` |
| `hour` | integer, 0 to 23 | hour of the day |
| `pm25` | number | PM2.5 in µg/m³, the value the model learns to predict |

Other columns are ignored.

### stations.csv

| Column | Type | Content |
|---|---|---|
| `name` | text | station name, spelled exactly as in `measurements.csv` |
| `line` | text | the line; a station served by two lines has two rows |
| `latitude`, `longitude` | number | position of the station |
| `outdoor` | `True` / `False` | elevated or open-air station; these are not predicted, since the model learns from underground stations |
| other columns | number or text | the station characteristics given to the model (see below) |

The characteristics used with the Seoul data are:

| Column | Content |
|---|---|
| `n_connections` | number of lines serving the station |
| `n_exits` | number of exits |
| `latitude`, `longitude` | position |
| `platform_length` | platform length, in metres |
| `depth` | depth of the platform below ground, in metres |
| `station_area` | floor area, in m² |
| `opening_year` | year the station opened |
| `platform_layout` | `island`, `side` or `mixed`; the model gets 1 for an island platform and 0 otherwise |

They are listed in `pm25/config.py`: `NUMERIC_FEATURES` for the columns used as numbers, and `BINARY_FEATURES` for text columns turned into 0 or 1. To use other characteristics, change these two lists. Other columns of `stations.csv` are ignored.

### Features computed by the code

`pm25/features.py` gives the model the station characteristics above, the line as one 0/1 column per line of `stations.csv`, the hour as a sine and a cosine (so that 23:00 is close to 0:00), and the `onboard` flag. None of them comes from the PM2.5 values. Missing values are replaced by the median of the training data.

### Things to check

Station names and lines must match exactly between the two files. A measurement whose station is missing from `stations.csv` silently gets median values instead of its own characteristics, so check the spelling. Lines are read as text, which means that `2` and `2.0` are different. The hours shown on the map are set by `HOURS` in `pm25/config.py` (5 to 23).

## How the Seoul data was built

Both files come from open data published by Seoul Metro (서울교통공사) on the [Seoul Open Data Plaza](https://data.seoul.go.kr), under the [Korea Open Government License type 1](https://www.kogl.or.kr/info/licenseType1.do), which allows reuse, modification and redistribution as long as the source is credited. The files here are a modified version of the original data: readings were filtered and aggregated, columns renamed and station names made consistent, as described below.

| Dataset | Used for |
|---|---|
| [OA-22459](https://data.seoul.go.kr/dataList/OA-22459/L/1/datasetView.do), archive of 2025-08-20 | hourly PM2.5, April to December 2021 |
| [OA-22534](https://data.seoul.go.kr/dataList/OA-22534/S/1/datasetView.do) | station list and coordinates |
| [OA-11572](https://data.seoul.go.kr/dataList/OA-11572/F/1/datasetView.do), 2021 version | platform layout and length, floors, area, opening year |
| [OA-13305](https://data.seoul.go.kr/dataList/OA-13305/F/1/datasetView.do), 2021 version | platform depth |
| [OA-22449](https://data.seoul.go.kr/dataList/OA-22449/L/1/datasetView.do) | exits |
| [OA-22521](https://data.seoul.go.kr/dataList/OA-22521/S/1/datasetView.do) | transfers between lines |

`stations.csv` lists the 276 stations and lines of lines 1 to 8 with their coordinates, joined with the 2021 architecture and depth tables, 2021 being the year of the measurements. `n_exits` counts the exits of the station and `n_connections` the lines that serve it. Elevated stations are marked `outdoor`. Some files use older names (stations renamed since 2021) or short forms, which were matched by hand to the station list.

`measurements.csv` comes from about 1.7 million hourly readings of monitors in underground stations. Readings flagged as faulty by the operator (inspection, malfunction, power cut, repair, temporary zero) were removed, as were weekends, public holidays and the hours before 5:00. For each station, line and hour, we then took the median over April to December 2021. This gives 4,750 rows, 19 hours for each of 250 stations. Nine stations of the line 7 extension towards Bupyeong are missing from the station list and were left out.
