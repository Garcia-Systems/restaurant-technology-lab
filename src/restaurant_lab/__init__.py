"""Executable foundation for the fictional James River Kitchen lab."""

from .loader import load_restaurant
from .menu import ItemProfitability, MenuAnalysis, MenuItem, SalesRecord
from .menu_loader import load_menu, load_sales
from .menu_summary import format_menu_analysis
from .model import DataSource, OperatingPeriod, Restaurant, RestaurantValidationError
from .profitability import analyze_menu, rank_by_contribution, simulate_price
from .summary import format_operational_summary
from .demand import (DemandForecast, DemandObservation, ForecastRules,
                     ForecastScenario, ReservationSnapshot, SUPPORTED_WEATHER)
from .demand_loader import load_demand_history, load_forecast_rules, load_reservations
from .demand_summary import format_demand_forecast, format_scenario_comparison
from .forecasting import forecast_demand, override_scenario

__all__ = [
    "DataSource",
    "ItemProfitability",
    "MenuAnalysis",
    "MenuItem",
    "OperatingPeriod",
    "Restaurant",
    "RestaurantValidationError",
    "SalesRecord",
    "analyze_menu",
    "format_menu_analysis",
    "format_operational_summary",
    "load_restaurant",
    "load_menu",
    "load_sales",
    "rank_by_contribution",
    "simulate_price",
    "DemandForecast",
    "DemandObservation",
    "ForecastRules",
    "ForecastScenario",
    "ReservationSnapshot",
    "SUPPORTED_WEATHER",
    "forecast_demand",
    "format_demand_forecast",
    "format_scenario_comparison",
    "load_demand_history",
    "load_forecast_rules",
    "load_reservations",
    "override_scenario",
]
