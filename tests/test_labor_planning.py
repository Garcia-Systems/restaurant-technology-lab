from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (ForecastScenario, RolePlanningAssumption, ScheduledShift,  # noqa: E402
    RestaurantValidationError, analyze_staffing, forecast_demand, load_demand_history,
    load_forecast_rules, load_labor_assumptions, load_reservations, load_schedule,
    override_scenario)

SCHEDULE = ROOT / "data" / "labor_schedule_2026-08-28.csv"
ASSUMPTIONS = ROOT / "data" / "labor_planning_assumptions.json"


class LaborPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        history = load_demand_history(ROOT / "data" / "demand_history_summer_2026.csv")
        self.reservations = load_reservations(ROOT / "data" / "reservations_august_2026.csv", history)
        self.rules = load_forecast_rules(ROOT / "data" / "demand_forecast_rules.json")
        self.history = history
        self.scenario = ForecastScenario(date(2026, 8, 28), 174, "clear", False)
        self.shifts = load_schedule(SCHEDULE)
        self.assumptions = load_labor_assumptions(ASSUMPTIONS)
        self.analysis = self.analyze(self.scenario)

    def analyze(self, scenario: ForecastScenario):
        forecast = forecast_demand(self.history, self.reservations, scenario, self.rules)
        return analyze_staffing(forecast, self.shifts, self.assumptions)

    def test_loads_fictional_schedule_and_all_roles(self) -> None:
        self.assertEqual(len(self.shifts), 22)
        self.assertEqual(self.shifts[0].employee_id, "jrk-h01")
        self.assertEqual({shift.role for shift in self.shifts},
                         {"host", "server", "bartender", "cook", "support"})
        self.assertEqual({row.role for row in self.assumptions},
                         {"host", "server", "bartender", "cook", "support"})

    def test_shift_duration_labor_hours_and_decimal_cost(self) -> None:
        self.assertEqual(self.shifts[0].duration_hours, Decimal("6.5"))
        self.assertEqual(self.shifts[0].labor_cost, Decimal("117.000"))
        self.assertEqual(self.analysis.total_hours, sum((s.duration_hours for s in self.shifts), Decimal("0")))
        self.assertEqual(self.analysis.total_cost, Decimal("2727.38"))

    def test_planning_ranges_derive_from_forecast_range_and_assumptions(self) -> None:
        roles = {row.role: row for row in self.analysis.roles}
        self.assertEqual((roles["server"].planning_low, roles["server"].planning_high), (8, 10))
        self.assertEqual((roles["host"].planning_low, roles["host"].planning_high), (2, 2))
        self.assertEqual((roles["cook"].planning_low, roles["cook"].planning_high), (6, 7))

    def test_compares_scheduled_counts_with_ranges(self) -> None:
        roles = {row.role: row for row in self.analysis.roles}
        self.assertEqual((roles["server"].scheduled, roles["server"].status), (7, "Below"))
        self.assertEqual((roles["cook"].scheduled, roles["cook"].status), (6, "Aligned"))
        self.assertEqual((roles["bartender"].scheduled, roles["bartender"].status), (3, "Aligned"))

    def test_low_normal_and_high_demand_scenarios_change_signals(self) -> None:
        low = self.analyze(override_scenario(self.scenario, reservations_booked=100, weather="rain"))
        high = self.analyze(override_scenario(self.scenario, reservations_booked=210, local_event=True))
        self.assertLess(low.forecast.expected_covers, self.analysis.forecast.expected_covers)
        self.assertEqual(self.analysis.forecast.expected_covers, 266)
        self.assertGreater(high.forecast.expected_covers, self.analysis.forecast.expected_covers)
        server = lambda result: next(row for row in result.roles if row.role == "server")
        self.assertEqual(server(low).status, "Aligned")
        self.assertEqual(server(self.analysis).status, "Below")
        self.assertEqual(server(high).planning_low, 10)

    def test_forecast_integration_overrides_do_not_mutate_schedule_or_scenario(self) -> None:
        original_shifts = tuple(self.shifts)
        original_scenario = self.scenario
        changed = override_scenario(self.scenario, local_event=True)
        result = self.analyze(changed)
        self.assertEqual(result.forecast.event_adjustment, 28)
        self.assertEqual(self.shifts, original_shifts)
        self.assertEqual(self.scenario, original_scenario)
        self.assertEqual(result.shifts, original_shifts)

    def test_rejects_bad_shift_times_rates_roles_and_identifiers(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "after shift start"):
            ScheduledShift("x", date(2026, 8, 28), "e", "host", time(18), time(17), Decimal("10"))
        with self.assertRaisesRegex(RestaurantValidationError, "hourly cost"):
            ScheduledShift("x", date(2026, 8, 28), "e", "host", time(17), time(18), Decimal("-1"))
        with self.assertRaisesRegex(RestaurantValidationError, "unsupported labor role"):
            ScheduledShift("x", date(2026, 8, 28), "e", "manager", time(17), time(18), Decimal("10"))
        self.assert_bad_schedule("x,2026-08-28,e,host,not-time,18:00,10.00\n", "malformed shift start")
        duplicate = ("x,2026-08-28,e1,host,17:00,18:00,10.00\n"
                     "x,2026-08-28,e2,host,17:00,18:00,10.00\n")
        self.assert_bad_schedule(duplicate, "duplicate shift identifiers")

    def test_rejects_invalid_assumptions_and_missing_or_mismatched_schedule(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "positive integer"):
            RolePlanningAssumption("server", 0, 1)
        with self.assertRaisesRegex(RestaurantValidationError, "non-negative integer"):
            RolePlanningAssumption("server", 10, -1)
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "empty.csv"
            empty.write_text("shift_id,date,employee_id,role,shift_start,shift_end,hourly_cost\n", encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, "cannot be empty"):
                load_schedule(empty)
        with self.assertRaisesRegex(RestaurantValidationError, "requires schedule"):
            analyze_staffing(self.analysis.forecast, (), self.assumptions)
        wrong_day = (ScheduledShift("x", date(2026, 8, 29), "e", "host", time(17), time(18), Decimal("10")),)
        with self.assertRaisesRegex(RestaurantValidationError, "match the forecast"):
            analyze_staffing(self.analysis.forecast, wrong_day, self.assumptions)

    def test_examples_show_default_low_and_high_scenarios(self) -> None:
        default = self.run_example()
        low = self.run_example("--weather", "rain", "--reservations", "100")
        high = self.run_example("--event", "--reservations", "210")
        self.assertIn("Expected covers:                  266", default)
        self.assertIn("Server               7", default)
        self.assertIn("planning signal, not an automatic staffing decision", default)
        self.assertIn("Changed expected covers: 176", low)
        self.assertIn("Changed expected covers: 326", high)
        self.assertIn("The schedule didn't change", high)

    def run_example(self, *arguments: str) -> str:
        return subprocess.run([sys.executable, "examples/labor_planning.py", *arguments], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout

    def assert_bad_schedule(self, rows: str, message: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "schedule.csv"
            path.write_text("shift_id,date,employee_id,role,shift_start,shift_end,hourly_cost\n" + rows,
                            encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, message):
                load_schedule(path)


if __name__ == "__main__":
    unittest.main()
