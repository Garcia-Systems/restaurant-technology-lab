#!/usr/bin/env python3
"""Print the introductory James River Kitchen system briefing."""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from restaurant_lab import format_operational_summary, load_restaurant  # noqa: E402


def main() -> None:
    restaurant = load_restaurant(REPOSITORY_ROOT / "data" / "james_river_kitchen.json")
    print(format_operational_summary(restaurant))


if __name__ == "__main__":
    main()
