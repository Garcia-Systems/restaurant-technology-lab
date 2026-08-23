"""Lightweight pre-presentation integrity checks."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .capstone import build_capstone
from .demand import ForecastScenario
from .loader import load_restaurant


CHECKS = ("Restaurant configuration", "Menu data", "Demand forecast", "Labor schedule",
          "Inventory data", "Customer feedback", "Friday Night Capstone")


def check_demo(data_dir: Path) -> tuple[bool, list[tuple[str, str | None]]]:
    """Load the foundation and integrated result, returning presenter-friendly results."""
    results: list[tuple[str, str | None]] = []
    try:
        load_restaurant(data_dir / "james_river_kitchen.json")
        results.append((CHECKS[0], None))
    except Exception as exc:  # health boundary must report malformed and missing inputs
        results.append((CHECKS[0], str(exc)))
        return False, results
    try:
        briefing = build_capstone(data_dir, ForecastScenario(date(2026, 8, 28), 174, "clear", False))
        components = (briefing.menu, briefing.demand, briefing.labor,
                      briefing.inventory, briefing.feedback, briefing)
        results.extend((name, None) for name, component in zip(CHECKS[1:], components) if component is not None)
    except Exception as exc:
        completed = {name for name, _ in results}
        results.extend((name, str(exc)) for name in CHECKS if name not in completed)
    return len(results) == len(CHECKS) and all(error is None for _, error in results), results
