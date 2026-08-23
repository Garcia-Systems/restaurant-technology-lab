"""Immutable contracts for James River Kitchen's labor-planning simulation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal

from .demand import DemandForecast
from .model import RestaurantValidationError


LABOR_ROLES = ("host", "server", "bartender", "cook", "support")


@dataclass(frozen=True)
class ScheduledShift:
    shift_id: str
    service_date: date
    employee_id: str
    role: str
    shift_start: time
    shift_end: time
    hourly_cost: Decimal

    def __post_init__(self) -> None:
        if not self.shift_id.strip() or not self.employee_id.strip():
            raise RestaurantValidationError("shift and employee identifiers cannot be empty")
        if self.role not in LABOR_ROLES:
            raise RestaurantValidationError(f"unsupported labor role: {self.role}")
        if self.shift_end <= self.shift_start:
            raise RestaurantValidationError("shift end must be after shift start")
        if not self.hourly_cost.is_finite() or self.hourly_cost < 0:
            raise RestaurantValidationError("hourly cost must be a finite, non-negative amount")

    @property
    def duration_hours(self) -> Decimal:
        start = datetime.combine(self.service_date, self.shift_start)
        end = datetime.combine(self.service_date, self.shift_end)
        return Decimal(int((end - start).total_seconds())) / Decimal("3600")

    @property
    def labor_cost(self) -> Decimal:
        return self.duration_hours * self.hourly_cost


@dataclass(frozen=True)
class RolePlanningAssumption:
    role: str
    covers_per_employee: int
    minimum_staff: int

    def __post_init__(self) -> None:
        if self.role not in LABOR_ROLES:
            raise RestaurantValidationError(f"unsupported labor role: {self.role}")
        if (isinstance(self.covers_per_employee, bool) or
                not isinstance(self.covers_per_employee, int) or self.covers_per_employee <= 0):
            raise RestaurantValidationError("covers per employee must be a positive integer")
        if (isinstance(self.minimum_staff, bool) or
                not isinstance(self.minimum_staff, int) or self.minimum_staff < 0):
            raise RestaurantValidationError("minimum staff must be a non-negative integer")


@dataclass(frozen=True)
class RoleStaffingAlignment:
    role: str
    scheduled: int
    planning_low: int
    planning_high: int

    def __post_init__(self) -> None:
        if self.role not in LABOR_ROLES:
            raise RestaurantValidationError(f"unsupported labor role: {self.role}")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
               for value in (self.scheduled, self.planning_low, self.planning_high)):
            raise RestaurantValidationError("staffing counts must be non-negative integers")
        if self.planning_high < self.planning_low:
            raise RestaurantValidationError("staffing planning range is invalid")

    @property
    def status(self) -> str:
        if self.scheduled < self.planning_low:
            return "Below"
        if self.scheduled > self.planning_high:
            return "Above"
        return "Aligned"


@dataclass(frozen=True)
class StaffingAnalysis:
    forecast: DemandForecast
    shifts: tuple[ScheduledShift, ...]
    assumptions: tuple[RolePlanningAssumption, ...]
    roles: tuple[RoleStaffingAlignment, ...]
    total_hours: Decimal
    total_cost: Decimal

    @property
    def employee_count(self) -> int:
        return len({shift.employee_id for shift in self.shifts})

    @property
    def labor_cost_per_forecast_cover(self) -> Decimal:
        if self.forecast.expected_covers == 0:
            return Decimal("0")
        return self.total_cost / Decimal(self.forecast.expected_covers)
