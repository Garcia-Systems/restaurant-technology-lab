"""Validated boundaries for fictional schedule and planning assumptions."""

from __future__ import annotations

import csv
from datetime import date, time
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from .labor import LABOR_ROLES, RolePlanningAssumption, ScheduledShift
from .model import RestaurantValidationError


def _time(value: str, row: int, field: str) -> time:
    try:
        parsed = time.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise RestaurantValidationError(f"malformed {field} on row {row}: {value!r}; use HH:MM") from error
    if parsed.second or parsed.microsecond:
        raise RestaurantValidationError(f"{field} on row {row} must use HH:MM")
    return parsed


def load_schedule(path: str | Path) -> tuple[ScheduledShift, ...]:
    source = Path(path)
    columns = {"shift_id", "date", "employee_id", "role", "shift_start", "shift_end", "hourly_cost"}
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or set(reader.fieldnames) != columns:
                raise RestaurantValidationError(f"{source.name} columns must be: {', '.join(sorted(columns))}")
            rows = list(reader)
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"schedule data file not found: {source}") from error
    if not rows:
        raise RestaurantValidationError("schedule data cannot be empty")
    shifts = []
    for number, row in enumerate(rows, 2):
        try:
            service_date = date.fromisoformat(row["date"])
        except (TypeError, ValueError) as error:
            raise RestaurantValidationError(f"malformed schedule date on row {number}: {row['date']!r}") from error
        try:
            hourly_cost = Decimal(row["hourly_cost"])
        except (InvalidOperation, TypeError) as error:
            raise RestaurantValidationError(f"malformed hourly cost on row {number}") from error
        if not hourly_cost.is_finite() or hourly_cost.as_tuple().exponent < -2:
            raise RestaurantValidationError(f"hourly cost on row {number} must be finite with at most 2 decimals")
        shifts.append(ScheduledShift(row["shift_id"], service_date, row["employee_id"], row["role"],
                                     _time(row["shift_start"], number, "shift start"),
                                     _time(row["shift_end"], number, "shift end"), hourly_cost))
    identifiers = [shift.shift_id for shift in shifts]
    if len(identifiers) != len(set(identifiers)):
        raise RestaurantValidationError("schedule contains duplicate shift identifiers")
    employee_services = [(shift.service_date, shift.employee_id) for shift in shifts]
    if len(employee_services) != len(set(employee_services)):
        raise RestaurantValidationError("schedule contains duplicate employee shifts for a service date")
    return tuple(shifts)


def load_labor_assumptions(path: str | Path) -> tuple[RolePlanningAssumption, ...]:
    source = Path(path)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
        rows = document["roles"]
        assumptions = tuple(RolePlanningAssumption(row["role"], row["covers_per_employee"],
                                                   row["minimum_staff"]) for row in rows)
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"labor assumptions file not found: {source}") from error
    except json.JSONDecodeError as error:
        raise RestaurantValidationError(f"labor assumptions are not valid JSON: {error.msg}") from error
    except (KeyError, TypeError) as error:
        raise RestaurantValidationError(f"malformed labor assumptions: {error}") from error
    roles = [assumption.role for assumption in assumptions]
    if set(roles) != set(LABOR_ROLES) or len(roles) != len(LABOR_ROLES):
        raise RestaurantValidationError("labor assumptions must define each supported role exactly once")
    return assumptions
