#!/usr/bin/env python3
"""Connect forecast demand with fictional recipes, inventory, and recorded waste."""

import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (ForecastScenario, RestaurantValidationError, SUPPORTED_WEATHER,  # noqa: E402
    analyze_inventory, forecast_demand, format_inventory_analysis, format_inventory_comparison,
    load_demand_history, load_forecast_rules, load_ingredients, load_inventory, load_menu,
    load_recipes, load_reservations, load_sales, load_waste, override_scenario,
    simulate_ingredient_cost, validate_recipe_costs)


def non_negative(value: str) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("reservations must be a non-negative integer") from error
    if result < 0:
        raise argparse.ArgumentTypeError("reservations must be a non-negative integer")
    return result


def cost_change(value: str) -> tuple[str, Decimal]:
    try:
        identifier, raw = value.split("=", 1)
        cost = Decimal(raw)
    except (ValueError, InvalidOperation) as error:
        raise argparse.ArgumentTypeError("ingredient cost must use ingredient-id=amount") from error
    if not identifier or not cost.is_finite() or cost < 0:
        raise argparse.ArgumentTypeError("ingredient cost must be finite and non-negative")
    return identifier, cost


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--reservations", type=non_negative, help="change booked covers")
    result.add_argument("--weather", choices=sorted(SUPPORTED_WEATHER), help="change forecast weather")
    result.add_argument("--event", action="store_true", help="compare a local-event demand scenario")
    result.add_argument("--ingredient-cost", type=cost_change, help="simulate ingredient-id=unit-cost")
    return result


def main() -> None:
    argument_parser, target = parser(), date(2026, 8, 28)
    arguments = argument_parser.parse_args()
    try:
        menu = load_menu(ROOT / "data/menu.csv")
        sales = load_sales(ROOT / "data/menu_sales_july_2026.csv", menu)
        ingredients = load_ingredients(ROOT / "data/ingredients.csv")
        recipes = load_recipes(ROOT / "data/recipes.csv", menu, ingredients)
        validate_recipe_costs(menu, ingredients, recipes)
        inventory = load_inventory(ROOT / "data/inventory_on_hand_2026-08-28.csv", ingredients)
        waste = load_waste(ROOT / "data/waste_august_2026.csv", ingredients)
        history = load_demand_history(ROOT / "data/demand_history_summer_2026.csv")
        reservations = load_reservations(ROOT / "data/reservations_august_2026.csv", history)
        rules = load_forecast_rules(ROOT / "data/demand_forecast_rules.json")
        snapshot = next(row for row in reservations if row.service_date == target)
        scenario = ForecastScenario(target, snapshot.booked_covers, "clear", False)
        base_forecast = forecast_demand(history, reservations, scenario, rules)
        base = analyze_inventory(base_forecast, ingredients, recipes, inventory, waste, sales)
        changes = {}
        if arguments.reservations is not None: changes["reservations_booked"] = arguments.reservations
        if arguments.weather is not None: changes["weather"] = arguments.weather
        if arguments.event: changes["local_event"] = True
        scenario_ingredients = ingredients
        if arguments.ingredient_cost:
            scenario_ingredients = simulate_ingredient_cost(ingredients, *arguments.ingredient_cost)
        if changes or arguments.ingredient_cost:
            changed_forecast = forecast_demand(history, reservations, override_scenario(scenario, **changes), rules)
            changed = analyze_inventory(changed_forecast, scenario_ingredients, recipes, inventory, waste, sales)
            print(format_inventory_analysis(changed))
            print(format_inventory_comparison(base, changed))
            if arguments.ingredient_cost:
                identifier, cost = arguments.ingredient_cost
                old = next(row for row in base.coverage if row.ingredient.ingredient_id == identifier)
                new = next(row for row in changed.coverage if row.ingredient.ingredient_id == identifier)
                print(f"\nCOST SCENARIO — {old.ingredient.name}\nRecorded waste quantity unchanged: {old.waste_quantity} {old.ingredient.unit}\n"
                      f"Original waste cost: ${old.waste_cost:,.2f}\nSimulated unit cost: ${cost:,.2f}\nSimulated waste cost: ${new.waste_cost:,.2f}")
        else:
            print(format_inventory_analysis(base))
    except (RestaurantValidationError, StopIteration) as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
