import pandas as pd
from analyzer import BikeShareSystem

# Daten laden
trips = pd.read_csv("data/trips.csv")

# Datumsfelder parsen
trips["start_time"] = pd.to_datetime(trips["start_time"])
trips["end_time"] = pd.to_datetime(trips["end_time"])

# Ungültige Trips entfernen
trips = trips[trips["end_time"] >= trips["start_time"]]

system = BikeShareSystem(trips)

if __name__ == "__main__":
    main()
