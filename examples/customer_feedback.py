#!/usr/bin/env python3
"""Run James River Kitchen's fictional customer-feedback analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restaurant_lab.feedback_analysis import TOPIC_RULES, analyze_feedback  # noqa: E402
from restaurant_lab.feedback_loader import load_reviews  # noqa: E402
from restaurant_lab.feedback_summary import format_feedback_analysis, format_topic_evidence  # noqa: E402
from restaurant_lab.model import RestaurantValidationError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze fictional James River Kitchen feedback")
    parser.add_argument("--period-days", type=int, default=30, help="days in each of two comparison windows")
    parser.add_argument("--topic", choices=TOPIC_RULES, help="show traceable evidence for one topic")
    args = parser.parse_args()
    try:
        analysis = analyze_feedback(
            load_reviews(ROOT / "data" / "customer_feedback_summer_2026.csv"),
            period_days=args.period_days,
        )
    except RestaurantValidationError as error:
        parser.error(str(error))
    print(format_feedback_analysis(analysis))
    if args.topic:
        print(format_topic_evidence(analysis, args.topic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
