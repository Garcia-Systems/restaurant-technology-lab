"""CSV boundary for fictional guest feedback."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .feedback import Review
from .model import RestaurantValidationError


def load_reviews(path: str | Path) -> tuple[Review, ...]:
    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            expected = {"review_id", "date", "rating", "channel", "text"}
            if reader.fieldnames is None or set(reader.fieldnames) != expected:
                raise RestaurantValidationError(
                    f"{source.name} columns must be: {', '.join(sorted(expected))}"
                )
            reviews = []
            for row_number, row in enumerate(reader, start=2):
                try:
                    review_date = date.fromisoformat(row["date"])
                except (TypeError, ValueError) as error:
                    raise RestaurantValidationError(
                        f"malformed review date on CSV row {row_number}: {row['date']!r}"
                    ) from error
                try:
                    rating = int(row["rating"])
                except (TypeError, ValueError) as error:
                    raise RestaurantValidationError(
                        f"rating on CSV row {row_number} must be an integer from 1 to 5"
                    ) from error
                reviews.append(Review(row["review_id"], review_date, rating, row["channel"], row["text"]))
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"data file not found: {source}") from error

    identifiers = [review.review_id for review in reviews]
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        raise RestaurantValidationError(f"duplicate review ID(s): {', '.join(duplicates)}")
    if not reviews:
        raise RestaurantValidationError("feedback data cannot be empty")
    return tuple(reviews)
