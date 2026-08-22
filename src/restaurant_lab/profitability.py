"""Explainable menu-profitability calculations and scenario behavior."""

from __future__ import annotations

from decimal import Decimal

from .menu import ItemProfitability, MenuAnalysis, MenuItem, SalesRecord
from .model import RestaurantValidationError


def analyze_menu(menu: tuple[MenuItem, ...], sales: tuple[SalesRecord, ...]) -> MenuAnalysis:
    """Aggregate sales and classify items against visible arithmetic means.

    Popularity is high at or above mean units sold. Contribution is high at or
    above mean contribution per sale. These workshop rules are descriptive, not
    a claim of a universal restaurant-consulting standard.
    """
    if not menu or not sales:
        raise RestaurantValidationError("menu analysis requires menu items and sales records")
    periods = {record.period for record in sales}
    if len(periods) != 1:
        raise RestaurantValidationError("menu analysis requires exactly one sales period")
    sales_by_id = {record.item_id: record.units_sold for record in sales}
    missing = sorted({item.item_id for item in menu} - set(sales_by_id))
    if missing:
        raise RestaurantValidationError(f"sales data missing menu item(s): {', '.join(missing)}")

    popularity_threshold = Decimal(sum(sales_by_id.values())) / Decimal(len(menu))
    contribution_threshold = sum(
        (item.contribution_per_sale for item in menu), Decimal("0")
    ) / Decimal(len(menu))
    results = []
    for item in menu:
        popularity = "High popularity" if sales_by_id[item.item_id] >= popularity_threshold else "Low popularity"
        contribution = (
            "high contribution" if item.contribution_per_sale >= contribution_threshold else "low contribution"
        )
        results.append(ItemProfitability(item, sales_by_id[item.item_id], f"{popularity} + {contribution}"))
    return MenuAnalysis(next(iter(periods)), tuple(results), popularity_threshold, contribution_threshold)


def rank_by_contribution(analysis: MenuAnalysis) -> tuple[ItemProfitability, ...]:
    return tuple(sorted(analysis.items, key=lambda row: (-row.total_contribution, row.item.name)))


def simulate_price(menu: tuple[MenuItem, ...], item_id: str, price: Decimal) -> tuple[MenuItem, ...]:
    """Return a new tuple with one price changed; input objects remain untouched."""
    if item_id not in {item.item_id for item in menu}:
        raise RestaurantValidationError(f"cannot simulate unknown menu item: {item_id}")
    return tuple(item.with_price(price) if item.item_id == item_id else item for item in menu)
