"""Presentation-friendly views of the restaurant model."""

from .model import Restaurant


def format_operational_summary(restaurant: Restaurant) -> str:
    """Turn validated restaurant data into a concise business briefing."""
    services = list(dict.fromkeys(period.service for period in restaurant.operating_periods))
    lines = [
        restaurant.name,
        f"{restaurant.location} | Fictional demonstration data",
        f"Concept: {restaurant.concept}",
        "",
        f"Capacity: {restaurant.capacity} guests",
        f"Service: {', '.join(services)}",
        "Operating periods:",
    ]
    lines.extend(
        f"- {', '.join(period.days)}: {period.service}, {period.opens}-{period.closes}"
        for period in restaurant.operating_periods
    )
    lines.extend(["", "Menu categories:"])
    lines.extend(f"- {category}" for category in restaurant.menu_categories)
    lines.extend(["", "Sales channels:"])
    lines.extend(f"- {channel}" for channel in restaurant.sales_channels)
    lines.extend(["", "Operational data sources:"])
    lines.extend(f"- {source.name}: {source.provides}" for source in restaurant.data_sources)
    lines.extend(
        [
            "",
            "How the restaurant operates:",
            "Guest -> Reservation or Order -> Kitchen / Service -> Inventory -> Labor -> Payment / POS -> Business results",
            "",
            "How connected data creates decisions:",
            "POS + Reservations + Scheduling + Inventory + Reviews",
            "  -> Import / adapters",
            "  -> Normalized restaurant data",
            "  -> Analytics / business rules",
            "  -> Recommendations / alerts",
            "",
            "Business takeaway: keep the systems already in use; connect their evidence to answer cross-system questions.",
        ]
    )
    return "\n".join(lines)
