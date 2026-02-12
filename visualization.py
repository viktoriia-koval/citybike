"""Modul zum Erstellen und Speichern zentraler CityBike-Visualisierungen."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path("data")
OUT_DIR = Path("output") / "figures"


def _pick_path(cleaned_name: str, raw_name: str) -> Path:
    cleaned = DATA_DIR / cleaned_name
    return cleaned if cleaned.exists() else DATA_DIR / raw_name


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    trips = pd.read_csv(_pick_path("trips_cleaned.csv", "trips.csv"))
    maintenance = pd.read_csv(_pick_path("maintenance_cleaned.csv", "maintenance.csv"))

    trips["start_time"] = pd.to_datetime(trips["start_time"], errors="coerce")
    trips["duration_minutes"] = pd.to_numeric(trips["duration_minutes"], errors="coerce")
    trips["distance_km"] = pd.to_numeric(trips["distance_km"], errors="coerce")
    trips["user_type"] = trips["user_type"].astype(str).str.strip().str.lower()

    maintenance["cost"] = pd.to_numeric(maintenance["cost"], errors="coerce")
    maintenance["bike_type"] = maintenance["bike_type"].astype(str).str.strip().str.lower()
    return trips, maintenance


def _setup_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (11, 6),
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )


def _save(fig: plt.Figure, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout() # Passt die Abstände automatisch an
    fig.savefig(OUT_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


def bar_trips_per_station(trips: pd.DataFrame) -> None:
    """Erzeugt ein Balkendiagramm der zehn meistgenutzten Startstationen."""
    top = trips["start_station_id"].value_counts().head(10)
    fig, ax = plt.subplots()
    ax.bar(top.index, top.values, color="#2E86AB", label="Trip count")
    ax.set_title("Top 10 Start Stations by Trip Count")
    ax.set_xlabel("Start Station ID")
    ax.set_ylabel("Trips (count)")
    ax.legend()
    _save(fig, "bar_trips_per_station.png")


def line_monthly_trip_trend(trips: pd.DataFrame) -> None:
    """Erzeugt ein Liniendiagramm zum monatlichen Trend der Fahrten."""
    monthly = trips.set_index("start_time").resample("ME").size()
    fig, ax = plt.subplots()
    ax.plot(monthly.index, monthly.values, marker="o", color="#F18F01", label="Monthly trips")
    ax.set_title("Monthly Trip Volume Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Trips (count)")
    ax.legend()
    _save(fig, "line_monthly_trip_trend.png")


def histogram_trip_duration(trips: pd.DataFrame) -> None:
    """Erzeugt ein Histogramm der Fahrtdauer in Minuten."""
    durations = trips["duration_minutes"].dropna()
    fig, ax = plt.subplots()
    ax.hist(durations, bins=30, color="#4CAF50", alpha=0.85, label="Trip durations")
    ax.set_title("Distribution of Trip Duration")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Frequency (trips)")
    ax.legend()
    _save(fig, "hist_trip_duration.png")


def boxplot_duration_by_user_type(trips: pd.DataFrame) -> None:
    """Erzeugt einen Boxplot der Fahrtdauer nach Nutzertyp."""
    data = [
        trips.loc[trips["user_type"] == "casual", "duration_minutes"].dropna(),
        trips.loc[trips["user_type"] == "member", "duration_minutes"].dropna(),
    ]
    fig, ax = plt.subplots()
    bp = ax.boxplot(data, tick_labels=["casual", "member"], patch_artist=True)
    colors = ["#9C27B0", "#03A9F4"]
    for box, color in zip(bp["boxes"], colors):
        box.set_facecolor(color)
        box.set_alpha(0.55)

    ax.set_title("Trip Duration by User Type")
    ax.set_xlabel("User Type")
    ax.set_ylabel("Duration (minutes)")
    _save(fig, "box_duration_by_user_type.png")


def bar_revenue_by_user_type(
    trips: pd.DataFrame, base_fare: float = 1.0, per_km_rate: float = 0.4
) -> None:
    """Erzeugt ein Balkendiagramm des geschaetzten Umsatzes pro Nutzertyp."""
    revenue_df = trips[["user_type", "distance_km"]].copy()
    revenue_df["estimated_revenue"] = base_fare + revenue_df["distance_km"] * per_km_rate
    revenue = revenue_df.groupby("user_type")["estimated_revenue"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots()
    ax.bar(revenue.index, revenue.values, color="#E4572E", label="Estimated revenue")
    ax.set_title("Estimated Revenue by User Type")
    ax.set_xlabel("User Type")
    ax.set_ylabel("Revenue Euro")
    ax.legend()
    _save(fig, "bar_revenue_by_user_type.png")


def create_all_visualizations() -> None:
    """Laedt Daten und erstellt alle definierten Visualisierungen."""
    _setup_style()
    trips, maintenance = _load_data()
    bar_trips_per_station(trips)
    line_monthly_trip_trend(trips)
    histogram_trip_duration(trips)
    boxplot_duration_by_user_type(trips)
    bar_revenue_by_user_type(trips)
    print(f"Saved 5 figures to: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    create_all_visualizations()
