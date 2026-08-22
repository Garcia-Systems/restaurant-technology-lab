from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (DemandObservation, ForecastScenario, ReservationSnapshot,  # noqa: E402
    RestaurantValidationError, forecast_demand, load_demand_history, load_forecast_rules,
    load_reservations, override_scenario)

HISTORY = ROOT / "data" / "demand_history_summer_2026.csv"
RESERVATIONS = ROOT / "data" / "reservations_august_2026.csv"
RULES = ROOT / "data" / "demand_forecast_rules.json"


class DemandForecastTests(unittest.TestCase):
    def setUp(self) -> None:
        self.history = load_demand_history(HISTORY)
        self.reservations = load_reservations(RESERVATIONS, self.history)
        self.rules = load_forecast_rules(RULES)
        self.scenario = ForecastScenario(date(2026, 8, 28), 174, "clear", False)
        self.forecast = forecast_demand(self.history, self.reservations, self.scenario, self.rules)

    def test_loads_human_sized_historical_demand(self) -> None:
        self.assertEqual(len(self.history), 32)
        self.assertEqual(self.history[0].service_date, date(2026, 7, 27))
        self.assertIsInstance(self.history[0].revenue, Decimal)

    def test_loads_historical_and_target_reservation_snapshots(self) -> None:
        self.assertEqual(len(self.reservations), 33)
        self.assertEqual(self.reservations[-1], ReservationSnapshot(date(2026, 8, 28), 174))

    def test_calculates_weekday_baseline_and_day_behavior(self) -> None:
        self.assertEqual(self.forecast.weekday_baseline, Decimal("233.75"))
        self.assertEqual(self.forecast.day_adjustment, 55)
        monday = forecast_demand(self.history, self.reservations,
            ForecastScenario(date(2026, 8, 24), 87, "clear", False), self.rules)
        self.assertLess(monday.weekday_baseline, self.forecast.weekday_baseline)

    def test_reservation_event_and_weather_adjustments_are_explicit(self) -> None:
        self.assertEqual(self.forecast.reservation_adjustment, 32)
        event = forecast_demand(self.history, self.reservations,
            override_scenario(self.scenario, local_event=True), self.rules)
        rain = forecast_demand(self.history, self.reservations,
            override_scenario(self.scenario, weather="rain"), self.rules)
        self.assertEqual(event.event_adjustment, 28)
        self.assertEqual(event.expected_covers - self.forecast.expected_covers, 28)
        self.assertEqual(rain.weather_adjustment, -23)
        self.assertEqual(rain.expected_covers - self.forecast.expected_covers, -23)

    def test_range_and_revenue_forecast_are_derived(self) -> None:
        self.assertEqual(self.forecast.expected_covers, 266)
        self.assertEqual((self.forecast.range_low, self.forecast.range_high), (239, 293))
        self.assertEqual(self.forecast.expected_revenue, Decimal("9059.79"))
        self.assertEqual(self.forecast.expected_walk_ins, 92)

    def test_scenario_override_does_not_mutate_source(self) -> None:
        original_history = tuple(self.history)
        changed = override_scenario(self.scenario, reservations_booked=190, weather="rain")
        forecast_demand(self.history, self.reservations, changed, self.rules)
        self.assertEqual(self.scenario, ForecastScenario(date(2026, 8, 28), 174, "clear", False))
        self.assertEqual(self.history, original_history)

    def test_rejects_invalid_domain_values(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "reservations booked"):
            ForecastScenario(date(2026, 8, 28), -1, "clear", False)
        with self.assertRaisesRegex(RestaurantValidationError, "unsupported weather"):
            ForecastScenario(date(2026, 8, 28), 1, "snow", False)
        with self.assertRaisesRegex(RestaurantValidationError, "historical covers"):
            DemandObservation(date(2026, 1, 1), -1, Decimal("1"), "clear", False)
        with self.assertRaisesRegex(RestaurantValidationError, "historical revenue"):
            DemandObservation(date(2026, 1, 1), 1, Decimal("-1"), "clear", False)

    def test_rejects_malformed_dates_duplicates_and_unresolved_reservations(self) -> None:
        self.assert_bad_history("not-a-date,1,1.00,clear,no\n", "malformed date")
        duplicate = "2026-01-01,1,1.00,clear,no\n2026-01-01,2,2.00,clear,no\n"
        self.assert_bad_history(duplicate, "duplicate daily")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reservations.csv"
            path.write_text("date,booked_covers\n2026-07-27,80\n", encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, "no reservation reference"):
                load_reservations(path, self.history)

    def test_rejects_missing_history(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "requires historical"):
            forecast_demand((), self.reservations, self.scenario, self.rules)
        with self.assertRaisesRegex(RestaurantValidationError, "no historical demand"):
            forecast_demand(self.history, self.reservations,
                ForecastScenario(date(2026, 7, 27), 10, "clear", False), self.rules)

    def test_example_and_two_scenario_comparisons_run(self) -> None:
        default = self.run_example()
        event = self.run_example("--event")
        rain = self.run_example("--weather", "rain", "--reservations", "190")
        self.assertIn("Expected covers:                266", default)
        self.assertIn("Forecast ≠ fact.", default)
        self.assertIn("Difference:       +28 covers", event)
        self.assertIn("Difference:       -9 covers", rain)
        self.assertIn("Source CSV files are unchanged", rain)

    def run_example(self, *arguments: str) -> str:
        return subprocess.run([sys.executable, "examples/demand_forecast.py", *arguments], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout

    def assert_bad_history(self, rows: str, message: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.csv"
            path.write_text("date,total_covers,revenue,weather,local_event\n" + rows, encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, message):
                load_demand_history(path)


if __name__ == "__main__":
    unittest.main()
