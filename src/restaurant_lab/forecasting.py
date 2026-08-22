"""Deterministic, explainable demand calculations—not machine learning."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP

from .demand import DemandForecast, DemandObservation, ForecastRules, ForecastScenario, ReservationSnapshot
from .model import RestaurantValidationError


def _round(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def forecast_demand(history: tuple[DemandObservation, ...], reservations: tuple[ReservationSnapshot, ...],
                    scenario: ForecastScenario, rules: ForecastRules) -> DemandForecast:
    """Build a forecast whose baseline and every adjustment remain visible."""
    if not history:
        raise RestaurantValidationError("forecast requires historical demand data")
    prior = tuple(row for row in history if row.service_date < scenario.target_date)
    comparable = tuple(row for row in prior if not row.local_event)
    weekday = tuple(row for row in comparable if row.service_date.weekday() == scenario.target_date.weekday())
    if not comparable or not weekday:
        raise RestaurantValidationError(f"no historical demand for {scenario.target_date.strftime('%A')} before target date")
    reservation_by_date = {row.service_date: row.booked_covers for row in reservations}
    missing = [row.service_date.isoformat() for row in weekday if row.service_date not in reservation_by_date]
    if missing:
        raise RestaurantValidationError(f"reservation references cannot be resolved for: {', '.join(missing)}")

    weekly = Decimal(sum(row.total_covers for row in comparable)) / Decimal(len(comparable))
    day = Decimal(sum(row.total_covers for row in weekday)) / Decimal(len(weekday))
    typical_reservations = Decimal(sum(reservation_by_date[row.service_date] for row in weekday)) / Decimal(len(weekday))
    day_adjustment = _round(day - weekly)
    reservation_adjustment = _round((Decimal(scenario.reservations_booked) - typical_reservations)
                                    * rules.reservation_show_rate)
    event_adjustment = _round(day * rules.event_rate) if scenario.local_event else 0
    weather_adjustment = _round(day * rules.weather_rates[scenario.weather])
    expected = max(0, _round(weekly) + day_adjustment + reservation_adjustment + event_adjustment + weather_adjustment)
    spread = max(1, _round(Decimal(expected) * rules.range_rate))
    revenue_per_cover = sum((row.revenue for row in prior), Decimal("0")) / Decimal(sum(row.total_covers for row in prior))
    revenue = (Decimal(expected) * revenue_per_cover).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return DemandForecast(scenario, weekly, day, typical_reservations, day_adjustment,
                          reservation_adjustment, event_adjustment, weather_adjustment, expected,
                          max(0, expected - spread), expected + spread, revenue_per_cover, revenue)


def override_scenario(scenario: ForecastScenario, **changes: object) -> ForecastScenario:
    """Return a validated scenario copy without mutating loaded source evidence."""
    return replace(scenario, **changes)
