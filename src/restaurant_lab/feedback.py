"""Domain contracts for the explainable customer-feedback chapter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .model import RestaurantValidationError


FEEDBACK_CHANNELS = frozenset(
    {"public_review", "reservation_survey", "website_feedback", "takeout_survey"}
)
SENTIMENTS = frozenset({"positive", "negative", "neutral", "mixed"})


@dataclass(frozen=True)
class Review:
    review_id: str
    date: date
    rating: int
    channel: str
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.review_id, str) or not self.review_id.strip():
            raise RestaurantValidationError("review ID must be a non-empty string")
        if isinstance(self.rating, bool) or not isinstance(self.rating, int) or not 1 <= self.rating <= 5:
            raise RestaurantValidationError(f"rating for {self.review_id} must be an integer from 1 to 5")
        if self.channel not in FEEDBACK_CHANNELS:
            raise RestaurantValidationError(
                f"unsupported feedback channel for {self.review_id}: {self.channel!r}"
            )
        if not isinstance(self.text, str) or not self.text.strip():
            raise RestaurantValidationError(f"review text for {self.review_id} cannot be empty")


@dataclass(frozen=True)
class TopicSignal:
    topic: str
    sentiment: str
    matched_phrases: tuple[str, ...]


@dataclass(frozen=True)
class ClassifiedReview:
    review: Review
    signals: tuple[TopicSignal, ...]


@dataclass(frozen=True)
class TopicSummary:
    topic: str
    mentions: int
    positive: int
    negative: int
    neutral_or_mixed: int

    @property
    def positive_share(self) -> float:
        return self.positive / self.mentions if self.mentions else 0.0

    @property
    def negative_share(self) -> float:
        return self.negative / self.mentions if self.mentions else 0.0


@dataclass(frozen=True)
class TopicTrend:
    topic: str
    previous: TopicSummary
    recent: TopicSummary
    direction: str


@dataclass(frozen=True)
class FeedbackAnalysis:
    period_start: date
    period_end: date
    reviews: tuple[ClassifiedReview, ...]
    topics: tuple[TopicSummary, ...]
    trends: tuple[TopicTrend, ...]
    period_days: int

    @property
    def average_rating(self) -> float:
        return sum(row.review.rating for row in self.reviews) / len(self.reviews) if self.reviews else 0.0

    @property
    def five_star_count(self) -> int:
        return sum(row.review.rating == 5 for row in self.reviews)

    @property
    def low_rating_count(self) -> int:
        return sum(row.review.rating <= 2 for row in self.reviews)
