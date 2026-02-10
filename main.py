from platform import system
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
    system = BikeShareSystem()
    system.load_stations_from_csv()
    system.load_trips_from_csv()
    system.load_maintenance_from_csv()

    print("before sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    t1 = perf_counter()
    system.sort_trips_by_distance()
    merge_sort_time = perf_counter() - t1
    print("after merge sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    system.load_trips_from_csv()

    t2 = perf_counter()
    system.sort_trips_by_distance_sys()
    pandas_sort_time = perf_counter() - t2
    print("after pandas sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    print(f"merge sort time: {merge_sort_time:.6f} s")
    print(f"pandas sort_values time: {pandas_sort_time:.6f} s")
    if pandas_sort_time > 0:
        print(f"speed ratio (merge/pandas): {merge_sort_time / pandas_sort_time:.2f}x")

    t3 = perf_counter()
    found_station = system.search_stations("ST100")
    station_search_time = perf_counter() - t3
    t4 = perf_counter()
    found_station_sys = system.search_stations_sys("ST100")
    station_search_sys_time = perf_counter() - t4
    print("search station result:", found_station.station_id if found_station else None)
    print("search station sys result:", found_station_sys.station_id if found_station_sys else None)
    print(f"binary search station time: {station_search_time:.6f} s")
    print(f"pandas .loc station time: {station_search_sys_time:.6f} s")
    if station_search_sys_time > 0:
        print(
            f"speed ratio (binary/pandas): "
            f"{station_search_time / station_search_sys_time:.2f}x"
        )

    

if __name__ == "__main__":
    main()
