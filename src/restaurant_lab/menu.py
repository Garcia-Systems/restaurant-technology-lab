"""Domain contracts for transparent menu-profitability analysis."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from .model import RestaurantValidationError


ZERO = Decimal("0")


@dataclass(frozen=True)
class MenuItem:
    item_id: str
    name: str
    category: str
    selling_price: Decimal
    ingredient_cost: Decimal

    def __post_init__(self) -> None:
        for value, field in ((self.item_id, "item ID"), (self.name, "item name"), (self.category, "category")):
            if not isinstance(value, str) or not value.strip():
                raise RestaurantValidationError(f"menu {field} must be a non-empty string")
        if self.selling_price <= ZERO:
            raise RestaurantValidationError(f"selling price for {self.item_id} must be positive")
        if self.ingredient_cost < ZERO:
            raise RestaurantValidationError(f"ingredient cost for {self.item_id} cannot be negative")
        if self.ingredient_cost >= self.selling_price:
            raise RestaurantValidationError(
                f"ingredient cost for {self.item_id} must be less than its selling price"
            )

    @property
    def contribution_per_sale(self) -> Decimal:
        return self.selling_price - self.ingredient_cost

    @property
    def contribution_margin(self) -> Decimal:
        return self.contribution_per_sale / self.selling_price if self.selling_price else ZERO

    def with_price(self, selling_price: Decimal) -> "MenuItem":
        """Return a simulated item; never alter the source menu item."""
        return replace(self, selling_price=selling_price)


@dataclass(frozen=True)
class SalesRecord:
    period: str
    item_id: str
    units_sold: int

    def __post_init__(self) -> None:
        if not self.period.strip():
            raise RestaurantValidationError("sales period must be a non-empty string")
        if not self.item_id.strip():
            raise RestaurantValidationError("sales item ID must be a non-empty string")
        if isinstance(self.units_sold, bool) or not isinstance(self.units_sold, int) or self.units_sold < 0:
            raise RestaurantValidationError(f"units sold for {self.item_id} must be a non-negative integer")


@dataclass(frozen=True)
class ItemProfitability:
    item: MenuItem
    units_sold: int
    classification: str

    @property
    def revenue(self) -> Decimal:
        return self.item.selling_price * self.units_sold

    @property
    def estimated_food_cost(self) -> Decimal:
        return self.item.ingredient_cost * self.units_sold

    @property
    def total_contribution(self) -> Decimal:
        return self.revenue - self.estimated_food_cost

    @property
    def contribution_per_sale(self) -> Decimal:
        return self.item.contribution_per_sale

    @property
    def contribution_margin(self) -> Decimal:
        return self.item.contribution_margin


@dataclass(frozen=True)
class MenuAnalysis:
    period: str
    items: tuple[ItemProfitability, ...]
    popularity_threshold: Decimal
    contribution_threshold: Decimal

    @property
    def total_revenue(self) -> Decimal:
        return sum((item.revenue for item in self.items), ZERO)

    @property
    def total_food_cost(self) -> Decimal:
        return sum((item.estimated_food_cost for item in self.items), ZERO)

    @property
    def total_contribution(self) -> Decimal:
        return self.total_revenue - self.total_food_cost

    @property
    def food_cost_percentage(self) -> Decimal:
        return self.total_food_cost / self.total_revenue if self.total_revenue else ZERO
