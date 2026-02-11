# CityBike

Backend-Projekt fuer ein City-Bike-Sharing-System mit Datenbereinigung, objektorientierten Modellen, algorithmischer Analyse, numerischen Berechnungen, Reporting und Visualisierung.

## Ueberblick

Dieses Projekt verarbeitet Fahrten-, Stations- und Wartungsdaten einer Bike-Sharing-Plattform und erzeugt daraus:

- bereinigte Datensaetze
- Kennzahlen und Business-Insights
- CSV-Reports und einen Textbericht
- Diagramme fuer zentrale Metriken

## Hauptfunktionen

- Objektorientierte Domaenenmodelle fuer Bikes, Nutzer, Fahrten, Stationen und Wartung (`models.py`)
- Datenladen und -bereinigung fuer Rohdaten (`utils.py`, `analyzer.py`)
- Eigene Algorithmen (Merge Sort, Binary Search) inkl. Benchmarking gegen pandas/Python (`algorithms.py`, `main.py`)
- Preisstrategien mit Strategy-Pattern (`pricing.py`)
- Vektorisierte numerische Auswertungen mit NumPy (`numerical.py`)
- Reporting-Exports nach `output/reports` (`analyzer.py`)
- Visualisierungen nach `output/figures` (`visualization.py`)

## Projektstruktur

```text
citybike/
|- data/
|  |- trips.csv
|  |- stations.csv
|  |- maintenance.csv
|  |- trips_cleaned.csv
|  |- stations_cleaned.csv
|  `- maintenance_cleaned.csv
|- output/
|  |- reports/
|  `- figures/
|- main.py
|- analyzer.py
|- models.py
|- pricing.py
|- numerical.py
|- algorithms.py
|- factories.py
|- utils.py
|- visualization.py
`- requirements.txt
```

## Voraussetzungen

- Python 3.10 oder neuer
- `pip`

## Installation

```bash
git clone <repo-url>
cd citybike
python -m venv .venv
.venv\Scripts\activate # Linux / macOS
pip install -r requirements.txt
```

## Ausfuehrung

Gesamte Pipeline (Cleaning, Analyse, Reports, Visualisierung):

```bash
python main.py
```

Nur Visualisierungen erzeugen:

```bash
python visualization.py
```

## Datenfluss

1. Rohdaten werden aus `data/*.csv` geladen.
2. Daten werden validiert, normalisiert und bereinigt.
3. Bereinigte Daten werden als `*_cleaned.csv` exportiert.
4. Analyse- und Reporting-Schritte berechnen KPIs und aggregierte Tabellen.
5. Ergebnisse werden nach `output/reports` und `output/figures` geschrieben.

## Ergebnisdateien

Nach `python main.py` entstehen typischerweise:

- `output/reports/top_stations.csv`
- `output/reports/top_users.csv`
- `output/reports/maintenance_summary.csv`
- `output/reports/summary_report.txt`
- `output/figures/bar_trips_per_station.png`
- `output/figures/line_monthly_trip_trend.png`
- `output/figures/hist_trip_duration.png`
- `output/figures/box_duration_by_user_type.png`
- `output/figures/bar_revenue_by_user_type.png`

## Hinweise

- Das Projekt nutzt sowohl eigene Algorithmen als auch pandas/NumPy-Varianten zum Vergleich.
- Die Preisberechnung ist ueber austauschbare Strategien modelliert.
- Bei Bedarf koennen neue Reports oder Diagramme modular erweitert werden.
