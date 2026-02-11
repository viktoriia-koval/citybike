"""Modul mit Preisstrategien zur Berechnung von Fahrtkosten."""

from abc import ABC, abstractmethod

from models import Trip


class PricingStrategy(ABC):
    """Abstrakte Basisklasse fuer alle Preisstrategien."""

    @abstractmethod
    def compute_cost(self, trip: Trip) -> float:
        """Berechnet den Preis fuer eine einzelne Fahrt."""
        pass


class CasualPricing(PricingStrategy):
    """Preisstrategie fuer Gelegenheitsnutzer."""

    def compute_cost(self, trip: Trip) -> float:
        """Berechnet den Preis fuer Gelegenheitsfahrten."""
        return trip.distance_km * 1.0


class MemberPricing(PricingStrategy):
    """Preisstrategie fuer Mitglieder mit reduziertem Kilometerpreis."""

    def compute_cost(self, trip: Trip) -> float:
        """Berechnet den Preis fuer Mitgliederfahrten."""
        return trip.distance_km * 0.5


class PeakHourPricing(PricingStrategy):
    """Dekoratorstrategie mit Zuschlag fuer Stosszeiten."""

    def __init__(self, base_strategy: PricingStrategy) -> None:
        self.base_strategy = base_strategy

    def compute_cost(self, trip: Trip) -> float:
        """Berechnet den Basispreis und wendet einen Stosszeiten-Zuschlag an."""
        base_cost = self.base_strategy.compute_cost(trip)
        return base_cost * 1.2
