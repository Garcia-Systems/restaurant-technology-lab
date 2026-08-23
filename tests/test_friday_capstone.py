from __future__ import annotations

from datetime import date
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (ForecastScenario, RestaurantValidationError, analyze_menu,  # noqa: E402
    build_capstone, format_capstone, load_menu, load_sales)


class FridayCapstoneTests(unittest.TestCase):
    def scenario(self, reservations=174, weather="clear", event=False):
        return ForecastScenario(date(2026, 8, 28), reservations, weather, event)

    def test_default_composes_all_five_chapter_results(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario())
        self.assertEqual(result.menu.total_contribution, analyze_menu(
            load_menu(ROOT / "data/menu.csv"),
            load_sales(ROOT / "data/menu_sales_july_2026.csv", load_menu(ROOT / "data/menu.csv")),
        ).total_contribution)
        self.assertEqual(result.demand.expected_covers, 266)
        self.assertEqual(result.labor.forecast, result.demand)
        self.assertEqual(result.inventory.forecast, result.demand)
        self.assertEqual(result.feedback.period_end, date(2026, 8, 28))

    def test_default_cross_signals_priorities_and_evidence(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario())
        by_title = {row.title: row for row in result.signals}
        self.assertEqual(by_title["Review server coverage"].priority, "HIGH PRIORITY")
        self.assertEqual(by_title["Verify near-threshold inventory"].priority, "WATCH")
        self.assertEqual(by_title["Review ground beef prep"].priority, "WATCH")
        self.assertIn("Investigate guest-experience capacity", by_title)
        self.assertIn("do not establish", by_title["Investigate guest-experience capacity"].interpretation)
        self.assertTrue(all(signal.evidence for signal in result.signals))

    def test_menu_opportunity_uses_profitability_and_inventory_coverage(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario())
        self.assertEqual(result.opportunity.item.item_id, "beef-tenderloin")
        self.assertEqual(result.opportunity.classification, "Low popularity + high contribution")
        self.assertIn("comfortable recipe-ingredient coverage",
                      next(s.interpretation for s in result.signals if s.priority == "OPPORTUNITY"))

    def test_high_demand_propagates_to_labor_inventory_and_experience(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario(210, "clear", True))
        self.assertEqual(result.demand.expected_covers, 326)
        self.assertEqual(next(row for row in result.labor.roles if row.role == "server").status, "Below")
        self.assertEqual(sum(row.status == "Potential shortage" for row in result.inventory.coverage), 14)
        self.assertIn("Investigate guest-experience capacity", {row.title for row in result.signals})
        self.assertIsNone(result.opportunity)

    def test_lower_demand_changes_downstream_signals(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario(120, "storms"))
        self.assertEqual(result.demand.expected_covers, 175)
        self.assertEqual(next(row for row in result.labor.roles if row.role == "server").status, "Aligned")
        self.assertTrue(any(row.status == "Above" for row in result.labor.roles))
        self.assertFalse(any(row.status == "Potential shortage" for row in result.inventory.coverage))
        self.assertNotIn("Investigate guest-experience capacity", {row.title for row in result.signals})

    def test_scenario_override_does_not_mutate_loaded_source_or_default(self) -> None:
        scenario = self.scenario()
        source = (ROOT / "data/reservations_august_2026.csv").read_bytes()
        build_capstone(ROOT / "data", self.scenario(210, "clear", True))
        self.assertEqual(scenario, self.scenario())
        self.assertEqual((ROOT / "data/reservations_august_2026.csv").read_bytes(), source)
        self.assertEqual(build_capstone(ROOT / "data", scenario).demand.expected_covers, 266)

    def test_output_is_deterministic_and_explain_traces_every_signal(self) -> None:
        result = build_capstone(ROOT / "data", self.scenario())
        first = format_capstone(result, explain=True)
        self.assertEqual(first, format_capstone(build_capstone(ROOT / "data", self.scenario()), explain=True))
        self.assertEqual(first.count("Interpretation:"), len(result.signals))
        self.assertEqual(first.count("Evidence:"), len(result.signals))
        self.assertIn("Scheduled servers: 7; planning range: 8–10", first)

    def test_invalid_and_missing_scenario_inputs_fail_clearly(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "non-negative"):
            self.scenario(-1)
        missing = subprocess.run([sys.executable, "examples/friday_night_capstone.py", "--reservations"],
                                 cwd=ROOT, capture_output=True, text=True)
        invalid = subprocess.run([sys.executable, "examples/friday_night_capstone.py", "--weather", "snow"],
                                 cwd=ROOT, capture_output=True, text=True)
        self.assertEqual((missing.returncode, invalid.returncode), (2, 2))
        self.assertIn("expected one argument", missing.stderr)
        self.assertIn("invalid choice", invalid.stderr)

    def test_cli_default_high_low_and_explain(self) -> None:
        default = self.run_cli()
        high = self.run_cli("--reservations", "210", "--event")
        low = self.run_cli("--reservations", "120", "--weather", "storms")
        explain = self.run_cli("--explain")
        self.assertIn("Expected covers:     266", default)
        self.assertIn("Potential shortages: 14", high)
        self.assertIn("Server coverage: ALIGNED", low)
        self.assertIn("bartender above", low)
        self.assertIn("EVIDENCE TRACE", explain)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "examples/friday_night_capstone.py", *args], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout


if __name__ == "__main__":
    unittest.main()
