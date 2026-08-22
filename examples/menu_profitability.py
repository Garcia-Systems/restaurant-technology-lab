#!/usr/bin/env python3
"""Analyze James River Kitchen menu contribution or simulate one price."""

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from restaurant_lab import (  # noqa: E402
    RestaurantValidationError, analyze_menu, format_menu_analysis,
    load_menu, load_sales, simulate_price,
)


def parse_price(value: str) -> Decimal:
    try:
        price = Decimal(value)
    except InvalidOperation as error:
        raise argparse.ArgumentTypeError("price must be a monetary number") from error
    if not price.is_finite() or price.as_tuple().exponent < -2:
        raise argparse.ArgumentTypeError("price must be finite with at most two decimal places")
    return price


def build_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--item", help="stable item ID to simulate (requires --price)")
    result.add_argument("--price", type=parse_price, help="simulated selling price")
    return result


def main() -> None:
    argument_parser = build_parser()
    arguments = argument_parser.parse_args()
    if (arguments.item is None) != (arguments.price is None):
        argument_parser.error("--item and --price must be supplied together")
    try:
        menu = load_menu(REPOSITORY_ROOT / "data" / "menu.csv")
        sales = load_sales(REPOSITORY_ROOT / "data" / "menu_sales_july_2026.csv", menu)
        baseline_item = None
        if arguments.item is not None:
            baseline_item = next((item for item in menu if item.item_id == arguments.item), None)
            menu = simulate_price(menu, arguments.item, arguments.price)
        print(format_menu_analysis(analyze_menu(menu, sales), baseline_item=baseline_item))
    except RestaurantValidationError as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
