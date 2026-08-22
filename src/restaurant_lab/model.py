"""Small domain contracts shared by the restaurant lab chapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time


WEEKDAYS = {
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
}
REQUIRED_SOURCE_IDS = {"pos", "reservations", "scheduling", "inventory", "reviews"}


class RestaurantValidationError(ValueError):
    """Raised when restaurant configuration violates a business contract."""


def _required_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RestaurantValidationError(f"{field} must be a non-empty string")


def _parse_time(value: str, field: str) -> time:
    try:
        return time.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise RestaurantValidationError(f"{field} must use 24-hour HH:MM format") from error


@dataclass(frozen=True)
class OperatingPeriod:
    days: tuple[str, ...]
    service: str
    opens: str
    closes: str

    def __post_init__(self) -> None:
        if not self.days:
            raise RestaurantValidationError("operating period days cannot be empty")
        unknown_days = set(self.days) - WEEKDAYS
        if unknown_days:
            raise RestaurantValidationError(
                f"operating period contains unknown day(s): {', '.join(sorted(unknown_days))}"
            )
        if len(set(self.days)) != len(self.days):
            raise RestaurantValidationError("operating period days cannot contain duplicates")
        _required_text(self.service, "operating period service")
        opens = _parse_time(self.opens, "operating period opens")
        closes = _parse_time(self.closes, "operating period closes")
        if opens >= closes:
            raise RestaurantValidationError("operating period must close after it opens")


@dataclass(frozen=True)
class DataSource:
    identifier: str
    name: str
    provides: str

    def __post_init__(self) -> None:
        _required_text(self.identifier, "data source id")
        _required_text(self.name, "data source name")
        _required_text(self.provides, "data source provides")


@dataclass(frozen=True)
class Restaurant:
    name: str
    location: str
    concept: str
    fictional: bool
    capacity: int
    operating_periods: tuple[OperatingPeriod, ...]
    menu_categories: tuple[str, ...]
    sales_channels: tuple[str, ...]
    data_sources: tuple[DataSource, ...]

    def __post_init__(self) -> None:
        _required_text(self.name, "restaurant name")
        _required_text(self.location, "restaurant location")
        _required_text(self.concept, "restaurant concept")
        if self.fictional is not True:
            raise RestaurantValidationError("lab restaurant data must be marked fictional")
        if isinstance(self.capacity, bool) or not isinstance(self.capacity, int) or self.capacity <= 0:
            raise RestaurantValidationError("capacity must be a positive integer")
        if not self.operating_periods:
            raise RestaurantValidationError("at least one operating period is required")
        self._validate_text_collection(self.menu_categories, "menu categories")
        self._validate_text_collection(self.sales_channels, "sales channels")

        identifiers = [source.identifier for source in self.data_sources]
        duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
        if duplicates:
            raise RestaurantValidationError(
                f"duplicate data source id(s): {', '.join(duplicates)}"
            )
        missing = sorted(REQUIRED_SOURCE_IDS - set(identifiers))
        if missing:
            raise RestaurantValidationError(
                f"missing required operational data source(s): {', '.join(missing)}"
            )

    @staticmethod
    def _validate_text_collection(values: tuple[str, ...], field: str) -> None:
        if not values:
            raise RestaurantValidationError(f"{field} cannot be empty")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise RestaurantValidationError(f"{field} must contain non-empty strings")
        if len(set(values)) != len(values):
            raise RestaurantValidationError(f"{field} cannot contain duplicates")
