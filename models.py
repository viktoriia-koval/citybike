from abc import ABC, abstractmethod
from datetime import datetime

class Entity(ABC):
    """
    Abstrakte Basisklasse für alle Entitäten im System
    """

    def __init__(self, entity_id: str):
        self.id = entity_id
        self.created_at = datetime.now()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass
class Bike(Entity):
    """
    Basisklasse für Fahrräder
    """

    VALID_STATUS = {"available", "in_use", "maintenance"}

    def __init__(self, bike_id: str, bike_type: str, status: str):
        if status not in self.VALID_STATUS:
            raise ValueError("Ungültiger Fahrradstatus")

        super().  __init__(bike_id)
        self.bike_id = bike_id
        self.bike_type = bike_type
        self.status = status

    def __str__(self) -> str:
        return f"Bike {self.bike_id} ({self.bike_type})"

    def __repr__(self) -> str:
        return (
            f"Bike(bike_id={self.bike_id}, "
            f"bike_type={self.bike_type}, status={self.status})"
        )
class ClassicBike(Bike):
    """
    Klassisches Fahrrad
    """

    def __init__(self, bike_id: str, gear_count: int):
        if gear_count <= 0:
            raise ValueError("Ganganzahl muss positiv sein")

        super().__init__(bike_id, "classic", "available")
        self.gear_count = gear_count

    def __repr__(self) -> str:
        return (
            f"ClassicBike(bike_id={self.bike_id}, "
            f"gear_count={self.gear_count})"
        )
class ElectricBike(Bike):
    """
    Elektrisches Fahrrad
    """

    def __init__(self, bike_id: str, battery_level: float, max_range_km: float):
        if battery_level < 0:
            raise ValueError("Batteriestand darf nicht negativ sein")
        if max_range_km <= 0:
            raise ValueError("Maximale Reichweite muss positiv sein")

        super().__init__(bike_id, "electric", "available")
        self.battery_level = battery_level
        self.max_range_km = max_range_km

    def __repr__(self) -> str:
        return (
            f"ElectricBike(bike_id={self.bike_id}, "
            f"battery_level={self.battery_level}, "
            f"max_range_km={self.max_range_km})"
        )
class Station(Entity):
    """
    Fahrradstation
    """

    def __init__(
        self,
        station_id: str,
        name: str,
        capacity: int,
        latitude: float,
        longitude: float,
    ):
        if capacity <= 0:
            raise ValueError("Kapazität muss positiv sein")

        super().__init__(station_id)
        self.station_id = station_id
        self.name = name
        self.capacity = capacity
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self) -> str:
        return f"Station {self.name}"

    def __repr__(self) -> str:
        return (
            f"Station(station_id={self.station_id}, "
            f"name={self.name}, capacity={self.capacity})"
        )
class User(Entity):
    """
    Basisklasse für Nutzer
    """

    def __init__(self, user_id: str, name: str, email: str, user_type: str):
        if "@" not in email:
            raise ValueError("Ungültige E-Mail-Adresse")

        super().__init__(user_id)
        self.user_id = user_id
        self.name = name
        self.email = email
        self.user_type = user_type

    def __str__(self) -> str:
        return f"User {self.name} ({self.user_type})"

    def __repr__(self) -> str:
        return (
            f"User(user_id={self.user_id}, "
            f"name={self.name}, user_type={self.user_type})"
        )
class CasualUser(User):
    """
    Gelegenheitsnutzer
    """

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        day_pass_count: int,
    ):
        if day_pass_count < 0:
            raise ValueError("Anzahl der Tagespässe darf nicht negativ sein")

        super().__init__(user_id, name, email, "casual")
        self.day_pass_count = day_pass_count

    def __repr__(self) -> str:
        return (
            f"CasualUser(user_id={self.user_id}, "
            f"day_pass_count={self.day_pass_count})"
        )
class MemberUser(User):
    """
    Mitgliedsnutzer
    """

    VALID_TIERS = {"basic", "premium"}

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        membership_start: datetime,
        membership_end: datetime,
        tier: str,
    ):
        if tier not in self.VALID_TIERS:
            raise ValueError("Ungültiger Mitgliedschaftstyp")
        if membership_end <= membership_start:
            raise ValueError("Enddatum muss nach dem Startdatum liegen")

        super().__init__(user_id, name, email, "member")
        self.membership_start = membership_start
        self.membership_end = membership_end
        self.tier = tier

    def __repr__(self) -> str:
        return (
            f"MemberUser(user_id={self.user_id}, "
            f"tier={self.tier})"
        )
class Trip:
    """
    Fahrt im Bike-Sharing-System
    """

    def __init__(
        self,
        trip_id: str,
        user: User,
        bike: Bike,
        start_station: Station,
        end_station: Station,
        start_time: datetime,
        end_time: datetime,
        distance_km: float,
    ):
        if distance_km < 0:
            raise ValueError("Distanz darf nicht negativ sein")
        if end_time < start_time:
            raise ValueError("Endzeit liegt vor Startzeit")

        self.trip_id = trip_id
        self.user = user
        self.bike = bike
        self.start_station = start_station
        self.end_station = end_station
        self.start_time = start_time
        self.end_time = end_time
        self.distance_km = distance_km

    @property
    def duration_minutes(self) -> float:
        """Dauer der Fahrt in Minuten"""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 60

    def __str__(self) -> str:
        return f"Trip {self.trip_id}"

    def __repr__(self) -> str:
        return (
            f"Trip(trip_id={self.trip_id}, "
            f"distance_km={self.distance_km})"
        )
class MaintenanceRecord:
    """
    Wartungseintrag für ein Fahrrad
    """

    def __init__(
        self,
        record_id: str,
        bike: Bike,
        date: datetime,
        maintenance_type: str,
        cost: float,
        description: str,
    ):
        if cost < 0:
            raise ValueError("Kosten dürfen nicht negativ sein")

        self.record_id = record_id
        self.bike = bike
        self.date = date
        self.maintenance_type = maintenance_type
        self.cost = cost
        self.description = description

    def __str__(self) -> str:
        return f"Maintenance {self.record_id}"

    def __repr__(self) -> str:
        return (
            f"MaintenanceRecord(record_id={self.record_id}, "
            f"cost={self.cost})"
        )
