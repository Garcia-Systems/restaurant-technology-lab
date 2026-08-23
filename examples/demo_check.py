#!/usr/bin/env python3
"""Verify that the local repository is healthy for a live demonstration."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab.demo_check import check_demo  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data", help=argparse.SUPPRESS)
    args = parser.parse_args()
    print("Restaurant Technology Lab — Demo Check\n")
    healthy, results = check_demo(args.data_dir)
    for name, error in results:
        print(f"[{'OK' if error is None else 'FAIL'}] {name}" + (f": {error}" if error else ""))
    print("\nDemo environment ready." if healthy else "\nDemo environment is not ready.")
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
