"""Hauptmodul zum Ausfuehren der CityBike-Datenpipeline und Analyse."""

from platform import system
import timeit
from datetime import datetime, timedelta

import pandas as pd

from algorithms import binary_search, merge_sort
from analyzer import BikeShareSystem
from models import Bike, Station, Trip, User
from numerical import compute_distances_between_stations, compute_trip_vectorized_stats
from utils import (
    RAW_DATA_DIR,
    clean_maintenance,
    clean_stations,
    clean_trips,
    export_cleaned,
    inspect_dataframe,
    load_raw_data,
)
from visualization import create_all_visualizations


def benchmark_sorting(system_data: BikeShareSystem, runs: int = 10) -> dict[str, float]:
    """Vergleicht Sortierzeiten von merge_sort, pandas sort_values und built-in sorted."""
    distances = [trip.distance_km for trip in system_data.trips]
    if not distances:
        return {"merge_sort": 0.0, "pandas_sort_values": 0.0, "python_sorted": 0.0}

    distances_df = pd.DataFrame({"distance_km": distances})

    merge_total = timeit.timeit(
        lambda: merge_sort(distances, reverse=False),
        number=runs,
    )
    pandas_total = timeit.timeit(
        lambda: distances_df.sort_values(by="distance_km", ascending=True, kind="mergesort"),
        number=runs,
    )
    sorted_total = timeit.timeit(
        lambda: sorted(distances),
        number=runs,
    )

    return {
        "merge_sort": merge_total / runs,
        "pandas_sort_values": pandas_total / runs,
        "python_sorted": sorted_total / runs,
    }


def benchmark_search(
    system_data: BikeShareSystem, query: str = "ST100", runs: int = 1000
) -> dict[str, float]:
    """Vergleicht Suchzeiten von binary_search, pandas .loc und pandas .query."""
    station_ids = [station.station_id for station in system_data.stations]
    if not station_ids:
        return {"binary_search": 0.0, "pandas_loc": 0.0}

    normalized_query = query.strip().lower()
    sorted_station_ids = sorted(str(station_id).strip().lower() for station_id in station_ids)

    stations_df = pd.DataFrame({"station_id": station_ids})
    stations_df["station_id_norm"] = stations_df["station_id"].astype(str).str.strip().str.lower()

    binary_total = timeit.timeit(
        lambda: binary_search(sorted_station_ids, normalized_query),
        number=runs,
    )
    loc_total = timeit.timeit(
        lambda: stations_df.loc[stations_df["station_id_norm"] == normalized_query],
        number=runs,
    )
   
    return {
        "binary_search": binary_total / runs,
        "pandas_loc": loc_total / runs,
        
    }


def main() -> None:
    print("\n\n********* 2) Data Loading & Cleaning (Unit 11) *********")
    BikeShareSystem.clean_csv(is_print_details=True)

    print("\n\n********* 1) Object-Oriented Data Models (Units 7вЂ“8) *********")
    print("Running main...")
    system = BikeShareSystem()
    system.load_stations_from_csv()
    system.load_trips_from_csv()
    system.load_maintenance_from_csv()

    print("\n\n********* 3) Algorithmic Analysis (Unit 9) *********")
    print("before sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    system.sort_trips_by_distance()
    print("after merge sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    system.load_trips_from_csv("data\\trips_cleaned.csv")
    system.sort_trips_by_distance_sys()
    print("after pandas sort (first 20):", [trip.distance_km for trip in system.trips[:20]])

    sort_bench = benchmark_sorting(system, runs=10)
    print(f"merge sort avg time: {sort_bench['merge_sort']:.6f} s")
    print(f"pandas sort_values avg time: {sort_bench['pandas_sort_values']:.6f} s")
    print(f"python sorted avg time: {sort_bench['python_sorted']:.6f} s")
    if sort_bench["pandas_sort_values"] > 0:
        print(
            "speed ratio (merge/pandas): "
            f"{sort_bench['merge_sort'] / sort_bench['pandas_sort_values']:.2f}x"
        )
    if sort_bench["python_sorted"] > 0:
        print(
            "speed ratio (merge/sorted): "
            f"{sort_bench['merge_sort'] / sort_bench['python_sorted']:.2f}x"
        )

    found_station = system.search_stations("ST100")
    found_station_sys = system.search_stations_sys("ST100")
    search_bench = benchmark_search(system, query="ST100", runs=1000)
    print("search station result:", found_station.station_id if found_station else None)
    print("search station sys result:", found_station_sys.station_id if found_station_sys else None)
    print(f"binary search avg time: {search_bench['binary_search']:.8f} s")
    print(f"pandas .loc avg time: {search_bench['pandas_loc']:.8f} s")
    
    if search_bench["pandas_loc"] > 0:
        print(
            f"speed ratio (binary/pandas): "
            f"{search_bench['binary_search'] / search_bench['pandas_loc']:.2f}x"
        )

    print("\n\n********* 4) Numerical Computing (Unit 10) *********")
    latitudes = pd.Series([station.latitude for station in system.stations]).to_numpy()
    longitudes = pd.Series([station.longitude for station in system.stations]).to_numpy()
    station_distances = compute_distances_between_stations(latitudes, longitudes)
    print("station distance matrix shape:", station_distances.shape)
    print("station distance matrix first row (5):", station_distances[0, :5].round(6).tolist())

    trips_df = pd.read_csv("data\\trips_cleaned.csv")
    durations = pd.to_numeric(trips_df["duration_minutes"], errors="coerce").dropna().to_numpy()
    distances = pd.to_numeric(trips_df["distance_km"], errors="coerce").dropna().to_numpy()
    stats = compute_trip_vectorized_stats(durations, distances)
    print("duration stats:", stats["durations"])
    print("distance stats:", stats["distances"])

    print("\n\n********* 5) Analytics & Business Insights (Units 10 11) ")
    print("  und     7) Reporting & Export (Units 5, 11 12) *********")

    BikeShareSystem.run_report()

    print("\n\n********* 6) Visualization (Unit 12) *********")
    create_all_visualizations()


if __name__ == "__main__":
    main()
