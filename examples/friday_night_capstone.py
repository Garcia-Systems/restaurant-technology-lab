#!/usr/bin/env python3
"""Run the integrated fictional Friday-afternoon management briefing."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import ForecastScenario, RestaurantValidationError, SUPPORTED_WEATHER  # noqa: E402
from restaurant_lab.capstone import build_capstone  # noqa: E402
from restaurant_lab.capstone_summary import format_capstone  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="James River Kitchen Friday readiness briefing")
    def non_negative(value: str) -> int:
        parsed = int(value)
        if parsed < 0:
            raise argparse.ArgumentTypeError("reservations must be a non-negative integer")
        return parsed

    parser.add_argument("--reservations", type=non_negative, default=174, help="booked covers (default: 174)")
    parser.add_argument("--event", action="store_true", help="include the documented local-event adjustment")
    parser.add_argument("--weather", choices=sorted(SUPPORTED_WEATHER), default="clear")
    parser.add_argument("--explain", action="store_true", help="show evidence behind every readiness signal")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        scenario = ForecastScenario(date(2026, 8, 28), args.reservations, args.weather, args.event)
        print(format_capstone(build_capstone(ROOT / "data", scenario), explain=args.explain), end="")
    except RestaurantValidationError as exc:
        print(f"Scenario error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
