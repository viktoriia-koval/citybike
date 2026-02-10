import pandas as pd 
from utils import load_raw_data, inspect_dataframe, clean_trips, clean_stations,  clean_maintenance, export_cleaned, RAW_DATA_DIR
from time import perf_counter
from algorithms import merge_sort
from datetime import datetime, timedelta
from analyzer import BikeShareSystem
from models import User, Bike, Station, Trip

def main555():
    # -------------------------
    # 0. Загрузка и очистка CSV
    # -------------------------
    print("Loading data...")
    trips_raw, stations_raw, maintenance_raw = load_raw_data()

    inspect_dataframe("trips_raw", trips_raw)
    inspect_dataframe("stations_raw", stations_raw)
    inspect_dataframe("maintenance_raw", maintenance_raw)

    trips_cleaned = clean_trips(trips_raw)
    stations_cleaned = clean_stations(stations_raw)
    maintenance_cleaned = clean_maintenance(maintenance_raw)

    inspect_dataframe("trips_cleaned", trips_cleaned)
    inspect_dataframe("stations_cleaned", stations_cleaned)
    inspect_dataframe("maintenance_cleaned", maintenance_cleaned)

    export_cleaned(trips_cleaned, stations_cleaned, maintenance_cleaned)
    print("\nCleaned datasets exported to:", RAW_DATA_DIR.resolve())

    

def main():
    print("Running main...")
    distances = [7.8, 2.4, 5.0, 1.1, 2.4]
    distances = [5, 2, 4, 7, 1, 3]
    sorted_distances = merge_sort(distances)
    print("merge_sort example:", sorted_distances)

    system = BikeShareSystem()
    user = User("U1", "Test User", "test@example.com", "member")
    bike = Bike("B1", "classic", "available")
    station = Station("S1", "Station 1", 10, 48.8, 9.2)
    start = datetime.now()

    system.trips = [
        Trip("T1", user, bike, station, station, start, start + timedelta(minutes=10), 3.7),
        Trip("T2", user, bike, station, station, start, start + timedelta(minutes=15), 1.4),
        Trip("T3", user, bike, station, station, start, start + timedelta(minutes=20), 2.1),
    ]

    system.load_trips_from_csv()    

    print("before sort:", [trip.distance_km for trip in system.trips[:20]])
    system.sort_trips_by_distance()
    print("after sort:", [trip.distance_km for trip in system.trips[:20]])



if __name__ == "__main__":
    main()
