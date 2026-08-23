"""Immutable contracts for the fictional inventory and food-waste simulation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .demand import DemandForecast
from .menu import MenuItem
from .model import RestaurantValidationError


SUPPORTED_UNITS = frozenset({"each", "ounce", "pound", "fluid ounce", "cup"})
WASTE_REASONS = frozenset({"spoilage", "prep waste", "overproduction", "damage"})


def _positive(value: Decimal, field: str, *, zero_allowed: bool = False) -> None:
    valid = value.is_finite() and (value >= 0 if zero_allowed else value > 0)
    if not valid:
        qualifier = "non-negative" if zero_allowed else "positive"
        raise RestaurantValidationError(f"{field} must be a finite, {qualifier} quantity")


@dataclass(frozen=True)
class Ingredient:
    ingredient_id: str
    name: str
    unit: str
    unit_cost: Decimal

    def __post_init__(self) -> None:
        if not self.ingredient_id.strip() or not self.name.strip():
            raise RestaurantValidationError("ingredient identifier and name cannot be empty")
        if self.unit not in SUPPORTED_UNITS:
            raise RestaurantValidationError(f"unsupported ingredient unit: {self.unit}")
        _positive(self.unit_cost, "ingredient unit cost", zero_allowed=True)


@dataclass(frozen=True)
class RecipeComponent:
    menu_item_id: str
    ingredient_id: str
    quantity: Decimal

    def __post_init__(self) -> None:
        if not self.menu_item_id.strip() or not self.ingredient_id.strip():
            raise RestaurantValidationError("recipe references cannot be empty")
        _positive(self.quantity, "recipe quantity")


@dataclass(frozen=True)
class InventoryCount:
    ingredient_id: str
    quantity_on_hand: Decimal
    count_date: date

    def __post_init__(self) -> None:
        if not self.ingredient_id.strip():
            raise RestaurantValidationError("inventory ingredient reference cannot be empty")
        _positive(self.quantity_on_hand, "inventory quantity", zero_allowed=True)


@dataclass(frozen=True)
class WasteEvent:
    event_date: date
    ingredient_id: str
    quantity: Decimal
    reason: str

    def __post_init__(self) -> None:
        if not self.ingredient_id.strip():
            raise RestaurantValidationError("waste ingredient reference cannot be empty")
        _positive(self.quantity, "waste quantity")
        if self.reason not in WASTE_REASONS:
            raise RestaurantValidationError(f"unsupported waste reason: {self.reason}")


@dataclass(frozen=True)
class IngredientCoverage:
    ingredient: Ingredient
    quantity_on_hand: Decimal
    expected_usage: Decimal
    planning_need: Decimal
    historical_usage: Decimal
    waste_quantity: Decimal
    waste_cost: Decimal
    status: str

    @property
    def inventory_value(self) -> Decimal:
        return self.quantity_on_hand * self.ingredient.unit_cost


@dataclass(frozen=True)
class InventoryAnalysis:
    forecast: DemandForecast
    menu_mix: dict[str, Decimal]
    buffer_rate: Decimal
    coverage: tuple[IngredientCoverage, ...]

    @property
    def total_inventory_value(self) -> Decimal:
        return sum((row.inventory_value for row in self.coverage), Decimal("0"))

    @property
    def total_waste_cost(self) -> Decimal:
        return sum((row.waste_cost for row in self.coverage), Decimal("0"))


def validate_recipe_costs(menu: tuple[MenuItem, ...], ingredients: tuple[Ingredient, ...],
                          recipes: tuple[RecipeComponent, ...]) -> None:
    """Ensure recipe-derived costs remain the one ingredient-cost fact used by Chapter 2."""
    ingredient_by_id = {row.ingredient_id: row for row in ingredients}
    for item in menu:
        derived = sum((row.quantity * ingredient_by_id[row.ingredient_id].unit_cost
                       for row in recipes if row.menu_item_id == item.item_id), Decimal("0"))
        if derived != item.ingredient_cost:
            raise RestaurantValidationError(
                f"recipe cost for {item.item_id} ({derived}) does not match menu ingredient cost ({item.ingredient_cost})")
