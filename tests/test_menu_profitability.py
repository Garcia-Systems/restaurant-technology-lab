from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import (  # noqa: E402
    MenuItem, RestaurantValidationError, SalesRecord, analyze_menu,
    load_menu, load_sales, rank_by_contribution, simulate_price,
)

MENU = ROOT / "data" / "menu.csv"
SALES = ROOT / "data" / "menu_sales_july_2026.csv"


class MenuProfitabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.menu = load_menu(MENU)
        self.sales = load_sales(SALES, self.menu)
        self.analysis = analyze_menu(self.menu, self.sales)

    def test_loads_complete_menu_with_decimal_money(self) -> None:
        self.assertEqual(len(self.menu), 20)
        burger = next(item for item in self.menu if item.item_id == "river-burger")
        self.assertEqual(burger.selling_price, Decimal("16.00"))
        self.assertEqual(burger.ingredient_cost, Decimal("7.00"))

    def test_loads_aggregated_sales_and_period(self) -> None:
        self.assertEqual(len(self.sales), 20)
        self.assertEqual({record.period for record in self.sales}, {"July 2026"})
        self.assertEqual(next(row.units_sold for row in self.sales if row.item_id == "river-burger"), 610)

    def test_calculates_item_money_and_margin_exactly(self) -> None:
        burger = next(row for row in self.analysis.items if row.item.item_id == "river-burger")
        self.assertEqual(burger.revenue, Decimal("9760.00"))
        self.assertEqual(burger.estimated_food_cost, Decimal("4270.00"))
        self.assertEqual(burger.contribution_per_sale, Decimal("9.00"))
        self.assertEqual(burger.total_contribution, Decimal("5490.00"))
        self.assertEqual(burger.contribution_margin, Decimal("0.5625"))

    def test_aggregates_and_ranks_by_total_contribution(self) -> None:
        self.assertEqual(self.analysis.total_revenue, Decimal("97715.00"))
        self.assertEqual(self.analysis.total_food_cost, Decimal("32120.00"))
        self.assertEqual(self.analysis.total_contribution, Decimal("65595.00"))
        self.assertEqual(rank_by_contribution(self.analysis)[0].item.item_id, "crab-cake-dinner")

    def test_classification_uses_exposed_mean_thresholds(self) -> None:
        burger = next(row for row in self.analysis.items if row.item.item_id == "river-burger")
        tenderloin = next(row for row in self.analysis.items if row.item.item_id == "beef-tenderloin")
        self.assertEqual(self.analysis.popularity_threshold, Decimal("300.75"))
        self.assertEqual(self.analysis.contribution_threshold, Decimal("11.2975"))
        self.assertEqual(burger.classification, "High popularity + low contribution")
        self.assertEqual(tenderloin.classification, "Low popularity + high contribution")

    def test_zero_units_and_safe_zero_revenue_summary(self) -> None:
        item = MenuItem("test", "Test", "Test", Decimal("10.00"), Decimal("3.00"))
        result = analyze_menu((item,), (SalesRecord("Test", "test", 0),))
        self.assertEqual(result.total_revenue, Decimal("0.00"))
        self.assertEqual(result.food_cost_percentage, Decimal("0"))

    def test_scenario_changes_copy_not_original(self) -> None:
        original = next(item for item in self.menu if item.item_id == "river-burger")
        simulated = simulate_price(self.menu, "river-burger", Decimal("17.50"))
        changed = next(item for item in simulated if item.item_id == "river-burger")
        self.assertEqual(original.selling_price, Decimal("16.00"))
        self.assertEqual(changed.selling_price, Decimal("17.50"))
        self.assertIsNot(original, changed)

    def test_rejects_invalid_business_values(self) -> None:
        invalid = [
            (Decimal("0"), Decimal("0"), "selling price"),
            (Decimal("10"), Decimal("-1"), "cannot be negative"),
            (Decimal("10"), Decimal("10"), "must be less"),
        ]
        for price, cost, message in invalid:
            with self.subTest(message=message), self.assertRaisesRegex(RestaurantValidationError, message):
                MenuItem("bad", "Bad", "Test", price, cost)
        with self.assertRaisesRegex(RestaurantValidationError, "non-negative integer"):
            SalesRecord("July", "bad", -1)

    def test_rejects_unknown_sales_item_duplicate_ids_and_bad_money(self) -> None:
        self.assert_bad_sales("July 2026,not-on-menu,1\n", "unknown menu item")
        duplicate_menu = (
            "item_id,item_name,category,selling_price,ingredient_cost\n"
            "same,One,Test,10.00,2.00\n"
            "same,Two,Test,11.00,3.00\n"
        )
        self.assert_bad_menu(duplicate_menu, "duplicate menu item")
        bad_money = (
            "item_id,item_name,category,selling_price,ingredient_cost\n"
            "bad,Bad,Test,ten,2.00\n"
        )
        self.assert_bad_menu(bad_money, "malformed selling price")

    def test_scenario_rejects_unknown_item_and_invalid_price(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "unknown menu item"):
            simulate_price(self.menu, "missing", Decimal("12.00"))
        with self.assertRaisesRegex(RestaurantValidationError, "must be less"):
            simulate_price(self.menu, "river-burger", Decimal("6.00"))

    def test_example_and_scenario_are_presentation_ready(self) -> None:
        baseline = subprocess.run([sys.executable, "examples/menu_profitability.py"], cwd=ROOT,
                                  check=True, capture_output=True, text=True)
        scenario = subprocess.run([sys.executable, "examples/menu_profitability.py", "--item",
                                   "river-burger", "--price", "17.50"], cwd=ROOT,
                                  check=True, capture_output=True, text=True)
        self.assertIn("Best seller by units: River Burger", baseline.stdout)
        self.assertIn("Highest total contribution item: Crab Cake Dinner", baseline.stdout)
        self.assertIn("SIMULATION — source CSV files are unchanged", scenario.stdout)
        self.assertIn("Simulated total contribution change: $915.00", scenario.stdout)

    def assert_bad_menu(self, contents: str, message: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "menu.csv"
            path.write_text(contents, encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, message):
                load_menu(path)

    def assert_bad_sales(self, row: str, message: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sales.csv"
            path.write_text("period,item_id,units_sold\n" + row, encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, message):
                load_sales(path, self.menu)


if __name__ == "__main__":
    unittest.main()
