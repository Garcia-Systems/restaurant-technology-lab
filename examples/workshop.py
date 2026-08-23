#!/usr/bin/env python3
"""Run the complete James River Kitchen workshop."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import SUPPORTED_WEATHER  # noqa: E402
from restaurant_lab.workshop import run_workshop  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-pause", action="store_true", help="run without presenter prompts")
    parser.add_argument("--reservations", type=int, help="propagate booked covers through scenario-aware sections")
    parser.add_argument("--weather", choices=sorted(SUPPORTED_WEATHER), help="propagate weather")
    parser.add_argument("--event", action="store_true", help="propagate the local-event assumption")
    args = parser.parse_args()
    if args.reservations is not None and args.reservations < 0:
        parser.error("reservations must be a non-negative integer")
    run_workshop(ROOT, pause=not args.no_pause, reservations=args.reservations,
                 weather=args.weather, event=args.event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
