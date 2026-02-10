#from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path("output") / "reports"


def _pick_path(cleaned_name: str, raw_name: str) -> Path:
    cleaned = Path("data") / cleaned_name
    if cleaned.exists():
        return cleaned
    return Path("data") / raw_name


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    trips = pd.read_csv("data\\trips_cleaned.csv")
    stations = pd.read_csv("data\\stations_cleaned.csv")
    maintenance = pd.read_csv("data\\maintenance_cleaned.csv")
    return trips, stations, maintenance


def prepare_data(
    trips: pd.DataFrame, maintenance: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    t = trips.copy()

    #print("Before:", t["start_time"].dtype, t["end_time"].dtype)
    #print("Example type:", type(t["start_time"].dropna().iloc[0]))

    t["start_time"] = pd.to_datetime(t["start_time"], errors="coerce")
    t["end_time"] = pd.to_datetime(t["end_time"], errors="coerce")

    #print("After:", t["start_time"].dtype, t["end_time"].dtype)
    #print("Example type:", type(t["start_time"].dropna().iloc[0]))


    t["duration_minutes"] = pd.to_numeric(t["duration_minutes"], errors="coerce")
    t["distance_km"] = pd.to_numeric(t["distance_km"], errors="coerce")
    # t["user_type"] = t["user_type"].astype(str).str.strip().str.lower()
    # t["status"] = t["status"].astype(str).str.strip().str.lower()

    m = maintenance.copy()
    m["date"] = pd.to_datetime(m["date"], errors="coerce")
    m["cost"] = pd.to_numeric(m["cost"], errors="coerce")
    # m["bike_type"] = m["bike_type"].astype(str).str.strip().str.lower()
    return t, m


def run_report() -> None:
    trips, stations, maintenance = load_data()
    t, m = prepare_data(trips, maintenance)

    print("1) Total trips / total distance / average duration")
    print(
        f"Trips: {len(t)} | Distance km: {t['distance_km'].sum():.2f} | "
        f"Avg duration min: {t['duration_minutes'].mean():.2f}"
    )

    print("\n2) Top 10 start stations")
    print(t["start_station_id"].value_counts().head(10))
    print("\nTop 10 end stations")
    print(t["end_station_id"].value_counts().head(10))

    print("\n3) Peak usage hours")
    peak_hours = t["start_time"].dt.hour.value_counts().sort_values(ascending=False)
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
    weekday_counts = t["start_time"].dt.day_name().value_counts().reindex(weekday_order)
    print(weekday_counts)
    print("Highest:", weekday_counts.idxmax(), int(weekday_counts.max()))

    print("\n5) Avg trip distance by user type")
    print(t.groupby("user_type")["distance_km"].mean().sort_values(ascending=False))

    print("\n6) Bike utilization rate (approximation)")
    period_minutes = (t["end_time"].max() - t["start_time"].min()).total_seconds() / 60
    bikes = t["bike_id"].nunique()
    in_use = t["duration_minutes"].sum()
    utilization = (in_use / (bikes * period_minutes)) * 100 if bikes and period_minutes else np.nan
    print(f"Utilization: {utilization:.2f}%")

    print("\n7) Monthly trip trend")
    monthly = t.set_index("start_time").resample("ME").size()
    monthly_df = monthly.reset_index(name="trip_count")
    monthly_df["month"] = monthly_df["start_time"].dt.strftime("%Y-%m")
    print(monthly_df[["month", "trip_count"]])
    if len(monthly) >= 2:
        slope = np.polyfit(np.arange(len(monthly)), monthly.values, 1)[0]
        print("Growing:", bool(monthly.iloc[-1] > monthly.iloc[0]), "| slope:", round(float(slope), 3))

    print("\n8) Top 15 active users")
    print(t["user_id"].value_counts().head(15))

    print("\n9) Total maintenance cost per bike type")
    print(m.groupby("bike_type")["cost"].sum().sort_values(ascending=False))

    print("\n10) Top 10 station-to-station routes")
    routes = (t["start_station_id"].astype(str) + " -> " + t["end_station_id"].astype(str)).value_counts()
    print(routes.head(10))

    print("\n11) Trip completion rate")
    status_counts = t["status"].value_counts()
    completed = int(status_counts.get("completed", 0))
    cancelled = int(status_counts.get("cancelled", 0))
    rate = (completed / (completed + cancelled) * 100) if (completed + cancelled) else np.nan
    print(f"Completed: {completed} | Cancelled: {cancelled} | Completion rate: {rate:.2f}%")

    print("\n12) Avg number of trips per user by user type")
    trips_per_user = t.groupby(["user_type", "user_id"]).size().groupby(level=0).mean()
    print(trips_per_user.sort_values(ascending=False))

    print("\n13) Highest maintenance frequency by bike")
    maintenance_freq = m["bike_id"].value_counts().head(15)
    print(maintenance_freq)

    print("\n14) Outlier trips (z-score > 3)")
    valid = t[["trip_id", "duration_minutes", "distance_km"]].dropna().copy()
    for col in ["duration_minutes", "distance_km"]:
        std = valid[col].std(ddof=0)
        valid[f"{col}_z"] = 0.0 if std == 0 else (valid[col] - valid[col].mean()) / std
    outliers = valid[
        (valid["duration_minutes_z"].abs() > 3) | (valid["distance_km_z"].abs() > 3)
    ].copy()
    outliers["max_abs_z"] = outliers[["duration_minutes_z", "distance_km_z"]].abs().max(axis=1)
    outliers = outliers.sort_values("max_abs_z", ascending=False)
    print("Outliers count:", len(outliers))
    print(outliers[["trip_id", "duration_minutes", "distance_km"]].head(20))

    print("\nLoaded stations rows:", len(stations))

    # Exports
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    top_start = t["start_station_id"].value_counts().head(10).rename_axis("station_id").reset_index(name="start_trip_count")
    top_end = t["end_station_id"].value_counts().head(10).rename_axis("station_id").reset_index(name="end_trip_count")
    top_stations = top_start.merge(top_end, on="station_id", how="outer").fillna(0)
    top_stations[["start_trip_count", "end_trip_count"]] = top_stations[
        ["start_trip_count", "end_trip_count"]
    ].astype(int)
    top_stations.to_csv(OUT_DIR / "top_stations.csv", index=False)

    top_users = t["user_id"].value_counts().head(15).rename_axis("user_id").reset_index(name="trip_count")
    top_users.to_csv(OUT_DIR / "top_users.csv", index=False)

    maintenance_summary = (
        m.groupby("bike_type", dropna=False)
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
    q1_total_trips = len(t)
    q1_total_distance = float(t["distance_km"].sum())
    q1_avg_duration = float(t["duration_minutes"].mean())
    q4_best_day = weekday_counts.idxmax()
    q4_best_day_count = int(weekday_counts.max())
    top_start_station = t["start_station_id"].value_counts().idxmax()
    top_end_station = t["end_station_id"].value_counts().idxmax()
    top_user = t["user_id"].value_counts().idxmax()
    top_user_trips = int(t["user_id"].value_counts().max())
    top_route = routes.index[0] if len(routes) else "N/A"
    top_route_count = int(routes.iloc[0]) if len(routes) else 0
    top_maint_bike = maintenance_freq.index[0] if len(maintenance_freq) else "N/A"
    top_maint_bike_count = int(maintenance_freq.iloc[0]) if len(maintenance_freq) else 0

    summary_lines = [
        "CityBike Analytics Summary Report",
        "================================",
        "",
        "Data sources:",
        f"- Trips: {_pick_path('trips_cleaned.csv', 'trips.csv')}",
        f"- Stations: {_pick_path('stations_cleaned.csv', 'stations.csv')}",
        f"- Maintenance: {_pick_path('maintenance_cleaned.csv', 'maintenance.csv')}",
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
        f"- Avg distance by user type: {t.groupby('user_type')['distance_km'].mean().round(2).to_dict()}",
        f"- Avg trips per user by user type: {trips_per_user.round(2).to_dict()}",
        "",
        "5) Fleet and utilization",
        f"- Bike utilization rate (approx): {utilization:.2f}%",
        f"- Most maintained bike: {top_maint_bike} ({top_maint_bike_count} records)",
        "",
        "6) Growth and retention",
        f"- Monthly trend growing: {bool(monthly.iloc[-1] > monthly.iloc[0]) if len(monthly) >= 2 else False}",
        f"- Monthly trend slope: {round(float(np.polyfit(np.arange(len(monthly)), monthly.values, 1)[0]), 3) if len(monthly) >= 2 else 'N/A'}",
        f"- Completion rate: {rate:.2f}% (Completed={completed}, Cancelled={cancelled})",
        "",
        "7) Business hotspots",
        f"- Top active user: {top_user} ({top_user_trips} trips)",
        f"- Top route: {top_route} ({top_route_count} trips)",
        "",
        "8) Maintenance spend",
        f"- Maintenance cost by bike type: {m.groupby('bike_type')['cost'].sum().round(2).to_dict()}",
        "",
        "9) Data quality / anomalies",
        f"- Outlier trips detected (z-score > 3 on duration/distance): {len(outliers)}",
        "",
        "Exported tables:",
        f"- {OUT_DIR / 'top_stations.csv'}",
        f"- {OUT_DIR / 'top_users.csv'}",
        f"- {OUT_DIR / 'maintenance_summary.csv'}",
    ]

    summary_path = OUT_DIR / "summary_report.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"Exported summary report to: {summary_path.resolve()}")


if __name__ == "__main__":
    run_report()
