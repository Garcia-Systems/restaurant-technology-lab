"""Presentation-ready labor planning output."""

from __future__ import annotations

from decimal import Decimal

from .labor import StaffingAnalysis


def _money(value: Decimal) -> str:
    return f"${value:,.2f}"


def format_staffing_analysis(analysis: StaffingAnalysis) -> str:
    forecast = analysis.forecast
    lines = ["James River Kitchen", "Labor vs. Demand",
             "Fictional planning simulation — not an automatic staffing decision", "",
             forecast.scenario.target_date.strftime("%A, %B %d, %Y"), "", "DEMAND FORECAST", "-" * 56,
             f"Expected covers:             {forecast.expected_covers:>8}",
             f"Reasonable range:            {forecast.range_low:>4}–{forecast.range_high}",
             f"Forecast revenue:        {_money(forecast.expected_revenue):>12}", "", "CURRENT SCHEDULE", "-" * 56,
             f"Employees scheduled:         {analysis.employee_count:>8}",
             f"Scheduled labor hours:       {analysis.total_hours:>8.1f}",
             f"Estimated labor cost:    {_money(analysis.total_cost):>12}",
             f"Labor cost/forecast cover:{_money(analysis.labor_cost_per_forecast_cover):>12}", "",
             "STAFFING ALIGNMENT", "-" * 56,
             f"{'Role':<12}{'Scheduled':>10}{'Planning Range':>18}{'Status':>14}"]
    for role in analysis.roles:
        label = role.role.title()
        planning_range = f"{role.planning_low}–{role.planning_high}"
        lines.append(f"{label:<12}{role.scheduled:>10}{planning_range:>18}{role.status:>14}")
    lines.extend(["", "PLANNING SIGNALS", "-" * 56])
    exceptions = [role for role in analysis.roles if role.status != "Aligned"]
    if not exceptions:
        lines.append("- All modeled roles are within their planning ranges.")
    else:
        for role in exceptions:
            direction = "below" if role.status == "Below" else "above"
            lines.append(f"- {role.role.title()} coverage is {direction} the planning range; management may want to investigate.")
        aligned = [role.role for role in analysis.roles if role.status == "Aligned"]
        if aligned:
            lines.append(f"- Other modeled roles appear within range: {', '.join(aligned)}.")
    lines.extend(["", "James River Kitchen planning assumptions", "-" * 56])
    for assumption in analysis.assumptions:
        lines.append(f"- {assumption.role.title()}: 1 per {assumption.covers_per_employee} covers; minimum {assumption.minimum_staff}.")
    lines.extend(["", "These fictional assumptions are not restaurant-industry standards.",
                  "Layout, timing, experience, service style, menu complexity, absences,",
                  "labor rules, and manager judgment can change the operating need.", "",
                  "This is a planning signal, not an automatic staffing decision."])
    return "\n".join(lines)


def format_staffing_comparison(base: StaffingAnalysis, changed: StaffingAnalysis) -> str:
    lines = ["", "SCENARIO COMPARISON", "=" * 56,
             f"{'Role':<12}{'Scheduled':>10}{'Base range/status':>20}{'Changed range/status':>24}"]
    for before, after in zip(base.roles, changed.roles):
        left = f"{before.planning_low}–{before.planning_high} {before.status}"
        right = f"{after.planning_low}–{after.planning_high} {after.status}"
        lines.append(f"{before.role.title():<12}{before.scheduled:>10}{left:>20}{right:>24}")
    lines.extend(["", f"Base expected covers: {base.forecast.expected_covers}",
                  f"Changed expected covers: {changed.forecast.expected_covers}",
                  "The schedule didn't change. Our understanding of demand did.",
                  "Source schedule and forecast data remain unchanged; the scenario exists only in memory."])
    return "\n".join(lines)
