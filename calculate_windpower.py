import pandas as pd
from windpowerlib import WindTurbine, ModelChain

# Wetterdaten aus dem Download-Snippet laden
df = pd.read_csv("data/raw/wetter_2023.csv", parse_dates=["time"], index_col="time")

# windpowerlib erwartet Spalten als (Variable, Höhe in m)
weather = pd.DataFrame({
    ("wind_speed", 10): df["wind_speed_10m"],
    ("wind_speed", 100): df["wind_speed_100m"],
    ("temperature", 2): df["temperature_2m"] + 273.15,   # in Kelvin
    ("roughness_length", 0): 0.1,                        # m, Pflichtspalte (wird bei festem hellman_exp ignoriert)
})

# Anlage aus der eingebauten Turbinen-Datenbank (oedb)
turbine = WindTurbine(turbine_type="V126/3450", hub_height=112)

# Modellkette: Höhenkorrektur + Leistungskennlinie
mc = ModelChain(turbine, wind_speed_model="hellman", hellman_exp=1/7,
                temperature_model="linear_gradient").run_model(weather)

leistung_w = mc.power_output                          # in Watt
profil = leistung_w / turbine.nominal_power           # 0...1, bezogen auf Nennleistung
profil = profil * (1 - 0.10)                          # 10 % Park-/Verfügbarkeitsverluste

print("Nennleistung:", turbine.nominal_power / 1e6, "MW")
print("Volllaststunden:", round(profil.sum()))
print("Kapazitätsfaktor:", round(profil.mean() * 100, 1), "%")
profil.rename("wind_profil").to_csv("data/processed/wind_lastprofil_2023.csv")