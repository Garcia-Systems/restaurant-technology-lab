"""Validated CSV and JSON boundaries for demand-forecast evidence and rules."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from .demand import DemandObservation, ForecastRules, ReservationSnapshot
from .model import RestaurantValidationError


def _date(value: str, row: int) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise RestaurantValidationError(f"malformed date on row {row}: {value!r}; use YYYY-MM-DD") from error


def _integer(value: str, field: str, row: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise RestaurantValidationError(f"{field} on row {row} must be a non-negative integer") from error
    if str(result) != value.strip() or result < 0:
        raise RestaurantValidationError(f"{field} on row {row} must be a non-negative integer")
    return result


def _decimal(value: str, field: str, row: int) -> Decimal:
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError) as error:
        raise RestaurantValidationError(f"malformed {field} on row {row}: {value!r}") from error
    if not result.is_finite() or result.as_tuple().exponent < -2:
        raise RestaurantValidationError(f"{field} on row {row} must be finite with at most 2 decimals")
    return result


def _csv_rows(path: str | Path, columns: set[str]) -> list[dict[str, str]]:
    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or set(reader.fieldnames) != columns:
                raise RestaurantValidationError(f"{source.name} columns must be: {', '.join(sorted(columns))}")
            return list(reader)
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"data file not found: {source}") from error


def load_demand_history(path: str | Path) -> tuple[DemandObservation, ...]:
    rows = _csv_rows(path, {"date", "total_covers", "revenue", "weather", "local_event"})
    observations = []
    for number, row in enumerate(rows, 2):
        if row["local_event"] not in {"yes", "no"}:
            raise RestaurantValidationError(f"local_event on row {number} must be yes or no")
        observations.append(DemandObservation(_date(row["date"], number),
            _integer(row["total_covers"], "total covers", number),
            _decimal(row["revenue"], "revenue", number), row["weather"], row["local_event"] == "yes"))
    if not observations:
        raise RestaurantValidationError("historical demand data cannot be empty")
    dates = [row.service_date for row in observations]
    if len(dates) != len(set(dates)):
        raise RestaurantValidationError("historical demand contains duplicate daily observations")
    return tuple(observations)


def load_reservations(path: str | Path, history: tuple[DemandObservation, ...]) -> tuple[ReservationSnapshot, ...]:
    rows = _csv_rows(path, {"date", "booked_covers"})
    snapshots = tuple(ReservationSnapshot(_date(row["date"], number),
        _integer(row["booked_covers"], "reservations booked", number)) for number, row in enumerate(rows, 2))
    if not snapshots:
        raise RestaurantValidationError("reservation data cannot be empty")
    dates = [row.service_date for row in snapshots]
    if len(dates) != len(set(dates)):
        raise RestaurantValidationError("reservation data contains duplicate dates")
    historical_dates = {row.service_date for row in history}
    unresolved = sorted(day.isoformat() for day in historical_dates - set(dates))
    if unresolved:
        raise RestaurantValidationError(f"historical demand has no reservation reference for: {', '.join(unresolved)}")
    return snapshots


def load_forecast_rules(path: str | Path) -> ForecastRules:
    source = Path(path)
    try:
        document = json.loads(source.read_text(encoding="utf-8"), parse_float=Decimal)
        return ForecastRules(document["reservation_show_rate"], document["event_rate"],
                             document["weather_rates"], document["range_rate"])
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"forecast rules not found: {source}") from error
    except json.JSONDecodeError as error:
        raise RestaurantValidationError(f"forecast rules are not valid JSON: {error.msg}") from error
    except (KeyError, TypeError) as error:
        raise RestaurantValidationError(f"malformed forecast rules: {error}") from error
