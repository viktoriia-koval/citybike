import pandas as pd 
from utils import load_raw_data, inspect_dataframe, clean_trips, clean_stations,  clean_maintenance, export_cleaned, RAW_DATA_DIR
from time import perf_counter
from algorithms import bubble_sort_values, linear_search_numeric

def main():
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

    # -------------------------
    # 1. Загрузка CSV для анализа
    # -------------------------
    trips_df = pd.read_csv(RAW_DATA_DIR / "trips_cleaned.csv")
    print(f"\nВсего поездок: {len(trips_df)}")

    # Приводим duration и distance к float и округляем
    trips_df["duration_minutes"] = pd.to_numeric(trips_df["duration_minutes"], errors="coerce").round(2)
    trips_df["distance_km"] = pd.to_numeric(trips_df["distance_km"], errors="coerce").round(2)

    print("\n----- Sortieren (сортировка) -----")

    # Pandas sort по duration_minutes
    t2 = perf_counter()
    pandas_sorted_duration = trips_df.sort_values(by="duration_minutes").reset_index(drop=True)
    pandas_time = perf_counter() - t2

        # Bubble sort по duration_minutes
    t1 = perf_counter()
    print(t1)
    bubble_sorted_duration = bubble_sort_values(trips_df, by="duration_minutes")
    bubble_time = perf_counter() - t1

    print("Top 5 поездок по длительности (Pandas sort):")
    print(pandas_sorted_duration.head(5))

    print(f"Bubble sort (duration) time: {bubble_time:.6f} s")
    print(f"Pandas sort (duration) time: {pandas_time:.6f} s")
    if pandas_time > 0:
        print(f"Speed ratio (bubble/pandas): {bubble_time / pandas_time:.2f}x")

    # Bubble sort по distance_km
    t1 = perf_counter()
    bubble_sorted_distance = bubble_sort_values(trips_df, by="distance_km")
    bubble_time = perf_counter() - t1

    # Pandas sort по distance_km
    t2 = perf_counter()
    pandas_sorted_distance = trips_df.sort_values(by="distance_km").reset_index(drop=True)
    pandas_time = perf_counter() - t2

    print("Top 5 поездок по расстоянию (Pandas sort):")
    print(pandas_sorted_distance.head(5))

    print(f"Bubble sort (distance) time: {bubble_time:.6f} s")
    print(f"Pandas sort (distance) time: {pandas_time:.6f} s")
    if pandas_time > 0:
        print(f"Speed ratio (bubble/pandas): {bubble_time / pandas_time:.2f}x")

    # -------------------------
    # 2. Проверка поиска
    # -------------------------
    target_value = trips_df.iloc[0]["duration_minutes"]
    print("\n----- Search (поиск) -----")
    print(f"Ищем duration_minutes={target_value}")

    # Линейный поиск
    t1 = perf_counter()
    found_linear = linear_search_numeric(trips_df, field="duration_minutes", target=target_value)
    linear_time = perf_counter() - t1

    # Pandas поиск
    t2 = perf_counter()
    found_pandas = trips_df.loc[trips_df["duration_minutes"] == target_value]
    pandas_search_time = perf_counter() - t2

    print(f"Linear search found rows: {len(found_linear)}, time: {linear_time:.6f} s")
    print(f"Pandas search found rows: {len(found_pandas)}, time: {pandas_search_time:.6f} s")
    if pandas_search_time > 0:
        print(f"Speed ratio (linear/pandas): {linear_time / pandas_search_time:.2f}x")


if __name__ == "__main__":
    main()
