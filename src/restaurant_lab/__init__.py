"""Executable foundation for the fictional James River Kitchen lab."""

from .loader import load_restaurant
from .model import DataSource, OperatingPeriod, Restaurant, RestaurantValidationError
from .summary import format_operational_summary

__all__ = [
    "DataSource",
    "OperatingPeriod",
    "Restaurant",
    "RestaurantValidationError",
    "format_operational_summary",
    "load_restaurant",
]
