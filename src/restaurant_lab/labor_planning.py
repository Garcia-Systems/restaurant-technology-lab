"""Translate a Chapter 3 forecast into restrained staffing planning signals."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING

from .demand import DemandForecast
from .labor import (LABOR_ROLES, RolePlanningAssumption, RoleStaffingAlignment,
                    ScheduledShift, StaffingAnalysis)
from .model import RestaurantValidationError


def _needed(covers: int, assumption: RolePlanningAssumption) -> int:
    ratio = (Decimal(covers) / Decimal(assumption.covers_per_employee)).quantize(
        Decimal("1"), rounding=ROUND_CEILING)
    return max(assumption.minimum_staff, int(ratio))


def analyze_staffing(forecast: DemandForecast, shifts: tuple[ScheduledShift, ...],
                     assumptions: tuple[RolePlanningAssumption, ...]) -> StaffingAnalysis:
    """Compare one unchanged schedule with role ranges derived from the forecast range."""
    if not shifts:
        raise RestaurantValidationError("staffing analysis requires schedule data")
    if not assumptions:
        raise RestaurantValidationError("staffing analysis requires role assumptions")
    if any(shift.service_date != forecast.scenario.target_date for shift in shifts):
        raise RestaurantValidationError("every shift must match the forecast service date")
    by_role = {assumption.role: assumption for assumption in assumptions}
    if set(by_role) != set(LABOR_ROLES) or len(by_role) != len(assumptions):
        raise RestaurantValidationError("staffing analysis requires one assumption for every supported role")
    roles = tuple(RoleStaffingAlignment(
        role,
        sum(shift.role == role for shift in shifts),
        _needed(forecast.range_low, by_role[role]),
        _needed(forecast.range_high, by_role[role]),
    ) for role in LABOR_ROLES)
    total_hours = sum((shift.duration_hours for shift in shifts), Decimal("0"))
    total_cost = sum((shift.labor_cost for shift in shifts), Decimal("0")).quantize(Decimal("0.01"))
    return StaffingAnalysis(forecast, tuple(shifts), tuple(assumptions), roles, total_hours, total_cost)
