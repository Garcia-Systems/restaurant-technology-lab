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
from .labor import (LABOR_ROLES, RolePlanningAssumption, RoleStaffingAlignment,
                    ScheduledShift, StaffingAnalysis)
from .labor_loader import load_labor_assumptions, load_schedule
from .labor_planning import analyze_staffing
from .labor_summary import format_staffing_analysis, format_staffing_comparison
from .inventory import (SUPPORTED_UNITS, WASTE_REASONS, Ingredient, IngredientCoverage,
                        InventoryAnalysis, InventoryCount, RecipeComponent, WasteEvent,
                        validate_recipe_costs)
from .inventory_loader import load_ingredients, load_inventory, load_recipes, load_waste
from .inventory_planning import (analyze_inventory, calculate_menu_mix, expected_ingredient_demand,
                                 historical_ingredient_usage, simulate_ingredient_cost)
from .inventory_summary import format_inventory_analysis, format_inventory_comparison
from .feedback import (ClassifiedReview, FeedbackAnalysis, Review, TopicSignal,
                       TopicSummary, TopicTrend)
from .feedback_analysis import TOPIC_RULES, analyze_feedback, classify_review, drill_down
from .feedback_loader import load_reviews
from .capstone import CapstoneBriefing, PRIORITIES, ReadinessSignal, build_capstone, generate_signals
from .capstone_summary import format_capstone

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
    "LABOR_ROLES",
    "RolePlanningAssumption",
    "RoleStaffingAlignment",
    "ScheduledShift",
    "StaffingAnalysis",
    "analyze_staffing",
    "format_staffing_analysis",
    "format_staffing_comparison",
    "load_labor_assumptions",
    "load_schedule",
    "SUPPORTED_UNITS", "WASTE_REASONS", "Ingredient", "IngredientCoverage",
    "InventoryAnalysis", "InventoryCount", "RecipeComponent", "WasteEvent",
    "validate_recipe_costs", "load_ingredients", "load_inventory", "load_recipes", "load_waste",
    "analyze_inventory", "calculate_menu_mix", "expected_ingredient_demand",
    "historical_ingredient_usage", "simulate_ingredient_cost", "format_inventory_analysis",
    "format_inventory_comparison",
    "ClassifiedReview", "FeedbackAnalysis", "Review", "TopicSignal", "TopicSummary",
    "TopicTrend", "TOPIC_RULES", "analyze_feedback", "classify_review", "drill_down",
    "load_reviews", "CapstoneBriefing", "PRIORITIES", "ReadinessSignal", "build_capstone",
    "generate_signals", "format_capstone",
]
