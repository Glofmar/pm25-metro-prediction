"""Interactive map of the predictions, with one layer per hour."""

import branca.colormap
import folium

# Bigger hour menu, legend, zoom buttons and tooltips than the Leaflet defaults
STYLE = """<style>
.leaflet-control-layers { font-size: 16px; padding: 4px 8px; margin-top: 28px !important; }
.leaflet-control-layers-base label { margin: 4px 0; }
.leaflet-control-layers input { transform: scale(1.4); margin-right: 8px; }
.leaflet-control-zoom a { width: 40px !important; height: 40px !important;
                          line-height: 40px !important; font-size: 24px !important; }
.leaflet-tooltip { font-size: 15px; }
.legend { transform: scale(1.4); transform-origin: top right; background: white;
          padding: 2px 4px; border-radius: 4px; }
</style>"""


def make_map(predictions, path, start_hour=8):
    platforms = predictions[(predictions["type"] == "platform") & predictions["lat_a"].notna()]
    rides = predictions[(predictions["type"] == "onboard") & predictions["lat_a"].notna() & predictions["lat_b"].notna()]
    colour = branca.colormap.LinearColormap(
        ["#1a9850", "#fee08b", "#d73027"],
        vmin=predictions["pm25_pred"].quantile(0.05),
        vmax=predictions["pm25_pred"].quantile(0.95),
        caption="Predicted PM2.5 (µg/m³)",
    )

    m = folium.Map(location=[platforms["lat_a"].mean(), platforms["lon_a"].mean()], zoom_start=11, tiles=None)
    # Esri's grey background also loads when the file is opened from disk, unlike OpenStreetMap
    folium.TileLayer("Esri.WorldGrayCanvas", overlay=True, control=False).add_to(m)

    for hour in sorted(platforms["hour"].unique()):
        layer = folium.FeatureGroup(name=f"{hour:02d}:00", overlay=False, show=(hour == start_hour))
        for ride in rides[rides["hour"] == hour].itertuples():
            folium.PolyLine(
                [[ride.lat_a, ride.lon_a], [ride.lat_b, ride.lon_b]],
                color=colour(ride.pm25_pred), weight=5, opacity=0.9,
                tooltip=f"{ride.station_a} → {ride.station_b} (line {ride.line}): {ride.pm25_pred:.0f} µg/m³",
            ).add_to(layer)
        for station in platforms[platforms["hour"] == hour].itertuples():
            folium.CircleMarker(
                [station.lat_a, station.lon_a], radius=8, color="white", weight=1,
                fill=True, fill_color=colour(station.pm25_pred), fill_opacity=0.9,
                tooltip=f"{station.station_a} (line {station.line}): {station.pm25_pred:.0f} µg/m³",
            ).add_to(layer)
        layer.add_to(m)

    colour.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().header.add_child(folium.Element(STYLE))
    m.save(str(path))
