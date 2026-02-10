from models import Bike, User, Trip, MaintenanceRecord
from factories import BikeFactory, UserFactory
from pricing import PricingStrategy
from utils import read_csv_rows

class BikeShareSystem:
    def __init__(self):
        self.bikes: list[Bike] = []
        self.users: list[User] = []
        self.trips: list[Trip] = []
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

    # -------- Cleaning --------
    def remove_inactive_bikes(self) -> None:
        self.bikes = [b for b in self.bikes if b.status != "maintenance"]

    # -------- Analysis --------
    def total_distance(self) -> float:
        return sum(trip.distance_km for trip in self.trips)

    # -------- Reporting --------
    def compute_trip_cost(
        self, trip: Trip, pricing_strategy: PricingStrategy
    ) -> float:
        return pricing_strategy.compute_cost(trip)
