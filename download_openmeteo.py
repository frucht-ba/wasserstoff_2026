import requests
import pandas as pd

# Standort und Zeitraum
lat, lon = 35.754, -5.689          
start, end = "2023-01-01", "2023-12-31"

# Gewünschte stündliche Variablen
variablen = ["temperature_2m", "wind_speed_10m", "wind_speed_100m"]

# Anfrage an die Open-Meteo-Archiv-API (ERA5, kein API-Key nötig)
antwort = requests.get(
    "https://archive-api.open-meteo.com/v1/archive",
    params={
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": ",".join(variablen),
        "models": "era5",
        "timezone": "GMT",
        "wind_speed_unit": "ms",
    },
)
daten = antwort.json()

# In eine Tabelle umwandeln und speichern
df = pd.DataFrame(daten["hourly"])
df["time"] = pd.to_datetime(df["time"])
df.to_csv("./Data/TS renewable energie/wetter_2023.csv", index=False)

print(f"ERA5-Gitterpunkt: {daten['latitude']}, {daten['longitude']}")
print(df.head())
