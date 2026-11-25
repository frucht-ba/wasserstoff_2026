import math
import pandas as pd

# Route Tanger Med -> Rotterdam, gecharterter Anteil an einem größeren Schiff
distanz_sm = 1377                 # Seemeilen, Hafen zu Hafen
geschwindigkeit_kn = 12           # Knoten
fahrzeit_h = round(distanz_sm / geschwindigkeit_kn)   # ca. 115 h

zyklen = 4

# Transportmenge: 30 kt Wasserstoff pro Jahr, gebunden in DME
h2_jahr_t = 30_000
# Stöchiometrie: 2 CO2 + 6 H2 -> CH3OCH3 + 3 H2O  (6 mol H2 = 12,096 g je 46,07 g DME)
h2_je_t_dme = 6 * 2.016 / 46.07   # ca. 0,263 t H2 je t DME
dme_je_zyklus_t = h2_jahr_t / zyklen / h2_je_t_dme    # ca. 28.600 t DME
heizwert_h2_mwh_t = 33.33         # MWh/t (unterer Heizwert)

# Lade-/Löschzeit aus Menge und Pumprate, plus An-/Ablegen und Schläuche
pumprate_t_h = 1000
nebenzeit_h = 4
beladezeit_h = math.ceil(dme_je_zyklus_t / pumprate_t_h) + nebenzeit_h
entladezeit_h = beladezeit_h

# Eigenverbrauch des Schiffes (Referenz: VLGC, 84.000 m³, Gastanker für LPG/DME)
verbrauch_schiff_t_tag = 23       # t Brennstoff/Tag bei 12 kn (Hauptmaschine ~18 t + Hilfsdiesel ~5 t)
heizwert_brennstoff_mwh_t = 11.39 # MWh/t, Schiffsdiesel (41 MJ/kg)
schiff_kapazitaet_m3 = 84_000
dichte_dme_t_m3 = 0.67            # flüssiges DME
charter_anteil = dme_je_zyklus_t / dichte_dme_t_m3 / schiff_kapazitaet_m3   # ca. 51 %
heizwert_dme_mwh_t = 8.0          # MWh/t (28,8 MJ/kg)

# Erste Lieferung (Entladung in Rotterdam) Ende Januar
erste_entladung = pd.Timestamp("2023-01-30 00:00")

# Stündlicher Zeitindex für 2023 (8760 Stunden)
zeit = pd.date_range("2023-01-01 00:00", "2023-12-31 23:00", freq="h", name="time")
df = pd.DataFrame(0, index=zeit, columns=["beladung", "entladung", "fahrt"])

# Zyklen gleichmäßig über das Jahr verteilen, ab der ersten Beladung
abstand_h = len(zeit) // zyklen
erste_beladung_h = zeit.get_loc(erste_entladung) - fahrzeit_h - beladezeit_h
for i in range(zyklen):
    start_beladung = erste_beladung_h + i * abstand_h
    start_entladung = start_beladung + beladezeit_h + fahrzeit_h
    df.iloc[start_beladung:start_beladung + beladezeit_h, 0] = 1
    df.iloc[start_entladung:start_entladung + entladezeit_h, 1] = 1
    df.iloc[start_beladung + beladezeit_h:start_entladung, 2] = 1   # beladene Fahrt Tanger -> Rotterdam

# Last: anteiliger Eigenverbrauch des Schiffes während der Fahrt
verbrauch_mw = verbrauch_schiff_t_tag / 24 * heizwert_brennstoff_mwh_t * charter_anteil
df["schiff_verbrauch_mw"] = df["fahrt"] * verbrauch_mw
df["dme_verbrauch_t_h"] = df["schiff_verbrauch_mw"] / heizwert_dme_mwh_t           # falls mit DME betrieben
df["h2_verbrauch_mw"] = df["dme_verbrauch_t_h"] * h2_je_t_dme * heizwert_h2_mwh_t  # H2-Bedarf dafür (Hu)

print("Fahrzeit (h):", fahrzeit_h, "| Beladezeit (h):", beladezeit_h)
print("DME je Zyklus (t):", round(dme_je_zyklus_t), "| Charter-Anteil:", round(charter_anteil * 100), "%")
print("Verbrauch während Fahrt:", round(verbrauch_mw, 2), "MW =", round(verbrauch_mw / heizwert_dme_mwh_t, 3), "t DME/h")
print("Jahr: Brennstoff", round(df["schiff_verbrauch_mw"].sum()), "MWh | DME", round(df["dme_verbrauch_t_h"].sum()),
      "t | H2", round(df["h2_verbrauch_mw"].sum() / heizwert_h2_mwh_t), "t")
df.to_csv("Data/processed/schiff_beladung_2023.csv")
