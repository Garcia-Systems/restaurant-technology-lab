#!/usr/bin/env python3
"""Compare James River Kitchen's fixed schedule with forecast-driven labor ranges."""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (ForecastScenario, RestaurantValidationError, SUPPORTED_WEATHER,  # noqa: E402
    analyze_staffing, forecast_demand, format_staffing_analysis, format_staffing_comparison,
    load_demand_history, load_forecast_rules, load_labor_assumptions, load_reservations,
    load_schedule, override_scenario)


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
    result.add_argument("--reservations", type=non_negative, help="change booked covers")
    result.add_argument("--weather", choices=sorted(SUPPORTED_WEATHER), help="change forecast weather")
    result.add_argument("--event", action="store_true", help="compare a local-event demand scenario")
    return result


def main() -> None:
    argument_parser = parser()
    arguments = argument_parser.parse_args()
    try:
        target = date(2026, 8, 28)
        history = load_demand_history(ROOT / "data" / "demand_history_summer_2026.csv")
        reservations = load_reservations(ROOT / "data" / "reservations_august_2026.csv", history)
        rules = load_forecast_rules(ROOT / "data" / "demand_forecast_rules.json")
        shifts = load_schedule(ROOT / "data" / "labor_schedule_2026-08-28.csv")
        assumptions = load_labor_assumptions(ROOT / "data" / "labor_planning_assumptions.json")
        snapshot = next((row for row in reservations if row.service_date == target), None)
        if snapshot is None:
            raise RestaurantValidationError(f"no reservation snapshot for target date {target}")
        scenario = ForecastScenario(target, snapshot.booked_covers, "clear", False)
        base = analyze_staffing(forecast_demand(history, reservations, scenario, rules), shifts, assumptions)
        changes = {}
        if arguments.reservations is not None:
            changes["reservations_booked"] = arguments.reservations
        if arguments.weather is not None:
            changes["weather"] = arguments.weather
        if arguments.event:
            changes["local_event"] = True
        if changes:
            changed_forecast = forecast_demand(history, reservations, override_scenario(scenario, **changes), rules)
            changed = analyze_staffing(changed_forecast, shifts, assumptions)
            print(format_staffing_analysis(changed))
            print(format_staffing_comparison(base, changed))
        else:
            print(format_staffing_analysis(base))
    except RestaurantValidationError as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
