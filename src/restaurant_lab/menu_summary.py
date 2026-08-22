"""Presentation-ready output for the menu profitability lab."""

from __future__ import annotations

from decimal import Decimal

from .menu import MenuAnalysis, MenuItem
from .profitability import rank_by_contribution


def _money(value: Decimal) -> str:
    return f"${value:,.2f}"


def _percent(value: Decimal) -> str:
    return f"{value:.1%}"


def format_menu_analysis(analysis: MenuAnalysis, *, baseline_item: MenuItem | None = None) -> str:
    ranked = rank_by_contribution(analysis)
    lines = [
        "James River Kitchen",
        "Menu Profitability Analysis",
        "Fictional demonstration data — estimated ingredient cost, not accounting profit",
        "",
        f"Period: {analysis.period}",
        f"Total menu revenue:      {_money(analysis.total_revenue):>12}",
        f"Estimated food cost:     {_money(analysis.total_food_cost):>12}",
        f"Total contribution:      {_money(analysis.total_contribution):>12}",
        f"Estimated food cost %:   {_percent(analysis.food_cost_percentage):>12}",
    ]
    if baseline_item is not None:
        changed = next(row for row in analysis.items if row.item.item_id == baseline_item.item_id)
        old_contribution = baseline_item.contribution_per_sale
        delta_per_sale = changed.contribution_per_sale - old_contribution
        lines.extend(["", "SIMULATION — source CSV files are unchanged",
            f"{changed.item.name}: price {_money(baseline_item.selling_price)} -> {_money(changed.item.selling_price)}",
            f"Contribution per sale: {_money(old_contribution)} -> {_money(changed.contribution_per_sale)} ({_money(delta_per_sale)} change)",
            f"Simulated total contribution change: {_money(delta_per_sale * changed.units_sold)}",
            f"Simulated margin: {_percent(changed.contribution_margin)}"])
    lines.extend(["", "Ranked by total contribution",
        f"{'Item':32} {'Units':>6} {'Revenue':>12} {'Contribution':>14} {'Margin':>8}", "-" * 76])
    lines.extend(
        f"{row.item.name[:32]:32} {row.units_sold:6d} {_money(row.revenue):>12} {_money(row.total_contribution):>14} {_percent(row.contribution_margin):>8}"
        for row in ranked
    )
    by_revenue = max(analysis.items, key=lambda row: row.revenue)
    by_units = max(analysis.items, key=lambda row: row.units_sold)
    by_per_sale = max(analysis.items, key=lambda row: row.contribution_per_sale)
    popular = [row for row in analysis.items if row.units_sold >= analysis.popularity_threshold]
    unpopular = [row for row in analysis.items if row.units_sold < analysis.popularity_threshold]
    weak_popular = min(popular, key=lambda row: row.contribution_margin)
    strong_unpopular = max(unpopular, key=lambda row: row.contribution_margin)
    lines.extend(["", "Business observations",
        f"- Best seller by units: {by_units.item.name} ({by_units.units_sold:,}); it ranks #{ranked.index(by_units) + 1} in total contribution.",
        f"- Highest revenue item: {by_revenue.item.name} ({_money(by_revenue.revenue)}).",
        f"- Highest total contribution item: {ranked[0].item.name} ({_money(ranked[0].total_contribution)}).",
        f"- Highest contribution per sale: {by_per_sale.item.name} ({_money(by_per_sale.contribution_per_sale)}).",
        f"- Popular item with relatively weak margin: {weak_popular.item.name} ({_percent(weak_popular.contribution_margin)}).",
        f"- High-margin item with low sales volume: {strong_unpopular.item.name} ({_percent(strong_unpopular.contribution_margin)}, {strong_unpopular.units_sold} units).",
        "", "Menu-engineering rules (simple workshop quadrants)",
        f"- High popularity: units >= mean units, {analysis.popularity_threshold:.1f}.",
        f"- High contribution: contribution per sale >= menu mean, {_money(analysis.contribution_threshold)}.",
        "- These descriptive thresholds support questions; they do not replace operator judgment."])
    return "\n".join(lines)
