"""Presentation-oriented inventory, coverage, and waste reporting."""

from __future__ import annotations

from decimal import Decimal

from .inventory import InventoryAnalysis


def _quantity(value: Decimal) -> str:
    return f"{value:.1f}"


def format_inventory_analysis(analysis: InventoryAnalysis) -> str:
    forecast = analysis.forecast
    risks = sorted(analysis.coverage, key=lambda row: (
        {"Potential shortage": 0, "Near threshold": 1, "Comfortable": 2}[row.status], row.ingredient.name))
    waste = sorted((row for row in analysis.coverage if row.waste_quantity),
                   key=lambda row: (-row.waste_cost, row.ingredient.name))
    lines = ["James River Kitchen", "Inventory and Food Waste",
             "Fictional planning data — decision support, not an automatic purchase order", "",
             forecast.scenario.target_date.strftime("%A, %B %d, %Y"), "", "DEMAND", "-" * 72,
             f"Forecast covers: {forecast.expected_covers}",
             f"Reasonable range: {forecast.range_low}–{forecast.range_high}",
             "Estimated menu mix: July POS item shares; one menu-item unit per forecast cover.",
             f"Planning buffer: {analysis.buffer_rate:.0%} (fictional James River Kitchen assumption)", "",
             "INVENTORY SNAPSHOT", "-" * 72,
             f"{'Ingredient':28} {'On hand':>10} {'Est. usage':>11} {'Plan need':>10}  Status"]
    for row in risks:
        unit = row.ingredient.unit
        lines.append(f"{row.ingredient.name[:28]:28} {_quantity(row.quantity_on_hand):>7} {unit[:3]:3} "
                     f"{_quantity(row.expected_usage):>8} {unit[:3]:3} {_quantity(row.planning_need):>7} {unit[:3]:3}  {row.status}")
    lines.extend(["", "RECORDED WASTE — AUGUST 2026", "-" * 72,
                  f"{'Ingredient':28} {'Waste quantity':>18} {'Waste cost':>14}"])
    for row in waste:
        lines.append(f"{row.ingredient.name[:28]:28} {_quantity(row.waste_quantity):>10} {row.ingredient.unit[:3]:3} "
                     f"${row.waste_cost:>10,.2f}")
    lines.extend([f"\nTotal recorded waste cost: ${analysis.total_waste_cost:,.2f}",
                  f"Current inventory value: ${analysis.total_inventory_value:,.2f}", "",
                  "BUSINESS OBSERVATIONS", "-" * 72])
    if waste:
        top_three = sum((row.waste_cost for row in waste[:3]), Decimal("0"))
        share = top_three / analysis.total_waste_cost if analysis.total_waste_cost else Decimal("0")
        lines.extend([f"- {waste[0].ingredient.name} generated the highest recorded waste cost.",
                      f"- The top three ingredients represent {share:.0%} of recorded waste cost."])
    lines.extend(["- Potential shortages and near-threshold rows are planning signals; recount and verify assumptions.", "",
                  "POS sale -> Menu item -> Recipe -> Ingredient usage -> Inventory -> Financial consequence"])
    return "\n".join(lines)


def format_inventory_comparison(base: InventoryAnalysis, changed: InventoryAnalysis) -> str:
    count = lambda result, status: sum(row.status == status for row in result.coverage)
    return "\n".join(["", "SCENARIO COMPARISON", "=" * 72,
        f"Base demand: {base.forecast.expected_covers} covers; potential shortages: {count(base, 'Potential shortage')}",
        f"Changed demand: {changed.forecast.expected_covers} covers; potential shortages: {count(changed, 'Potential shortage')}",
        "The physical inventory did not change. The demand assumption changed, so the risk assessment changed.",
        "Source data remains unchanged; this scenario exists only in memory."])
