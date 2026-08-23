"""Presentation-ready customer-feedback reporting."""

from __future__ import annotations

from .feedback import FeedbackAnalysis
from .feedback_analysis import drill_down


def _label(topic: str) -> str:
    return topic.replace("_", " ").title()


def format_feedback_analysis(analysis: FeedbackAnalysis) -> str:
    lines = [
        "James River Kitchen",
        "Customer Feedback",
        "Fictional feedback — deterministic phrase matching, not AI",
        "",
        f"Period: {analysis.period_start:%B %d}–{analysis.period_end:%B %d, %Y}",
        f"Two adjacent {analysis.period_days}-day windows",
        "",
        "OVERALL",
        "-" * 64,
        f"Reviews analyzed: {len(analysis.reviews):>10}",
        f"Average rating:  {analysis.average_rating:>10.1f}",
        f"5-star reviews:  {analysis.five_star_count:>10}",
        f"1–2 star reviews:{analysis.low_rating_count:>10}",
        "",
        "MOST DISCUSSED TOPICS",
        "-" * 64,
        f"{'Topic':18} {'Mentions':>8} {'Positive':>9} {'Negative':>9} {'Other':>7}",
    ]
    lines.extend(
        f"{_label(row.topic):18} {row.mentions:8d} {row.positive:9d} {row.negative:9d} {row.neutral_or_mixed:7d}"
        for row in analysis.topics
    )
    lines.extend(["", "TREND SIGNALS", "-" * 64])
    for trend in analysis.trends:
        if trend.previous.mentions and trend.recent.mentions:
            detail = f"negative share {trend.previous.negative_share:.0%} → {trend.recent.negative_share:.0%}"
        else:
            detail = "not enough mentions in both windows"
        lines.append(f"{_label(trend.topic):18} {trend.direction:23} ({detail})")

    positive = max(analysis.topics, key=lambda row: (row.positive, row.mentions), default=None)
    worsening = [trend for trend in analysis.trends if trend.direction == "Worsening"]
    improving = [trend for trend in analysis.trends if trend.direction == "Improving"]
    lines.extend(["", "BUSINESS OBSERVATIONS", "-" * 64])
    if positive:
        lines.append(f"- {_label(positive.topic)} is the strongest positive theme ({positive.positive} positive mentions).")
    lines.extend(
        f"- {_label(trend.topic)} complaints increased in the recent window; investigate the experience."
        for trend in worsening
    )
    lines.extend(
        f"- {_label(trend.topic)} complaints declined in the recent window."
        for trend in improving
    )
    lines.extend([
        "- Ratings are context; written topic signals retain mixed experiences.",
        "- A customer symptom identifies where to investigate, not its operational cause.",
        "",
        "RULES",
        "- Topic phrases are listed in src/restaurant_lab/feedback_analysis.py.",
        "- A topic is worsening/improving when negative share moves by at least 20 percentage points.",
        "- Mixed signals count in positive, negative, and Other; neutral signals count only in Other.",
        "- No statistical significance or root cause is claimed.",
    ])
    return "\n".join(lines)


def format_topic_evidence(analysis: FeedbackAnalysis, topic: str) -> str:
    rows = drill_down(analysis, topic)
    lines = ["", f"{_label(topic).upper()} — FICTIONAL EVIDENCE", "-" * 64]
    if not rows:
        lines.append("No matching feedback in this analysis period.")
    for row in rows:
        signal = next(signal for signal in row.signals if signal.topic == topic)
        lines.extend([
            f"{row.review.date.isoformat()} — {row.review.rating} stars — {row.review.channel} — {signal.sentiment}",
            f'“{row.review.text}”',
            f"Matched: {', '.join(signal.matched_phrases)}",
            "",
        ])
    return "\n".join(lines).rstrip()
