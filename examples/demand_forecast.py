#!/usr/bin/env python3
"""Forecast James River Kitchen demand and compare optional scenario changes."""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (ForecastScenario, RestaurantValidationError, SUPPORTED_WEATHER,  # noqa: E402
    forecast_demand, format_demand_forecast, format_scenario_comparison,
    load_demand_history, load_forecast_rules, load_reservations, override_scenario)


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error


def non_negative(value: str) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("reservations must be a non-negative integer") from error
    if result < 0:
        raise argparse.ArgumentTypeError("reservations must be a non-negative integer")
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--date", type=parse_date, default=date(2026, 8, 28), help="target date (YYYY-MM-DD)")
    result.add_argument("--reservations", type=non_negative, help="change booked covers")
    result.add_argument("--weather", choices=sorted(SUPPORTED_WEATHER), help="change forecast weather")
    result.add_argument("--event", action="store_true", help="compare a local-event scenario")
    return result


def main() -> None:
    argument_parser = parser()
    arguments = argument_parser.parse_args()
    try:
        history = load_demand_history(ROOT / "data" / "demand_history_summer_2026.csv")
        reservations = load_reservations(ROOT / "data" / "reservations_august_2026.csv", history)
        rules = load_forecast_rules(ROOT / "data" / "demand_forecast_rules.json")
        snapshot = next((row for row in reservations if row.service_date == arguments.date), None)
        if snapshot is None:
            raise RestaurantValidationError(f"no reservation snapshot for target date {arguments.date}")
        base_scenario = ForecastScenario(arguments.date, snapshot.booked_covers, "clear", False)
        base = forecast_demand(history, reservations, base_scenario, rules)
        changes = {}
        if arguments.reservations is not None:
            changes["reservations_booked"] = arguments.reservations
        if arguments.weather is not None:
            changes["weather"] = arguments.weather
        if arguments.event:
            changes["local_event"] = True
        if changes:
            changed = forecast_demand(history, reservations, override_scenario(base_scenario, **changes), rules)
            print(format_demand_forecast(changed))
            print(format_scenario_comparison(base, changed))
        else:
            print(format_demand_forecast(base))
    except RestaurantValidationError as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
