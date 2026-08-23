"""Transparent phrase matching and period comparison for guest feedback."""

from __future__ import annotations

import re
from datetime import date, timedelta

from .feedback import ClassifiedReview, FeedbackAnalysis, Review, TopicSignal, TopicSummary, TopicTrend
from .model import RestaurantValidationError


# Each visible phrase both identifies its topic and supplies polarity. Keywords
# identify a mention but remain neutral unless a listed phrase also matches.
TOPIC_RULES = {
    "food_quality": {
        "keywords": ("food", "meal", "crab cake", "rockfish", "burger", "portion"),
        "positive": ("excellent food", "food was excellent", "delicious", "great meal", "great crab cakes", "perfectly cooked", "fresh"),
        "negative": ("cold food", "food was cold", "overcooked", "bland", "small portion", "inconsistent portion"),
    },
    "service": {
        "keywords": ("service", "server", "staff", "host"),
        "positive": ("friendly server", "friendly staff", "warm service", "attentive", "helpful host"),
        "negative": ("rude", "ignored", "inattentive", "confusing service", "slow service"),
    },
    "wait_time": {
        "keywords": ("wait", "waited", "slow", "took forever", "long line"),
        "positive": ("no wait", "right on time", "quickly seated", "wasn't bad"),
        "negative": ("long wait", "waited", "slow", "took forever", "long line", "late seating"),
    },
    "drinks": {
        "keywords": ("cocktail", "drink", "bar"),
        "positive": ("great cocktails", "excellent cocktails", "delicious drink", "creative cocktails"),
        "negative": ("slow drinks", "drinks took", "bar was slow", "watery cocktail"),
    },
    "value": {
        "keywords": ("value", "price", "expensive", "worth"),
        "positive": ("good value", "worth the price", "fair price"),
        "negative": ("overpriced", "too expensive", "not worth"),
    },
    "parking": {
        "keywords": ("parking", "park"),
        "positive": ("easy parking", "parking was easy"),
        "negative": ("difficult parking", "parking was difficult", "hard to park", "couldn't find parking"),
    },
    "online_ordering": {
        "keywords": ("online order", "ordering site", "takeout order", "pickup"),
        "positive": ("easy online order", "online ordering worked well", "smooth pickup", "ready on time"),
        "negative": ("online order was missing", "ordering site failed", "wrong pickup time", "confusing pickup"),
    },
    "cleanliness": {
        "keywords": ("clean", "restroom", "table"),
        "positive": ("very clean", "clean dining room", "spotless"),
        "negative": ("dirty", "sticky table", "messy restroom"),
    },
    "atmosphere": {
        "keywords": ("atmosphere", "dining room", "noise", "noisy", "music"),
        "positive": ("lovely atmosphere", "comfortable dining room", "great atmosphere"),
        "negative": ("too noisy", "loud dining room", "music was loud"),
    },
}


def normalize_text(text: str) -> str:
    """Lowercase, normalize apostrophes, remove punctuation, and collapse space."""
    lowered = text.lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9']+", " ", lowered)).strip()


def _contains(text: str, phrase: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def classify_review(review: Review) -> ClassifiedReview:
    text = normalize_text(review.text)
    signals = []
    for topic, rules in TOPIC_RULES.items():
        keywords = tuple(phrase for phrase in rules["keywords"] if _contains(text, phrase))
        positive = tuple(phrase for phrase in rules["positive"] if _contains(text, phrase))
        negative = tuple(phrase for phrase in rules["negative"] if _contains(text, phrase))
        if not (keywords or positive or negative):
            continue
        sentiment = "mixed" if positive and negative else "positive" if positive else "negative" if negative else "neutral"
        signals.append(TopicSignal(topic, sentiment, tuple(dict.fromkeys((*positive, *negative, *keywords)))))
    return ClassifiedReview(review, tuple(signals))


def aggregate(classified: tuple[ClassifiedReview, ...]) -> tuple[TopicSummary, ...]:
    summaries = []
    for topic in TOPIC_RULES:
        signals = [signal for row in classified for signal in row.signals if signal.topic == topic]
        if signals:
            summaries.append(TopicSummary(
                topic, len(signals),
                sum(signal.sentiment in {"positive", "mixed"} for signal in signals),
                sum(signal.sentiment in {"negative", "mixed"} for signal in signals),
                sum(signal.sentiment in {"neutral", "mixed"} for signal in signals),
            ))
    return tuple(sorted(summaries, key=lambda row: (-row.mentions, row.topic)))


def _summary_for(topic: str, rows: tuple[ClassifiedReview, ...]) -> TopicSummary:
    return next((row for row in aggregate(rows) if row.topic == topic), TopicSummary(topic, 0, 0, 0, 0))


def analyze_feedback(
    reviews: tuple[Review, ...], *, period_days: int = 30, as_of: date | None = None
) -> FeedbackAnalysis:
    """Compare two adjacent windows; 20 percentage points is a directional signal."""
    if isinstance(period_days, bool) or not isinstance(period_days, int) or period_days <= 0:
        raise RestaurantValidationError("analysis period must be a positive integer number of days")
    if not reviews:
        raise RestaurantValidationError("feedback analysis requires reviews")
    end = as_of or max(review.date for review in reviews)
    recent_start = end - timedelta(days=period_days - 1)
    previous_start = recent_start - timedelta(days=period_days)
    included = tuple(classify_review(review) for review in reviews if previous_start <= review.date <= end)
    recent = tuple(row for row in included if row.review.date >= recent_start)
    previous = tuple(row for row in included if row.review.date < recent_start)
    trends = []
    for topic in TOPIC_RULES:
        old, new = _summary_for(topic, previous), _summary_for(topic, recent)
        if not old.mentions and not new.mentions:
            direction = "No evidence"
        elif not old.mentions or not new.mentions:
            direction = "Insufficient comparison"
        else:
            delta = new.negative_share - old.negative_share
            direction = "Worsening" if delta >= .20 else "Improving" if delta <= -.20 else "Stable"
        trends.append(TopicTrend(topic, old, new, direction))
    return FeedbackAnalysis(previous_start, end, included, aggregate(included), tuple(trends), period_days)


def drill_down(analysis: FeedbackAnalysis, topic: str) -> tuple[ClassifiedReview, ...]:
    if topic not in TOPIC_RULES:
        raise RestaurantValidationError(f"unknown feedback topic: {topic}")
    return tuple(
        row for row in sorted(analysis.reviews, key=lambda item: item.review.date, reverse=True)
        if any(signal.topic == topic for signal in row.signals)
    )
