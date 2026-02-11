"""Modul mit zentraler Logik fuer Datenladen, Analyse und Reporting."""

from pathlib import Path
from models import Bike, User, Trip, MaintenanceRecord, Station
from factories import BikeFactory, UserFactory
from pricing import PricingStrategy
from utils import clean_maintenance, clean_stations, clean_trips, export_cleaned, inspect_dataframe, load_raw_data, read_csv_rows
from algorithms import merge_sort, binary_search
from datetime import datetime
import pandas as pd
import numpy as np

class BikeShareSystem:
    """Kernklasse zur Verwaltung von Fahrraedern, Nutzern, Fahrten und Berichten."""

    def __init__(self) -> None:
        self.bikes: list[Bike] = []
        self.users: list[User] = []
        self.trips: list[Trip] = []
        self.stations: list[Station] = []
        self.maintenance_records: list[MaintenanceRecord] = []

    # -------- Loading --------
    def load_bikes(self, rows: list[dict]) -> None:
        """Laedt Fahrraeder aus gegebenen Zeilen in das System."""
        for row in rows:
            self.bikes.append(BikeFactory.from_row(row))

    def load_bikes_from_csv(self, path: str) -> None:
        """Laedt Fahrraeder aus einer CSV-Datei."""
        rows = read_csv_rows(path)
        self.load_bikes(rows)

    def load_users(self, rows: list[dict]) -> None:
        """Laedt Nutzer aus gegebenen Zeilen in das System."""
        for row in rows:
            self.users.append(UserFactory.from_row(row))

    def load_stations_from_csv(self, path: str = "data\\stations_cleaned.csv") -> None:
        """Laedt Stationen aus einer CSV-Datei und ersetzt vorhandene Stationen."""
        rows = read_csv_rows(path)
        self.stations = []
        for row in rows:
            station = Station(
                station_id=str(row["station_id"]).strip(),
                name=str(row["station_name"]).strip(),
                capacity=int(row["capacity"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
            )
            self.stations.append(station)

    def _get_or_create_user(self, user_id: str, user_type: str) -> User:
        for user in self.users:
            if user.user_id == user_id:
                return user

        normalized_type = user_type if user_type in {"member", "casual"} else "member"
        new_user = User(
            user_id=user_id,
            name=f"User {user_id}",
            email=f"{user_id.lower()}@example.com",
            user_type=normalized_type,
        )
        self.users.append(new_user)
        return new_user

    def _get_or_create_station(self, station_id: str) -> Station:
        for station in self.stations:
            if station.station_id == station_id:
                return station

        new_station = Station(
            station_id=station_id,
            name=f"Station {station_id}",
            capacity=1,
            latitude=0.0,
            longitude=0.0,
        )
        self.stations.append(new_station)
        return new_station

    def load_trips_from_csv(self, path: str = "data\\trips_cleaned.csv") -> None:
        """Laedt Fahrten aus CSV, validiert Werte und verknuepft Objekte."""
        rows = read_csv_rows(path)
        self.trips = []

        for row in rows:
            user_id = str(row.get("user_id", "")).strip()
            bike_id = str(row.get("bike_id", "")).strip()
            start_station_id = str(row.get("start_station_id", "")).strip()
            end_station_id = str(row.get("end_station_id", "")).strip()
            if not user_id or not bike_id or not start_station_id or not end_station_id:
                continue

            bike_type = str(row.get("bike_type", "classic")).strip().lower() or "classic"
            user_type = str(row.get("user_type", "member")).strip().lower() or "member"

            user = self._get_or_create_user(user_id, user_type)
            bike = self._get_or_create_bike(bike_id, bike_type)
            start_station = self._get_or_create_station(start_station_id)
            end_station = self._get_or_create_station(end_station_id)

            try:
                trip = Trip(
                    trip_id=str(row["trip_id"]).strip(),
                    user=user,
                    bike=bike,
                    start_station=start_station,
                    end_station=end_station,
                    start_time=datetime.fromisoformat(str(row["start_time"]).strip()),
                    end_time=datetime.fromisoformat(str(row["end_time"]).strip()),
                    distance_km=float(row["distance_km"]),
                )
            except (ValueError, TypeError):
                continue

            self.trips.append(trip)

    def _get_or_create_bike(self, bike_id: str, bike_type: str) -> Bike:
        for bike in self.bikes:
            if bike.bike_id == bike_id:
                return bike

        new_bike = Bike(bike_id=bike_id, bike_type=bike_type, status="available")
        self.bikes.append(new_bike)
        return new_bike

    def load_maintenance_from_csv(
        self, path: str = "data\\maintenance_cleaned.csv"
    ) -> None:
        """Laedt Wartungsdatensaetze aus einer CSV-Datei."""
        rows = read_csv_rows(path)

        for row in rows:
            bike_id = str(row.get("bike_id", "")).strip()
            bike_type = str(row.get("bike_type", "classic")).strip().lower() or "classic"
            if not bike_id:
                continue

            bike = self._get_or_create_bike(bike_id, bike_type)
            date_value = datetime.fromisoformat(str(row["date"]).strip())
            cost_value = float(row["cost"])

            record = MaintenanceRecord(
                record_id=str(row["record_id"]).strip(),
                bike=bike,
                date=date_value,
                maintenance_type=str(row["maintenance_type"]).strip(),
                cost=cost_value,
                description=str(row.get("description", "")).strip(),
            )
            self.maintenance_records.append(record)

    # -------- Cleaning --------
    def remove_inactive_bikes(self) -> None:
        """Entfernt Fahrraeder mit Status 'maintenance' aus der aktiven Liste."""
        self.bikes = [b for b in self.bikes if b.status != "maintenance"]

    # -------- Analysis --------
    def total_distance(self) -> float:
        """Berechnet die gesamte gefahrene Distanz ueber alle Fahrten."""
        return sum(trip.distance_km for trip in self.trips)

    def sort_trips_by_distance(self, reverse: bool = False) -> list[Trip]:
        """Sortiert Fahrten nach Distanz mit dem eigenen Merge-Sort-Ansatz."""
        sorted_distances = merge_sort([trip.distance_km for trip in self.trips], reverse=reverse)

        distance_to_trips: dict[float, list[Trip]] = {}
        for trip in self.trips:
            distance_to_trips.setdefault(trip.distance_km, []).append(trip)

        sorted_trips: list[Trip] = []
        for distance in sorted_distances:
            sorted_trips.append(distance_to_trips[distance].pop(0))

        self.trips = sorted_trips
        return self.trips

    def sort_trips_by_distance_sys(self, reverse: bool = False) -> list[Trip]:
        """Sortiert Fahrten nach Distanz mit pandas sort_values."""
        if not self.trips:
            return self.trips

        trips_df = pd.DataFrame(
            {
                "index": list(range(len(self.trips))),
                "distance_km": [trip.distance_km for trip in self.trips],
            }
        )
        trips_df = trips_df.sort_values(
            by="distance_km",
            ascending=not reverse,
            kind="mergesort",
        )
        self.trips = [self.trips[int(i)] for i in trips_df["index"].tolist()]
        return self.trips

    def search_stations(self, query: str, by: str = "station_id") -> Station | None:
        """Sucht eine Station per binaerer Suche nach ID oder Name."""
        if by not in {"station_id", "station_name"}:
            raise ValueError("by must be 'station_id' or 'station_name'")
        if not self.stations:
            return None

        normalized_query = query.strip().lower()
        key_name = "station_id" if by == "station_id" else "name"

        sorted_stations = sorted(
            self.stations,
            key=lambda station: str(getattr(station, key_name)).strip().lower(),
        )
        keys = [str(getattr(station, key_name)).strip().lower() for station in sorted_stations]
        index = binary_search(keys, normalized_query)
        if index == -1:
            return None
        return sorted_stations[index]

    def search_stations_sys(self, query: str, by: str = "station_id") -> Station | None:
        """Sucht eine Station ueber pandas-Filter nach ID oder Name."""
        if by not in {"station_id", "station_name"}:
            raise ValueError("by must be 'station_id' or 'station_name'")
        if not self.stations:
            return None

        key_name = "station_id" if by == "station_id" else "name"
        normalized_query = query.strip().lower()

        stations_df = pd.DataFrame(
            {
                "station_obj": self.stations,
                "station_id": [station.station_id for station in self.stations],
                "name": [station.name for station in self.stations],
            }
        )
        normalized_col = stations_df[key_name].astype(str).str.strip().str.lower()
        matched = stations_df.loc[normalized_col == normalized_query, "station_obj"]
        if matched.empty:
            return None
        return matched.iloc[0]

    # -------- Reporting --------
    def compute_trip_cost(self, trip: Trip, pricing_strategy: PricingStrategy) -> float:
        """Berechnet Fahrkosten anhand der uebergebenen Preisstrategie."""
        return pricing_strategy.compute_cost(trip)

    @staticmethod
    def clean_csv(is_print_details:bool = False) -> None:
        """Bereinigt Rohdaten und exportiert bereinigte CSV-Dateien."""

        if is_print_details:
            print("Loading data...")

        trips_raw, stations_raw, maintenance_raw = load_raw_data()
        
        if is_print_details:
            inspect_dataframe("trips_raw", trips_raw)
            inspect_dataframe("stations_raw", stations_raw)
            inspect_dataframe("maintenance_raw", maintenance_raw)

        trips_cleaned = clean_trips(trips_raw)
        stations_cleaned = clean_stations(stations_raw)
        maintenance_cleaned = clean_maintenance(maintenance_raw)

        if is_print_details:
            inspect_dataframe("trips_cleaned", trips_cleaned)
            inspect_dataframe("stations_cleaned", stations_cleaned)
            inspect_dataframe("maintenance_cleaned", maintenance_cleaned)

        export_cleaned(trips_cleaned, stations_cleaned, maintenance_cleaned)

        if is_print_details:
            print("\nCleaned datasets exported")

    
    ''' 5) Analytics & Business Insights (Units 10–11)
        7) Reporting & Export (Units 5, 11–12) '''
    @staticmethod
    def run_report() -> None:
        """Erstellt Analyseausgaben und exportiert Tabellen sowie Textbericht."""
        OUT_DIR = Path("output") / "reports"
        
        trips = pd.read_csv("data\\trips_cleaned.csv")
        stations = pd.read_csv("data\\stations_cleaned.csv")
        maintenance = pd.read_csv("data\\maintenance_cleaned.csv")

        trips_data = trips.copy()
        trips_data["start_time"] = pd.to_datetime(trips_data["start_time"], errors="coerce")
        trips_data["end_time"] = pd.to_datetime(trips_data["end_time"], errors="coerce")
        trips_data["duration_minutes"] = pd.to_numeric(trips_data["duration_minutes"], errors="coerce")
        trips_data["distance_km"] = pd.to_numeric(trips_data["distance_km"], errors="coerce")

        maintenance_data = maintenance.copy()
        maintenance_data["date"] = pd.to_datetime(maintenance_data["date"], errors="coerce")
        maintenance_data["cost"] = pd.to_numeric(maintenance_data["cost"], errors="coerce")

        print("1) Total trips / total distance / average duration")
        print(
            f"Trips: {len(trips_data)} | Distance km: {trips_data['distance_km'].sum():.2f} | "
            f"Avg duration min: {trips_data['duration_minutes'].mean():.2f}"
        )

        print("\n2) Top 10 start stations")
        print(trips_data["start_station_id"].value_counts().head(10))
        print("\nTop 10 end stations")
        print(trips_data["end_station_id"].value_counts().head(10))

        print("\n3) Peak usage hours")
        peak_hours = trips_data["start_time"].dt.hour.value_counts().sort_values(ascending=False)
        print(peak_hours.head(10))

        print("\n4) Day of week with highest volume")
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday_counts = trips_data["start_time"].dt.day_name().value_counts().reindex(weekday_order)
        print(weekday_counts)
        print("Highest:", weekday_counts.idxmax(), int(weekday_counts.max()))

        print("\n5) Avg trip distance by user type")
        print(trips_data.groupby("user_type")["distance_km"].mean().sort_values(ascending=False))

        print("\n6) Bike utilization rate (approximation)")
        period_minutes = (trips_data["end_time"].max() - trips_data["start_time"].min()).total_seconds() / 60
        bikes = trips_data["bike_id"].nunique()
        in_use = trips_data["duration_minutes"].sum()
        utilization = (in_use / (bikes * period_minutes)) * 100 if bikes and period_minutes else np.nan
        print(f"Utilization: {utilization:.2f}%")

        print("\n7) Top 15 active users")
        print(trips_data["user_id"].value_counts().head(15))

        print("\n8) Total maintenance cost per bike type")
        print(maintenance_data.groupby("bike_type")["cost"].sum().sort_values(ascending=False))

        print("\n9) Top 10 station-to-station routes")
        routes = (trips_data["start_station_id"].astype(str) + " -> " + trips_data["end_station_id"].astype(str)).value_counts()
        print(routes.head(10))

        print("\n10) Trip completion rate")
        status_counts = trips_data["status"].value_counts()
        completed = int(status_counts.get("completed", 0))
        cancelled = int(status_counts.get("cancelled", 0))
        rate = (completed / (completed + cancelled) * 100) if (completed + cancelled) else np.nan # Scutz vor Division durch Null
        print(f"Completed: {completed} | Cancelled: {cancelled} | Completion rate: {rate:.2f}%")

        print("\n11) Avg number of trips per user by user type")
        trips_per_user = trips_data.groupby(["user_type", "user_id"]).size().groupby(level=0).mean()
        print(trips_per_user.sort_values(ascending=False))

        print("\n12) Highest maintenance frequency by bike")
        maintenance_freq = maintenance_data["bike_id"].value_counts().head(15)
        print(maintenance_freq)


        # Exports
        OUT_DIR.mkdir(parents=True, exist_ok=True)

        top_start = trips_data["start_station_id"].value_counts().head(10).rename_axis("station_id").reset_index(name="start_trip_count")
        top_end = trips_data["end_station_id"].value_counts().head(10).rename_axis("station_id").reset_index(name="end_trip_count")
        top_stations = top_start.merge(top_end, on="station_id", how="outer").fillna(0)
        top_stations[["start_trip_count", "end_trip_count"]] = top_stations[
            ["start_trip_count", "end_trip_count"]
        ].astype(int)
        top_stations.to_csv(OUT_DIR / "top_stations.csv", index=False)

        top_users = trips_data["user_id"].value_counts().head(15).rename_axis("user_id").reset_index(name="trip_count")
        top_users.to_csv(OUT_DIR / "top_users.csv", index=False)

        maintenance_summary = (
            maintenance_data.groupby("bike_type", dropna=False)
            .agg(
                total_cost=("cost", "sum"),
                records=("bike_id", "count"),
                unique_bikes=("bike_id", "nunique"),
                avg_cost=("cost", "mean"),
            )
            .reset_index()
        )
        maintenance_summary.to_csv(OUT_DIR / "maintenance_summary.csv", index=False)
        print(f"\nExported summaries to: {OUT_DIR.resolve()}")

        # Text summary report
        q1_total_trips = len(trips_data)  # Gesamtanzahl der Fahrten (Zeilen im DataFrame)
        q1_total_distance = float(trips_data["distance_km"].sum())   # Gesamtdistanz aller Fahrten in km
        q1_avg_duration = float(trips_data["duration_minutes"].mean())   # Durchschnittliche Fahrtdauer in Minuten
        q4_best_day = weekday_counts.idxmax()   # Name des Wochentags mit den meisten Fahrten
        q4_best_day_count = int(weekday_counts.max())  # Anzahl der Fahrten an diesem Wochentag
        top_start_station = trips_data["start_station_id"].value_counts().idxmax()   # Startstation mit den meisten Abfahrten
        top_end_station = trips_data["end_station_id"].value_counts().idxmax()   # Zielstation mit den meisten Ankünften
        top_user = trips_data["user_id"].value_counts().idxmax()   # Nutzer-ID mit den meisten Fahrten
        top_user_trips = int(trips_data["user_id"].value_counts().max())   # Anzahl der Fahrten dieses Nutzers
        top_route = routes.index[0] if len(routes) else "N/A"   # Häufigste Route oder "N/A", falls keine Daten
        top_route_count = int(routes.iloc[0]) if len(routes) else 0   # Anzahl der Fahrten auf der häufigsten Route
        top_maint_bike = maintenance_freq.index[0] if len(maintenance_freq) else "N/A"   # Meistgewartetes Bike oder "N/A"
        top_maint_bike_count = int(maintenance_freq.iloc[0]) if len(maintenance_freq) else 0   # Anzahl der Wartungseinträge

        summary_lines = [
            "CityBike Analytics Summary Report",
            "================================",
            "",
            "Data sources:",
            f"- Trips: 'trips_cleaned.csv'",
            f"- Stations: 'stations_cleaned.csv'",
            f"- Maintenance: 'maintenance_cleaned.csv'",
            "",
            "1) Core KPIs",
            f"- Total trips: {q1_total_trips}",
            f"- Total distance (km): {q1_total_distance:.2f}",
            f"- Average trip duration (min): {q1_avg_duration:.2f}",
            "",
            "2) Station popularity",
            f"- Top start station: {top_start_station}",
            f"- Top end station: {top_end_station}",
            "",
            "3) Temporal demand",
            f"- Peak usage hour: {int(peak_hours.idxmax())}:00",
            f"- Highest trip-volume weekday: {q4_best_day} ({q4_best_day_count} trips)",
            "",
            "4) Customer and behavior insights",
            f"- Avg distance by user type: {trips_data.groupby('user_type')['distance_km'].mean().round(2).to_dict()}",
            f"- Avg trips per user by user type: {trips_per_user.round(2).to_dict()}",
            "",
            "5) Fleet and utilization",
            f"- Bike utilization rate (approx): {utilization:.2f}%",
            f"- Most maintained bike: {top_maint_bike} ({top_maint_bike_count} records)",
            "",
            "6) Business hotspots",
            f"- Top active user: {top_user} ({top_user_trips} trips)",
            f"- Top route: {top_route} ({top_route_count} trips)",
            "",
            "7) Maintenance spend",
            f"- Maintenance cost by bike type: {maintenance_data.groupby('bike_type')['cost'].sum().round(2).to_dict()}",
            "",
            "Exported tables:",
            f"- {OUT_DIR / 'top_stations.csv'}",
            f"- {OUT_DIR / 'top_users.csv'}",
            f"- {OUT_DIR / 'maintenance_summary.csv'}",
        ]

        summary_path = OUT_DIR / "summary_report.txt"
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")  # Schreibt die Zusammenfassung zeilenweise in eine UTF-8-kodierte Textdatei.
        print(f"Exported summary report to: {summary_path.resolve()}")
