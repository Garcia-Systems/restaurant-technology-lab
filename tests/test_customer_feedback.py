from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab.feedback import Review
from restaurant_lab.feedback_analysis import (
    TOPIC_RULES,
    aggregate,
    analyze_feedback,
    classify_review,
    drill_down,
    normalize_text,
)
from restaurant_lab.feedback_loader import load_reviews
from restaurant_lab.model import RestaurantValidationError


DATA = ROOT / "data" / "customer_feedback_summer_2026.csv"


class CustomerFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reviews = load_reviews(DATA)

    def _csv(self, rows: list[list[str]]) -> Path:
        temporary = tempfile.NamedTemporaryFile("w", newline="", suffix=".csv", delete=False)
        with temporary:
            writer = csv.writer(temporary)
            writer.writerow(["review_id", "date", "rating", "channel", "text"])
            writer.writerows(rows)
        self.addCleanup(Path(temporary.name).unlink)
        return Path(temporary.name)

    def test_loads_fictional_reviews_and_supported_channels(self) -> None:
        self.assertEqual(48, len(self.reviews))
        self.assertEqual("FB-001", self.reviews[0].review_id)
        self.assertEqual(date(2026, 8, 30), self.reviews[-1].date)
        self.assertEqual(4, len({review.channel for review in self.reviews}))

    def test_normalizes_text_without_hiding_words(self) -> None:
        self.assertEqual("the wait wasn't bad great", normalize_text("  The WAIT wasn’t bad—great! "))

    def test_detects_positive_and_negative_topic_phrases(self) -> None:
        positive = classify_review(Review("A", date(2026, 8, 1), 5, "public_review", "Great crab cakes."))
        negative = classify_review(Review("B", date(2026, 8, 1), 2, "public_review", "We waited 40 minutes."))
        self.assertEqual(("food_quality", "positive"), (positive.signals[0].topic, positive.signals[0].sentiment))
        self.assertEqual(("wait_time", "negative"), (negative.signals[0].topic, negative.signals[0].sentiment))

    def test_preserves_multi_topic_and_mixed_written_feedback_despite_rating(self) -> None:
        row = classify_review(Review(
            "A", date(2026, 8, 1), 4, "public_review",
            "Great cocktails, but drinks took too long. The food was excellent.",
        ))
        signals = {signal.topic: signal.sentiment for signal in row.signals}
        self.assertEqual("mixed", signals["drinks"])
        self.assertEqual("positive", signals["food_quality"])

    def test_aggregation_counts_mentions_polarity_shares_and_mixed(self) -> None:
        rows = tuple(classify_review(review) for review in (
            Review("A", date(2026, 8, 1), 5, "public_review", "Great cocktails."),
            Review("B", date(2026, 8, 2), 3, "public_review", "Great cocktails but drinks took too long."),
        ))
        drinks = next(row for row in aggregate(rows) if row.topic == "drinks")
        self.assertEqual((2, 2, 1, 1), (drinks.mentions, drinks.positive, drinks.negative, drinks.neutral_or_mixed))
        self.assertEqual(.5, drinks.negative_share)

    def test_average_rating_and_trends_derive_from_adjacent_windows(self) -> None:
        analysis = analyze_feedback(self.reviews, period_days=30)
        self.assertAlmostEqual(sum(review.rating for review in self.reviews) / 48, analysis.average_rating)
        trends = {trend.topic: trend for trend in analysis.trends}
        self.assertEqual("Worsening", trends["wait_time"].direction)
        self.assertEqual("Improving", trends["online_ordering"].direction)
        self.assertGreater(trends["wait_time"].recent.negative_share, trends["wait_time"].previous.negative_share)

    def test_analysis_window_filters_without_mutating_source(self) -> None:
        before = self.reviews
        short = analyze_feedback(self.reviews, period_days=7)
        self.assertTrue(all(date(2026, 8, 17) <= row.review.date <= date(2026, 8, 30) for row in short.reviews))
        self.assertEqual(before, self.reviews)
        self.assertIs(before, self.reviews)

    def test_topic_drill_down_is_reverse_chronological_and_traceable(self) -> None:
        analysis = analyze_feedback(self.reviews)
        rows = drill_down(analysis, "wait_time")
        self.assertGreater(len(rows), 5)
        self.assertEqual(sorted((row.review.date for row in rows), reverse=True), [row.review.date for row in rows])
        self.assertTrue(all(any(signal.topic == "wait_time" for signal in row.signals) for row in rows))

    def test_empty_result_period_is_explicit_and_safe(self) -> None:
        analysis = analyze_feedback(self.reviews, period_days=7, as_of=date(2027, 1, 31))
        self.assertEqual((), analysis.reviews)
        self.assertEqual(0.0, analysis.average_rating)
        self.assertTrue(all(trend.direction == "No evidence" for trend in analysis.trends))

    def test_rejects_invalid_domain_values_and_periods(self) -> None:
        with self.assertRaises(RestaurantValidationError):
            Review("A", date.today(), 0, "public_review", "Text")
        with self.assertRaises(RestaurantValidationError):
            Review("A", date.today(), 4, "email", "Text")
        with self.assertRaises(RestaurantValidationError):
            Review("A", date.today(), 4, "public_review", " ")
        for value in (0, -2, True):
            with self.subTest(value=value), self.assertRaises(RestaurantValidationError):
                analyze_feedback(self.reviews, period_days=value)

    def test_loader_rejects_malformed_dates_ratings_and_duplicate_ids(self) -> None:
        bad_rows = (
            [["A", "08/01/2026", "4", "public_review", "Text"]],
            [["A", "2026-08-01", "six", "public_review", "Text"]],
            [["A", "2026-08-01", "6", "public_review", "Text"]],
            [["A", "2026-08-01", "4", "public_review", "Text"], ["A", "2026-08-02", "4", "public_review", "More"]],
        )
        for rows in bad_rows:
            with self.subTest(rows=rows), self.assertRaises(RestaurantValidationError):
                load_reviews(self._csv(rows))

    def test_topic_taxonomy_is_small_explicit_and_cli_runs(self) -> None:
        self.assertEqual(9, len(TOPIC_RULES))
        result = subprocess.run(
            [sys.executable, "examples/customer_feedback.py", "--topic", "wait_time", "--period-days", "14"],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        self.assertIn("WAIT TIME — FICTIONAL EVIDENCE", result.stdout)
        self.assertIn("Matched:", result.stdout)


if __name__ == "__main__":
    unittest.main()
