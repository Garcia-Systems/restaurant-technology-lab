from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab.demo_check import CHECKS, check_demo  # noqa: E402
from restaurant_lab.workshop import SECTIONS, run_workshop  # noqa: E402


class WorkshopTests(unittest.TestCase):
    def test_sections_execute_in_story_order_and_reuse_examples(self) -> None:
        calls = []

        def record(command, cwd):
            calls.append((tuple(command), cwd))

        run_workshop(ROOT, pause=False, command_runner=record)
        self.assertEqual([Path(call[0][1]).name for call in calls],
                         [section.script for section in SECTIONS])
        self.assertTrue(all(call[1] == ROOT for call in calls))

    def test_scenario_options_propagate_only_to_aware_sections(self) -> None:
        calls = []
        run_workshop(ROOT, pause=False, reservations=210, weather="clear", event=True,
                     command_runner=lambda command, cwd: calls.append(tuple(command)))
        for section, command in zip(SECTIONS, calls):
            if section.scenario_aware:
                self.assertIn("--reservations", command)
                self.assertIn("--weather", command)
                self.assertIn("--event", command)
            else:
                self.assertNotIn("--reservations", command)

    def test_orchestration_does_not_mutate_data(self) -> None:
        before = {path: path.read_bytes() for path in (ROOT / "data").iterdir() if path.is_file()}
        run_workshop(ROOT, pause=False, command_runner=lambda command, cwd: None)
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_noninteractive_cli_completes_all_sections(self) -> None:
        result = subprocess.run([sys.executable, "examples/workshop.py", "--no-pause"], cwd=ROOT,
                                check=True, capture_output=True, text=True)
        positions = [result.stdout.index(f"JAMES RIVER KITCHEN\n{section.title}\n{'=' * 60}")
                     for section in SECTIONS]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("DISCOVERY DISCUSSION", result.stdout)

    def test_demo_check_succeeds_and_reports_every_component(self) -> None:
        healthy, results = check_demo(ROOT / "data")
        self.assertTrue(healthy)
        self.assertEqual([name for name, _ in results], list(CHECKS))
        self.assertTrue(all(error is None for _, error in results))

    def test_demo_check_fails_clearly_for_missing_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            healthy, results = check_demo(Path(directory))
        self.assertFalse(healthy)
        self.assertEqual(results[0][0], "Restaurant configuration")
        self.assertIsNotNone(results[0][1])


if __name__ == "__main__":
    unittest.main()
