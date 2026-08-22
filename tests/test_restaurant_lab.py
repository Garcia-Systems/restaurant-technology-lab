from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab import RestaurantValidationError, format_operational_summary, load_restaurant  # noqa: E402


CONFIG = ROOT / "data" / "james_river_kitchen.json"


class RestaurantFoundationTests(unittest.TestCase):
    def test_loads_james_river_kitchen(self) -> None:
        restaurant = load_restaurant(CONFIG)

        self.assertEqual(restaurant.name, "James River Kitchen")
        self.assertEqual(restaurant.capacity, 120)
        self.assertTrue(restaurant.fictional)
        self.assertIn("Dine-in", restaurant.sales_channels)

    def test_has_every_required_operational_system(self) -> None:
        restaurant = load_restaurant(CONFIG)

        self.assertEqual(
            {source.identifier for source in restaurant.data_sources},
            {"pos", "reservations", "scheduling", "inventory", "reviews"},
        )

    def test_summary_is_business_oriented_and_stable(self) -> None:
        summary = format_operational_summary(load_restaurant(CONFIG))

        self.assertTrue(summary.startswith("James River Kitchen\n"))
        self.assertIn("Capacity: 120 guests", summary)
        self.assertIn("POS + Reservations + Scheduling + Inventory + Reviews", summary)
        self.assertIn("Business takeaway:", summary)
        self.assertNotIn("Restaurant(", summary)

    def test_rejects_non_positive_capacity(self) -> None:
        self.assert_invalid_config({"capacity": 0}, "capacity must be a positive integer")

    def test_rejects_invalid_operating_period(self) -> None:
        document = self.base_document()
        document["operating_periods"][0]["closes"] = "15:00"
        self.assert_document_invalid(document, "must close after it opens")

    def test_rejects_missing_required_system(self) -> None:
        document = self.base_document()
        document["data_sources"] = [source for source in document["data_sources"] if source["id"] != "reviews"]
        self.assert_document_invalid(document, r"missing required operational data source\(s\): reviews")

    def test_rejects_duplicate_source_identifier(self) -> None:
        document = self.base_document()
        document["data_sources"].append(dict(document["data_sources"][0]))
        self.assert_document_invalid(document, r"duplicate data source id\(s\): pos")

    def test_example_runs_from_repository_root(self) -> None:
        result = subprocess.run(
            [sys.executable, "examples/restaurant_system.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("James River Kitchen", result.stdout)
        self.assertIn("Fictional demonstration data", result.stdout)

    def base_document(self) -> dict:
        return json.loads(CONFIG.read_text(encoding="utf-8"))

    def assert_invalid_config(self, changes: dict, message: str):
        document = self.base_document()
        document.update(changes)
        self.assert_document_invalid(document, message)

    def assert_document_invalid(self, document: dict, message: str):
        temporary = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        try:
            json.dump(document, temporary)
            temporary.close()
            with self.assertRaisesRegex(RestaurantValidationError, message):
                load_restaurant(temporary.name)
        finally:
            Path(temporary.name).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
