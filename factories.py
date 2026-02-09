from models import Bike, ClassicBike, ElectricBike, User, CasualUser, MemberUser

class BikeFactory:
    @staticmethod
    def from_row(row: dict) -> Bike:
        bike_type = row.get("bike_type")

        if bike_type == "classic":
            return ClassicBike(
                bike_id=row["bike_id"],
                gear_count=int(row["gear_count"]),
            )
        elif bike_type == "electric":
            return ElectricBike(
                bike_id=row["bike_id"],
                battery_level=float(row["battery_level"]),
                max_range_km=float(row["max_range_km"]),
            )
        else:
            return Bike(
                bike_id=row["bike_id"],
                bike_type=bike_type,
                status=row.get("status", "available"),
            )

class UserFactory:
    @staticmethod
    def from_row(row: dict) -> User:
        user_type = row.get("user_type")

        if user_type == "casual":
            return CasualUser(
                user_id=row["user_id"],
                name=row["name"],
                email=row["email"],
                day_pass_count=int(row["day_pass_count"]),
            )
        elif user_type == "member":
            return MemberUser(
                user_id=row["user_id"],
                name=row["name"],
                email=row["email"],
                membership_start=row["membership_start"],
                membership_end=row["membership_end"],
                tier=row["tier"],
            )
        else:
            raise ValueError("Unbekannter Nutzertyp")
