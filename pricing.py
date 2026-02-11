from abc import ABC, abstractmethod
from models import Trip 

class PricingStrategy(ABC):
    @abstractmethod
    def compute_cost(self, trip: Trip) -> float:
        pass

class CasualPricing(PricingStrategy):
    def compute_cost(self, trip: Trip) -> float:
        # 1€ pro km
        return trip.distance_km * 1.0


class MemberPricing(PricingStrategy):
    def compute_cost(self, trip: Trip) -> float:
        # 0.5€ pro km
        return trip.distance_km * 0.5


class PeakHourPricing(PricingStrategy):
    def __init__(self, base_strategy: PricingStrategy):
        self.base_strategy = base_strategy

    def compute_cost(self, trip: Trip) -> float:
        base_cost = self.base_strategy.compute_cost(trip)
        # +20% Aufschlag
        return base_cost * 1.2