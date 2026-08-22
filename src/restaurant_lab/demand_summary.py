"""Presentation-oriented rendering for demand forecasts and comparisons."""

from __future__ import annotations

from decimal import Decimal

from .demand import DemandForecast


def _money(value: Decimal) -> str:
    return f"${value:,.2f}"


def _signed(value: int) -> str:
    return f"{value:+d}"


def format_demand_forecast(forecast: DemandForecast) -> str:
    scenario = forecast.scenario
    direction = "above" if forecast.day_adjustment > 0 else "below" if forecast.day_adjustment < 0 else "at"
    lines = ["James River Kitchen", "Tonight's Demand Forecast",
             "Fictional demonstration data — forecast, not a fact", "",
             scenario.target_date.strftime("%A, %B %d, %Y"), "", "What we know", "-" * 40,
             f"Reservations booked: {scenario.reservations_booked:>14}",
             f"Weather: {scenario.weather.title():>26}",
             f"Local event: {('Yes' if scenario.local_event else 'No'):>22}", "",
             "Historical evidence", "-" * 40,
             f"Overall normal-night covers: {forecast.weekly_baseline:>10.1f}",
             f"Typical {scenario.target_date.strftime('%A')} covers: {forecast.weekday_baseline:>10.1f}",
             f"Typical booked reservations: {forecast.typical_reservations:>8.1f}",
             f"Average revenue/cover: {_money(forecast.revenue_per_cover):>14}", "",
             "Forecast adjustments", "-" * 40,
             f"Day-of-week: {_signed(forecast.day_adjustment):>23}",
             f"Reservation signal: {_signed(forecast.reservation_adjustment):>19}",
             f"Local event: {_signed(forecast.event_adjustment):>24}",
             f"Weather: {_signed(forecast.weather_adjustment):>28}", "",
             "Forecast", "-" * 40,
             f"Reservations already booked: {scenario.reservations_booked:>9}",
             f"Expected walk-ins / other demand: {forecast.expected_walk_ins:>5}",
             f"Expected covers: {forecast.expected_covers:>18}",
             f"Reasonable forecast range: {forecast.range_low:>7}–{forecast.range_high}",
             f"Expected revenue: {_money(forecast.expected_revenue):>17}", "", "Why this number", "-" * 40,
             f"- {scenario.target_date.strftime('%A')} demand historically runs {direction} the normal-night average.",
             f"- Reservations are compared with the historical {scenario.target_date.strftime('%A')} booking level; only the documented show-rate is applied.",
             f"- Event and {scenario.weather} weather rules apply visible percentages to typical {scenario.target_date.strftime('%A')} demand.",
             "", "Forecast ≠ fact.",
             "Actual demand might be lower or higher. This is a defensible planning assumption, not knowledge of the future."]
    return "\n".join(lines)


def format_scenario_comparison(base: DemandForecast, changed: DemandForecast) -> str:
    return "\n".join(["", "SCENARIO COMPARISON", "=" * 40,
        f"Base scenario:    {base.expected_covers} covers ({base.scenario.weather}, event {'yes' if base.scenario.local_event else 'no'}, {base.scenario.reservations_booked} booked)",
        f"Changed scenario: {changed.expected_covers} covers ({changed.scenario.weather}, event {'yes' if changed.scenario.local_event else 'no'}, {changed.scenario.reservations_booked} booked)",
        f"Difference:       {_signed(changed.expected_covers - base.expected_covers)} covers",
        "Source CSV files are unchanged; the changed scenario exists only in memory."])
