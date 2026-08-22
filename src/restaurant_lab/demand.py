"""Domain contracts for James River Kitchen's explainable demand forecast."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .model import RestaurantValidationError


SUPPORTED_WEATHER = frozenset({"clear", "cloudy", "rain", "storms", "hot"})


@dataclass(frozen=True)
class DemandObservation:
    service_date: date
    total_covers: int
    revenue: Decimal
    weather: str
    local_event: bool

    def __post_init__(self) -> None:
        if isinstance(self.total_covers, bool) or not isinstance(self.total_covers, int) or self.total_covers < 0:
            raise RestaurantValidationError("historical covers must be a non-negative integer")
        if not self.revenue.is_finite() or self.revenue < 0:
            raise RestaurantValidationError("historical revenue must be a finite, non-negative amount")
        if self.weather not in SUPPORTED_WEATHER:
            raise RestaurantValidationError(f"unsupported weather value: {self.weather}")


@dataclass(frozen=True)
class ReservationSnapshot:
    service_date: date
    booked_covers: int

    def __post_init__(self) -> None:
        if isinstance(self.booked_covers, bool) or not isinstance(self.booked_covers, int) or self.booked_covers < 0:
            raise RestaurantValidationError("reservations booked must be a non-negative integer")


@dataclass(frozen=True)
class ForecastRules:
    reservation_show_rate: Decimal
    event_rate: Decimal
    weather_rates: dict[str, Decimal]
    range_rate: Decimal

    def __post_init__(self) -> None:
        rates = {
            "reservation show rate": self.reservation_show_rate,
            "event rate": self.event_rate,
            "range rate": self.range_rate,
            **{f"weather rate {name}": value for name, value in self.weather_rates.items()},
        }
        if set(self.weather_rates) != SUPPORTED_WEATHER:
            raise RestaurantValidationError("forecast rules must define every supported weather value")
        if any(not value.is_finite() for value in rates.values()):
            raise RestaurantValidationError("forecast rule rates must be finite")
        if not Decimal("0") <= self.reservation_show_rate <= Decimal("1"):
            raise RestaurantValidationError("reservation show rate must be between 0 and 1")
        if self.event_rate < 0 or self.range_rate <= 0:
            raise RestaurantValidationError("event rate must be non-negative and range rate must be positive")
        if any(value <= Decimal("-1") for value in self.weather_rates.values()):
            raise RestaurantValidationError("weather rates must be greater than -1")


@dataclass(frozen=True)
class ForecastScenario:
    target_date: date
    reservations_booked: int
    weather: str
    local_event: bool

    def __post_init__(self) -> None:
        ReservationSnapshot(self.target_date, self.reservations_booked)
        if self.weather not in SUPPORTED_WEATHER:
            raise RestaurantValidationError(f"unsupported weather value: {self.weather}")


@dataclass(frozen=True)
class DemandForecast:
    scenario: ForecastScenario
    weekly_baseline: Decimal
    weekday_baseline: Decimal
    typical_reservations: Decimal
    day_adjustment: int
    reservation_adjustment: int
    event_adjustment: int
    weather_adjustment: int
    expected_covers: int
    range_low: int
    range_high: int
    revenue_per_cover: Decimal
    expected_revenue: Decimal

    @property
    def expected_walk_ins(self) -> int:
        return max(0, self.expected_covers - self.scenario.reservations_booked)
