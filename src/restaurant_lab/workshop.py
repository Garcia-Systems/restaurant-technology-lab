"""Presentation orchestration for the completed James River Kitchen examples."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from typing import Callable, Sequence


@dataclass(frozen=True)
class WorkshopSection:
    title: str
    script: str
    transition: str
    scenario_aware: bool = False


SECTIONS = (
    WorkshopSection("Restaurant as a System", "restaurant_system.py",
                    "We can see the systems. Next, ask what the sales data says about contribution."),
    WorkshopSection("Menu Profitability", "menu_profitability.py",
                    "We know what sold. Sales alone do not tell us how busy Friday will be."),
    WorkshopSection("Demand Forecast", "demand_forecast.py",
                    "Demand is a planning assumption. What does it mean for the team already scheduled?", True),
    WorkshopSection("Labor Planning", "labor_planning.py",
                    "We may have people scheduled. Do we have enough food for the same demand?", True),
    WorkshopSection("Inventory and Waste", "inventory_waste.py",
                    "The operating numbers are visible. What are guests actually experiencing?", True),
    WorkshopSection("Customer Feedback", "customer_feedback.py",
                    "Now bring the five signals together for Friday afternoon."),
    WorkshopSection("Friday Night Capstone", "friday_night_capstone.py",
                    "The software stops before the decision. The workshop ends with your operation.", True),
)

OPENING = """JAMES RIVER KITCHEN
Restaurant Technology Lab

A fictional independent restaurant in Williamsburg, Virginia.

Today's question:
What becomes possible when information from sales, reservations, staffing,
inventory, and customer feedback can be examined together?

This lab does not replace restaurant software. It demonstrates how disconnected
operational data can become useful business signals.
"""

DISCOVERY = """DISCOVERY DISCUSSION
------------------------------------------------------------
Which of these questions can your systems answer today?
Which require Excel or managers combining several reports?
Which operational problem do you usually discover too late?
What does your Friday-afternoon management routine look like?
Which useful information lives in separate systems?
Which alert would genuinely help rather than create noise?
If one operational question could be answered instantly, what would you choose?
"""


def run_workshop(repository_root: Path, *, pause: bool = True,
                 reservations: int | None = None, weather: str | None = None,
                 event: bool = False,
                 command_runner: Callable[[Sequence[str], Path], None] | None = None,
                 input_reader: Callable[[str], str] = input) -> None:
    """Run examples in narrative order; analytics remain in their chapter modules."""
    runner = command_runner or _run_command
    print(OPENING, flush=True)
    for section in SECTIONS:
        if pause:
            input_reader(f"Press Enter to continue to {section.title}...")
        print(f"\n{'=' * 60}\nJAMES RIVER KITCHEN\n{section.title}\n{'=' * 60}\n", flush=True)
        command = [sys.executable, str(repository_root / "examples" / section.script)]
        if section.scenario_aware:
            if reservations is not None:
                command.extend(("--reservations", str(reservations)))
            if weather is not None:
                command.extend(("--weather", weather))
            if event:
                command.append("--event")
        runner(command, repository_root)
        print(f"\nTRANSITION\n{section.transition}", flush=True)
    if pause:
        input_reader("Press Enter to begin the discovery discussion...")
    print(f"\n{DISCOVERY}", flush=True)


def _run_command(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)
