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

from restaurant_lab import (ForecastScenario, Ingredient, InventoryCount, RecipeComponent,  # noqa: E402
    RestaurantValidationError, WasteEvent, analyze_inventory, calculate_menu_mix,
    expected_ingredient_demand, forecast_demand, historical_ingredient_usage,
    load_demand_history, load_forecast_rules, load_ingredients, load_inventory, load_menu,
    load_recipes, load_reservations, load_sales, load_waste, override_scenario,
    simulate_ingredient_cost, validate_recipe_costs)


class InventoryWasteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.menu = load_menu(ROOT / "data/menu.csv")
        self.sales = load_sales(ROOT / "data/menu_sales_july_2026.csv", self.menu)
        self.ingredients = load_ingredients(ROOT / "data/ingredients.csv")
        self.recipes = load_recipes(ROOT / "data/recipes.csv", self.menu, self.ingredients)
        self.inventory = load_inventory(ROOT / "data/inventory_on_hand_2026-08-28.csv", self.ingredients)
        self.waste = load_waste(ROOT / "data/waste_august_2026.csv", self.ingredients)
        history = load_demand_history(ROOT / "data/demand_history_summer_2026.csv")
        reservations = load_reservations(ROOT / "data/reservations_august_2026.csv", history)
        rules = load_forecast_rules(ROOT / "data/demand_forecast_rules.json")
        self.scenario = ForecastScenario(date(2026, 8, 28), 174, "clear", False)
        self.forecast = forecast_demand(history, reservations, self.scenario, rules)
        self.forecast_inputs = history, reservations, rules
        self.analysis = analyze_inventory(self.forecast, self.ingredients, self.recipes,
                                          self.inventory, self.waste, self.sales)

    def test_loads_catalog_recipes_inventory_and_waste(self) -> None:
        self.assertEqual(len(self.ingredients), 20)
        self.assertEqual(len(self.recipes), 20)
        self.assertEqual(len(self.inventory), 20)
        self.assertEqual(len(self.waste), 10)
        self.assertEqual(next(row.unit_cost for row in self.ingredients if row.ingredient_id == "ground-beef"), Decimal("14.0"))

    def test_recipe_costs_are_compatible_with_chapter_two(self) -> None:
        validate_recipe_costs(self.menu, self.ingredients, self.recipes)
        burger = next(row for row in self.recipes if row.menu_item_id == "river-burger")
        self.assertEqual(burger.quantity * Decimal("14.0"), Decimal("7.00"))

    def test_usage_is_derived_from_pos_sales_and_recipe_quantities(self) -> None:
        usage = historical_ingredient_usage(self.sales, self.recipes)
        self.assertEqual(usage["ground-beef"], Decimal("305.0"))
        self.assertEqual(usage["crab-cake-portion"], Decimal("420"))

    def test_menu_mix_and_expected_demand_are_derived(self) -> None:
        mix = calculate_menu_mix(self.sales)
        self.assertEqual(sum(mix.values()), Decimal("1"))
        expected = expected_ingredient_demand(self.forecast, mix, self.recipes)
        self.assertEqual(expected["ground-beef"], Decimal(266) * Decimal(610) / Decimal(6015) * Decimal(".5"))

    def test_inventory_value_waste_cost_and_buffer(self) -> None:
        beef = next(row for row in self.analysis.coverage if row.ingredient.ingredient_id == "ground-beef")
        self.assertEqual(beef.inventory_value, Decimal("245.420"))
        self.assertEqual(beef.waste_cost, Decimal("77.00"))
        self.assertEqual(beef.planning_need, beef.expected_usage * Decimal("1.10"))
        self.assertEqual(self.analysis.total_waste_cost, Decimal("240.10"))

    def test_coverage_statuses_change_with_real_chapter_three_forecast(self) -> None:
        history, reservations, rules = self.forecast_inputs
        high_forecast = forecast_demand(history, reservations,
            override_scenario(self.scenario, reservations_booked=210, local_event=True), rules)
        high = analyze_inventory(high_forecast, self.ingredients, self.recipes, self.inventory, self.waste, self.sales)
        low_forecast = forecast_demand(history, reservations,
            override_scenario(self.scenario, reservations_booked=100, weather="rain"), rules)
        low = analyze_inventory(low_forecast, self.ingredients, self.recipes, self.inventory, self.waste, self.sales)
        shortages = lambda result: sum(row.status == "Potential shortage" for row in result.coverage)
        self.assertEqual((low.forecast.expected_covers, self.forecast.expected_covers, high.forecast.expected_covers), (176, 266, 326))
        self.assertLessEqual(shortages(low), shortages(self.analysis))
        self.assertLess(shortages(self.analysis), shortages(high))

    def test_cost_scenario_is_non_mutating_and_changes_only_financial_effect(self) -> None:
        original = self.ingredients
        changed = simulate_ingredient_cost(original, "rockfish-fillet", Decimal("12.00"))
        simulated = analyze_inventory(self.forecast, changed, self.recipes, self.inventory, self.waste, self.sales)
        old = next(row for row in self.analysis.coverage if row.ingredient.ingredient_id == "rockfish-fillet")
        new = next(row for row in simulated.coverage if row.ingredient.ingredient_id == "rockfish-fillet")
        self.assertEqual(old.waste_quantity, new.waste_quantity)
        self.assertEqual((old.waste_cost, new.waste_cost), (Decimal("49.00"), Decimal("60.00")))
        self.assertEqual(next(row.unit_cost for row in original if row.ingredient_id == "rockfish-fillet"), Decimal("9.80"))

    def test_domain_rejects_negative_cost_quantities_units_and_reasons(self) -> None:
        with self.assertRaisesRegex(RestaurantValidationError, "unit cost"):
            Ingredient("x", "X", "each", Decimal("-1"))
        with self.assertRaisesRegex(RestaurantValidationError, "unsupported ingredient unit"):
            Ingredient("x", "X", "kilogram", Decimal("1"))
        with self.assertRaisesRegex(RestaurantValidationError, "recipe quantity"):
            RecipeComponent("x", "y", Decimal("0"))
        with self.assertRaisesRegex(RestaurantValidationError, "inventory quantity"):
            InventoryCount("x", Decimal("-1"), date.today())
        with self.assertRaisesRegex(RestaurantValidationError, "unsupported waste reason"):
            WasteEvent(date.today(), "x", Decimal("1"), "mystery")

    def test_loaders_reject_unknown_references_duplicates_and_malformed_waste(self) -> None:
        self.bad_csv("menu_item_id,ingredient_id,quantity\nmissing,ground-beef,1\n", "recipe", "unknown menu item")
        self.bad_csv("menu_item_id,ingredient_id,quantity\nriver-burger,missing,1\n", "recipe", "unknown ingredient")
        ingredient = "ingredient_id,name,unit,unit_cost\nx,X,each,1\nx,Y,each,2\n"
        self.bad_csv(ingredient, "ingredient", "duplicate ingredient")
        waste = "date,ingredient_id,quantity,reason\nnot-date,ground-beef,1,spoilage\n"
        self.bad_csv(waste, "waste", "malformed")

    def test_examples_default_low_high_and_cost_scenarios(self) -> None:
        default = self.run_example()
        low = self.run_example("--weather", "rain", "--reservations", "100")
        high = self.run_example("--event", "--reservations", "210")
        cost = self.run_example("--ingredient-cost", "rockfish-fillet=12.00")
        self.assertIn("Forecast covers: 266", default)
        self.assertIn("Total recorded waste cost: $240.10", default)
        self.assertIn("Changed demand: 176 covers", low)
        self.assertIn("Changed demand: 326 covers; potential shortages: 14", high)
        self.assertIn("Recorded waste quantity unchanged: 5 each", cost)

    def run_example(self, *args: str) -> str:
        return subprocess.run([sys.executable, "examples/inventory_waste.py", *args], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout

    def bad_csv(self, contents: str, kind: str, message: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"; path.write_text(contents, encoding="utf-8")
            with self.assertRaisesRegex(RestaurantValidationError, message):
                if kind == "ingredient": load_ingredients(path)
                elif kind == "recipe": load_recipes(path, self.menu, self.ingredients)
                else: load_waste(path, self.ingredients)


if __name__ == "__main__":
    unittest.main()
