from models import Bike, User, Trip, MaintenanceRecord, Station
from factories import BikeFactory, UserFactory
from utils import read_csv_rows
from algorithms import merge_sort, binary_search
from datetime import datetime
import pandas as pd

class BikeShareSystem:
    def __init__(self):
        self.bikes: list[Bike] = []
        self.users: list[User] = []
        self.trips: list[Trip] = []
        self.stations: list[Station] = []
        self.maintenance_records: list[MaintenanceRecord] = []

    # -------- Loading --------
    def load_bikes(self, rows: list[dict]) -> None:
        for row in rows:
            self.bikes.append(BikeFactory.from_row(row))

    def load_bikes_from_csv(self, path: str) -> None:
        rows = read_csv_rows(path)
        self.load_bikes(rows)

    def load_users(self, rows: list[dict]) -> None:
        for row in rows:
            self.users.append(UserFactory.from_row(row))

    def load_stations_from_csv(self, path: str = "data\\stations_cleaned.csv") -> None:
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
        self.bikes = [b for b in self.bikes if b.status != "maintenance"]

    # -------- Analysis --------
    def total_distance(self) -> float:
        return sum(trip.distance_km for trip in self.trips)

    def sort_trips_by_distance(self, reverse: bool = False) -> list[Trip]:
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
    def compute_trip_cost(self, trip: Trip, pricing_strategy) -> float:
        return pricing_strategy.compute_cost(trip)
