"""CSV boundaries for the fictional menu and aggregated POS sales."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .menu import MenuItem, SalesRecord
from .model import RestaurantValidationError


def _rows(path: str | Path, expected: set[str]) -> list[dict[str, str]]:
    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or set(reader.fieldnames) != expected:
                raise RestaurantValidationError(
                    f"{source.name} columns must be: {', '.join(sorted(expected))}"
                )
            return list(reader)
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"data file not found: {source}") from error


def _money(value: str, field: str, row_number: int) -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError) as error:
        raise RestaurantValidationError(f"malformed {field} on CSV row {row_number}: {value!r}") from error
    if not amount.is_finite() or amount.as_tuple().exponent < -2:
        raise RestaurantValidationError(f"{field} on CSV row {row_number} must be finite with at most 2 decimals")
    return amount


def load_menu(path: str | Path) -> tuple[MenuItem, ...]:
    rows = _rows(path, {"item_id", "item_name", "category", "selling_price", "ingredient_cost"})
    items = tuple(
        MenuItem(
            item_id=row["item_id"],
            name=row["item_name"],
            category=row["category"],
            selling_price=_money(row["selling_price"], "selling price", index),
            ingredient_cost=_money(row["ingredient_cost"], "ingredient cost", index),
        )
        for index, row in enumerate(rows, start=2)
    )
    identifiers = [item.item_id for item in items]
    duplicates = sorted({item_id for item_id in identifiers if identifiers.count(item_id) > 1})
    if duplicates:
        raise RestaurantValidationError(f"duplicate menu item ID(s): {', '.join(duplicates)}")
    if not items:
        raise RestaurantValidationError("menu cannot be empty")
    return items


def load_sales(path: str | Path, menu: tuple[MenuItem, ...]) -> tuple[SalesRecord, ...]:
    rows = _rows(path, {"period", "item_id", "units_sold"})
    records: list[SalesRecord] = []
    known_ids = {item.item_id for item in menu}
    for index, row in enumerate(rows, start=2):
        try:
            units = int(row["units_sold"])
        except (TypeError, ValueError) as error:
            raise RestaurantValidationError(
                f"units sold on CSV row {index} must be a non-negative integer"
            ) from error
        if row["item_id"] not in known_ids:
            raise RestaurantValidationError(
                f"sales record on CSV row {index} references unknown menu item: {row['item_id']}"
            )
        records.append(SalesRecord(row["period"], row["item_id"], units))
    keys = [(record.period, record.item_id) for record in records]
    if len(keys) != len(set(keys)):
        raise RestaurantValidationError("sales data contains duplicate period/item records")
    if not records:
        raise RestaurantValidationError("sales data cannot be empty")
    return tuple(records)
