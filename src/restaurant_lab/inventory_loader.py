"""Validated CSV boundaries for ingredient, recipe, inventory, and waste evidence."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .inventory import Ingredient, InventoryCount, RecipeComponent, WasteEvent
from .menu import MenuItem
from .model import RestaurantValidationError


def _rows(path: str | Path, columns: set[str]) -> list[dict[str, str]]:
    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or set(reader.fieldnames) != columns:
                raise RestaurantValidationError(f"{source.name} columns must be: {', '.join(sorted(columns))}")
            return list(reader)
    except FileNotFoundError as error:
        raise RestaurantValidationError(f"data file not found: {source}") from error


def _decimal(value: str, field: str, row: int) -> Decimal:
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError) as error:
        raise RestaurantValidationError(f"malformed {field} on row {row}: {value!r}") from error
    if not result.is_finite():
        raise RestaurantValidationError(f"{field} on row {row} must be finite")
    return result


def _date(value: str, row: int) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise RestaurantValidationError(f"malformed waste/count date on row {row}: {value!r}; use YYYY-MM-DD") from error


def _unique(values: list[str], label: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise RestaurantValidationError(f"duplicate {label}: {', '.join(duplicates)}")


def load_ingredients(path: str | Path) -> tuple[Ingredient, ...]:
    result = tuple(Ingredient(row["ingredient_id"], row["name"], row["unit"],
                              _decimal(row["unit_cost"], "unit cost", number))
                   for number, row in enumerate(_rows(path, {"ingredient_id", "name", "unit", "unit_cost"}), 2))
    if not result:
        raise RestaurantValidationError("ingredient catalog cannot be empty")
    _unique([row.ingredient_id for row in result], "ingredient identifiers")
    return result


def load_recipes(path: str | Path, menu: tuple[MenuItem, ...],
                 ingredients: tuple[Ingredient, ...]) -> tuple[RecipeComponent, ...]:
    result = tuple(RecipeComponent(row["menu_item_id"], row["ingredient_id"],
                                   _decimal(row["quantity"], "recipe quantity", number))
                   for number, row in enumerate(_rows(path, {"menu_item_id", "ingredient_id", "quantity"}), 2))
    menu_ids, ingredient_ids = {row.item_id for row in menu}, {row.ingredient_id for row in ingredients}
    for row in result:
        if row.menu_item_id not in menu_ids:
            raise RestaurantValidationError(f"recipe references unknown menu item: {row.menu_item_id}")
        if row.ingredient_id not in ingredient_ids:
            raise RestaurantValidationError(f"recipe references unknown ingredient: {row.ingredient_id}")
    _unique([f"{row.menu_item_id}/{row.ingredient_id}" for row in result], "recipe mappings")
    missing = sorted(menu_ids - {row.menu_item_id for row in result})
    if missing:
        raise RestaurantValidationError(f"recipe data missing menu item(s): {', '.join(missing)}")
    return result


def load_inventory(path: str | Path, ingredients: tuple[Ingredient, ...]) -> tuple[InventoryCount, ...]:
    result = tuple(InventoryCount(row["ingredient_id"], _decimal(row["quantity_on_hand"], "inventory quantity", number),
                                  _date(row["count_date"], number))
                   for number, row in enumerate(_rows(path, {"ingredient_id", "quantity_on_hand", "count_date"}), 2))
    ingredient_ids = {row.ingredient_id for row in ingredients}
    unknown = sorted({row.ingredient_id for row in result} - ingredient_ids)
    if unknown:
        raise RestaurantValidationError(f"inventory references unknown ingredient: {', '.join(unknown)}")
    _unique([row.ingredient_id for row in result], "inventory ingredient counts")
    missing = sorted(ingredient_ids - {row.ingredient_id for row in result})
    if missing:
        raise RestaurantValidationError(f"inventory missing ingredient(s): {', '.join(missing)}")
    return result


def load_waste(path: str | Path, ingredients: tuple[Ingredient, ...]) -> tuple[WasteEvent, ...]:
    result = tuple(WasteEvent(_date(row["date"], number), row["ingredient_id"],
                              _decimal(row["quantity"], "waste quantity", number), row["reason"])
                   for number, row in enumerate(_rows(path, {"date", "ingredient_id", "quantity", "reason"}), 2))
    ingredient_ids = {row.ingredient_id for row in ingredients}
    unknown = sorted({row.ingredient_id for row in result} - ingredient_ids)
    if unknown:
        raise RestaurantValidationError(f"waste references unknown ingredient: {', '.join(unknown)}")
    return result
