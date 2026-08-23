"""Explainable inventory calculations joining POS sales, recipes, and forecasts."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from .demand import DemandForecast
from .inventory import (Ingredient, IngredientCoverage, InventoryAnalysis, InventoryCount,
                        RecipeComponent, WasteEvent)
from .menu import SalesRecord
from .model import RestaurantValidationError


def historical_ingredient_usage(sales: tuple[SalesRecord, ...], recipes: tuple[RecipeComponent, ...]) -> dict[str, Decimal]:
    units = {row.item_id: row.units_sold for row in sales}
    return _ingredient_usage({item_id: Decimal(value) for item_id, value in units.items()}, recipes)


def calculate_menu_mix(sales: tuple[SalesRecord, ...]) -> dict[str, Decimal]:
    total = sum(row.units_sold for row in sales)
    if total <= 0:
        raise RestaurantValidationError("menu mix requires positive historical sales")
    return {row.item_id: Decimal(row.units_sold) / Decimal(total) for row in sales}


def expected_ingredient_demand(forecast: DemandForecast, menu_mix: dict[str, Decimal],
                               recipes: tuple[RecipeComponent, ...]) -> dict[str, Decimal]:
    return _ingredient_usage({item_id: Decimal(forecast.expected_covers) * share
                              for item_id, share in menu_mix.items()}, recipes)


def _ingredient_usage(item_quantities: dict[str, Decimal], recipes: tuple[RecipeComponent, ...]) -> dict[str, Decimal]:
    usage: dict[str, Decimal] = {}
    for component in recipes:
        usage[component.ingredient_id] = usage.get(component.ingredient_id, Decimal("0")) + (
            item_quantities.get(component.menu_item_id, Decimal("0")) * component.quantity)
    return usage


def analyze_inventory(forecast: DemandForecast, ingredients: tuple[Ingredient, ...],
                      recipes: tuple[RecipeComponent, ...], inventory: tuple[InventoryCount, ...],
                      waste: tuple[WasteEvent, ...], sales: tuple[SalesRecord, ...],
                      buffer_rate: Decimal = Decimal("0.10")) -> InventoryAnalysis:
    if not buffer_rate.is_finite() or buffer_rate < 0:
        raise RestaurantValidationError("planning buffer must be a finite, non-negative rate")
    mix = calculate_menu_mix(sales)
    expected = expected_ingredient_demand(forecast, mix, recipes)
    historical = historical_ingredient_usage(sales, recipes)
    on_hand = {row.ingredient_id: row.quantity_on_hand for row in inventory}
    if set(on_hand) != {row.ingredient_id for row in ingredients}:
        raise RestaurantValidationError("inventory analysis requires one count for every ingredient")
    rows = []
    for ingredient in ingredients:
        usage = expected.get(ingredient.ingredient_id, Decimal("0"))
        need = usage * (Decimal("1") + buffer_rate)
        stock = on_hand[ingredient.ingredient_id]
        # Potential shortage: stock is below buffered need. Near threshold: stock covers
        # buffered need but has less than one additional 10% expected-usage cushion.
        if stock < need:
            status = "Potential shortage"
        elif stock < need + (usage * Decimal("0.10")):
            status = "Near threshold"
        else:
            status = "Comfortable"
        wasted = sum((row.quantity for row in waste if row.ingredient_id == ingredient.ingredient_id), Decimal("0"))
        rows.append(IngredientCoverage(ingredient, stock, usage, need, historical.get(ingredient.ingredient_id, Decimal("0")),
                                       wasted, wasted * ingredient.unit_cost, status))
    return InventoryAnalysis(forecast, mix, buffer_rate, tuple(rows))


def simulate_ingredient_cost(ingredients: tuple[Ingredient, ...], ingredient_id: str,
                             unit_cost: Decimal) -> tuple[Ingredient, ...]:
    if ingredient_id not in {row.ingredient_id for row in ingredients}:
        raise RestaurantValidationError(f"cannot simulate unknown ingredient: {ingredient_id}")
    if not unit_cost.is_finite() or unit_cost < 0:
        raise RestaurantValidationError("simulated ingredient cost must be finite and non-negative")
    return tuple(replace(row, unit_cost=unit_cost) if row.ingredient_id == ingredient_id else row
                 for row in ingredients)
