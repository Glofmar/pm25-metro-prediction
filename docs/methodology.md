# Methodology

The method works for any metro network that provides the two files described in [data/README.md](../data/README.md#expected-format), a list of PM2.5 measurements and a table of station characteristics. We use the Seoul metro as an example because its data is open, and the figures on this page come from it.

## What is predicted

The model predicts the PM2.5 level of a station, or of a ride between two stations, at a given hour, using only what is known about the station without measuring it. In the Seoul example, each observation is the typical level of a station at one hour of a working day (the median over April to December 2021). That makes 4,750 observations for 250 stations, or 217 physical stations since some are served by two lines.

The model gets 20 features describing the station, its line and the hour; they are listed in [data/README.md](../data/README.md#features-computed-by-the-code). None of them is computed from the PM2.5 values, and the same function builds them for training and for prediction (`pm25/features.py`).

## Model

A random forest of 200 trees, after replacing missing values by the median and scaling the features (`pm25/model.py`). The median and the scaling are part of the model, so during cross-validation they are computed on the training data only.

## Evaluation

Measurements of the same station look alike. In the Seoul example each station appears 19 times, once per hour, so with a plain random split the model sees a station at 8:00 during training and is then asked about the same station at 9:00. It only has to remember the station, and the score looks much better than it really is.

`pm25/validation.py` has three ways of splitting the data:

| Mode | Split | Question it answers |
|---|---|---|
| `random` | shuffled 3-fold | none really; it gives an optimistic upper bound |
| `revisit` | one measurement per station is held out | a known station, at another hour |
| `station_group` | each station is entirely in the training set or in the test set, 3-fold | a station never seen |

`station_group` is the one that matters. Stations are grouped by name rather than by name and line: a station measured on two lines has close values on both, so both lines must be on the same side of the split. Scores also vary from one random split to another, so each split is repeated 10 times with different seeds and we report the average.

## Simulated campaigns

These three modes apply to any data. In Seoul, though, every station is measured at every hour, which no field campaign does, so the results in [results.md](results.md) come from simulated campaigns. A share of the stations (25, 50 or 75 %) is visited, each at k random hours (1, 2, 3 or 5), and the model learns from these visits only. It is then tested on the other hours of the visited stations and on all the hours of the stations that were not visited. Each setting is repeated 10 times. The reference scenario is half of the stations, visited three times each.

## Limitations of the Seoul example

Architecture and depth come from 2021 versions of the station tables, but the coordinates, exits and transfers come from 2025 versions, applied to 2021 measurements. The exact position of each monitor in the station (platform or concourse) is not published. Finally, the random forest was picked by comparing several models on the same splits that are used to report its score, which can make that score slightly optimistic; the model is not tuned, which limits the effect.

## Features that could be added

Train frequency: the Seoul timetable ([OA-22522](https://data.seoul.go.kr/dataList/OA-22522/S/1/datasetView.do)) gives the number of trains per hour at each station. We tried it and it barely helped (an error of 9.9 instead of 10.2 µg/m³ on unvisited stations in the reference scenario), because it carries the same information as the hour of the day. We left it out to keep the code simple, but it may be more useful with other data, for example short platform measurements where passing trains have a direct effect.

Tunnel length: the distance to the neighbouring stations probably affects the air in stations and trains. It needs the order of stations along each line, which a timetable or a GTFS feed can provide, and would also make it possible to predict rides that were never measured.

Outdoor PM2.5 and weather: they change from day to day. Since the target here is a median over nine months, they matter less than they would for hourly forecasts.
