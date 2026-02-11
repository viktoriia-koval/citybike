"""Hilfsmodul zum Laden, Pruefen, Bereinigen und Exportieren von CityBike-Daten."""
import csv
from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data")


def read_csv_rows(path: str | Path) -> list[dict]:
    """Liest eine CSV-Datei und gibt alle Zeilen als Liste von Dictionaries zurueck."""
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))



def inspect_dataframe(name: str, df: pd.DataFrame) -> None:
    """Gibt kompakte Diagnosen zu Struktur, Statistik und fehlenden Werten aus."""
    print(f"\n=== {name} | info() ===")
    df.info()
    print(f"\n=== {name} | describe(include='all') ===")
    print(df.describe(include="all").transpose())
    print(f"\n=== {name} | isnull().sum() ===")
    print(df.isnull().sum())


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Laedt Rohdaten fuer Fahrten, Stationen und Wartung aus dem Datenordner."""
    trips = pd.read_csv(RAW_DATA_DIR / "trips.csv")
    stations = pd.read_csv(RAW_DATA_DIR / "stations.csv")
    maintenance = pd.read_csv(RAW_DATA_DIR / "maintenance.csv")
    return trips, stations, maintenance


def clean_trips(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt Fahrtdaten, normalisiert Kategorien und entfernt ungueltige Datensaetze."""
    cleaned = df.copy()

    # Parse datetimes; drop rows with invalid timestamps because trip timing is core data.
    cleaned["start_time"] = pd.to_datetime(cleaned["start_time"], errors="coerce")
    cleaned["end_time"] = pd.to_datetime(cleaned["end_time"], errors="coerce")
    cleaned = cleaned.dropna(subset=["start_time", "end_time"])

    # Numeric conversion with coercion to catch malformed values.
    cleaned["duration_minutes"] = pd.to_numeric(
        cleaned["duration_minutes"], errors="coerce"
    )
    cleaned["distance_km"] = pd.to_numeric(cleaned["distance_km"], errors="coerce")

    # Fill missing duration and distance from available timestamps.
    missing_duration = cleaned["duration_minutes"].isna()
    cleaned.loc[missing_duration, "duration_minutes"] = (
        cleaned.loc[missing_duration, "end_time"]
        - cleaned.loc[missing_duration, "start_time"]
    ).dt.total_seconds() / 60.0


    # Standardize categorical values.
    cleaned["user_type"] = cleaned["user_type"].astype(str).str.strip().str.lower()
    cleaned["bike_type"] = cleaned["bike_type"].astype(str).str.strip().str.lower()
    cleaned["status"] = cleaned["status"].astype("string").str.strip().str.lower()

    # Missing status defaults to completed only when trip has a valid positive duration.
    can_default_completed = cleaned["status"].isna() & (cleaned["duration_minutes"] > 0)
    cleaned.loc[can_default_completed, "status"] = "completed"
    cleaned["status"] = cleaned["status"].fillna("unknown")

    # Remove exact duplicates and invalid business records.
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned[cleaned["end_time"] >= cleaned["start_time"]]
    cleaned = cleaned[cleaned["duration_minutes"] >= 0]
    cleaned = cleaned[cleaned["distance_km"] >= 0]

    # Keep only known categories; unexpected values become unknown.
    cleaned["user_type"] = cleaned["user_type"].where(
        cleaned["user_type"].isin({"member", "casual"}), "unknown"
    )
    cleaned["bike_type"] = cleaned["bike_type"].where(
        cleaned["bike_type"].isin({"classic", "electric"}), "unknown"
    )
    cleaned["status"] = cleaned["status"].where(
        cleaned["status"].isin({"completed", "cancelled", "unknown"}), "unknown"
    )

    return cleaned


def clean_stations(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt Stationsdaten und validiert Kapazitaet sowie Koordinatenbereiche."""
    cleaned = df.copy()

    cleaned["capacity"] = pd.to_numeric(cleaned["capacity"], errors="coerce")
    cleaned["latitude"] = pd.to_numeric(cleaned["latitude"], errors="coerce")
    cleaned["longitude"] = pd.to_numeric(cleaned["longitude"], errors="coerce")

    cleaned["station_id"] = cleaned["station_id"].astype(str).str.strip().str.upper()
    cleaned["station_name"] = cleaned["station_name"].astype(str).str.strip()

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.dropna(subset=["station_id", "station_name", "capacity", "latitude", "longitude"])
    cleaned = cleaned[cleaned["capacity"] > 0]
    cleaned = cleaned[cleaned["latitude"].between(-90, 90)]
    cleaned = cleaned[cleaned["longitude"].between(-180, 180)]

    return cleaned


def clean_maintenance(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt Wartungsdaten und normalisiert Typen sowie Textfelder."""
    cleaned = df.copy()

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["cost"] = pd.to_numeric(cleaned["cost"], errors="coerce")

    cleaned["bike_type"] = cleaned["bike_type"].astype(str).str.strip().str.lower()
    cleaned["maintenance_type"] = (
        cleaned["maintenance_type"].astype(str).str.strip().str.lower()
    )
    cleaned["description"] = cleaned["description"].astype(str).str.strip()


    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.dropna(subset=["record_id", "bike_id", "bike_type", "date", "maintenance_type", "cost"])
    cleaned = cleaned[cleaned["cost"] >= 0]

    cleaned["bike_type"] = cleaned["bike_type"].where(
        cleaned["bike_type"].isin({"classic", "electric"}), "unknown"
    )

    return cleaned


def export_cleaned(
    trips: pd.DataFrame, stations: pd.DataFrame, maintenance: pd.DataFrame
) -> None:
    """Exportiert bereinigte Fahrten-, Stations- und Wartungsdaten als CSV-Dateien."""
 
    trips.to_csv(RAW_DATA_DIR / "trips_cleaned.csv", index=False)
    stations.to_csv(RAW_DATA_DIR / "stations_cleaned.csv", index=False)
    maintenance.to_csv(RAW_DATA_DIR / "maintenance_cleaned.csv", index=False)


