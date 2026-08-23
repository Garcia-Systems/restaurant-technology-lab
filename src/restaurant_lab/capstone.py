"""Compose the existing chapter analyses into one Friday readiness briefing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .demand import DemandForecast, ForecastScenario
from .demand_loader import load_demand_history, load_forecast_rules, load_reservations
from .feedback import FeedbackAnalysis
from .feedback_analysis import analyze_feedback
from .feedback_loader import load_reviews
from .forecasting import forecast_demand
from .inventory import InventoryAnalysis
from .inventory_loader import load_ingredients, load_inventory, load_recipes, load_waste
from .inventory_planning import analyze_inventory
from .labor import StaffingAnalysis
from .labor_loader import load_labor_assumptions, load_schedule
from .labor_planning import analyze_staffing
from .loader import load_restaurant
from .menu import ItemProfitability, MenuAnalysis
from .menu_loader import load_menu, load_sales
from .model import Restaurant, RestaurantValidationError
from .profitability import analyze_menu


PRIORITIES = ("HIGH PRIORITY", "WATCH", "OPPORTUNITY", "POSITIVE")


@dataclass(frozen=True)
class ReadinessSignal:
    """A categorical observation with enough evidence to explain its origin."""

    priority: str
    title: str
    interpretation: str
    evidence: tuple[str, ...]
    management_question: str

    def __post_init__(self) -> None:
        if self.priority not in PRIORITIES:
            raise RestaurantValidationError(f"unsupported readiness priority: {self.priority}")
        if not self.title.strip() or not self.interpretation.strip() or not self.evidence:
            raise RestaurantValidationError("readiness signals require a title, interpretation, and evidence")


@dataclass(frozen=True)
class CapstoneBriefing:
    restaurant: Restaurant
    menu: MenuAnalysis
    demand: DemandForecast
    labor: StaffingAnalysis
    inventory: InventoryAnalysis
    feedback: FeedbackAnalysis
    opportunity: ItemProfitability | None
    signals: tuple[ReadinessSignal, ...]


def build_capstone(data_dir: str | Path, scenario: ForecastScenario) -> CapstoneBriefing:
    """Load one service scenario and call the reusable analyses from Chapters 2–6."""
    root = Path(data_dir)
    restaurant = load_restaurant(root / "james_river_kitchen.json")
    menu_items = load_menu(root / "menu.csv")
    sales = load_sales(root / "menu_sales_july_2026.csv", menu_items)
    menu = analyze_menu(menu_items, sales)

    history = load_demand_history(root / "demand_history_summer_2026.csv")
    reservations = load_reservations(root / "reservations_august_2026.csv", history)
    demand = forecast_demand(history, reservations, scenario,
                             load_forecast_rules(root / "demand_forecast_rules.json"))
    labor = analyze_staffing(
        demand,
        load_schedule(root / "labor_schedule_2026-08-28.csv"),
        load_labor_assumptions(root / "labor_planning_assumptions.json"),
    )

    ingredients = load_ingredients(root / "ingredients.csv")
    recipes = load_recipes(root / "recipes.csv", menu_items, ingredients)
    inventory = analyze_inventory(
        demand, ingredients, recipes,
        load_inventory(root / "inventory_on_hand_2026-08-28.csv", ingredients),
        load_waste(root / "waste_august_2026.csv", ingredients), sales,
    )
    feedback = analyze_feedback(
        load_reviews(root / "customer_feedback_summer_2026.csv"),
        as_of=scenario.target_date,
    )
    opportunity = _menu_opportunity(menu, inventory, recipes)
    signals = generate_signals(demand, labor, inventory, feedback, opportunity)
    return CapstoneBriefing(restaurant, menu, demand, labor, inventory, feedback, opportunity, signals)


def _menu_opportunity(menu: MenuAnalysis, inventory: InventoryAnalysis, recipes) -> ItemProfitability | None:
    comfortable = {row.ingredient.ingredient_id for row in inventory.coverage if row.status == "Comfortable"}
    candidates = []
    for row in menu.items:
        required = {part.ingredient_id for part in recipes if part.menu_item_id == row.item.item_id}
        if row.classification == "Low popularity + high contribution" and required and required <= comfortable:
            candidates.append(row)
    return max(candidates, key=lambda row: (row.contribution_per_sale, row.item.name), default=None)


def generate_signals(demand: DemandForecast, labor: StaffingAnalysis,
                     inventory: InventoryAnalysis, feedback: FeedbackAnalysis,
                     opportunity: ItemProfitability | None) -> tuple[ReadinessSignal, ...]:
    """Apply transparent categorical rules; no score or causal claim is made.

    Rules:
    * A shortage is high priority; a near-threshold count is a watch item.
    * Below-range staffing is high priority when demand is above its weekday baseline.
    * Above-weekday demand + below-range servers + >=50% recent negative wait mentions
      creates an investigation hypothesis, not a statement that staffing caused waits.
    * A low-popularity/high-contribution item whose recipe inputs are all comfortable is
      an opportunity question. Strong recent food-quality sentiment is positive context.
    """
    signals: list[ReadinessSignal] = []
    above_typical = demand.expected_covers > demand.weekday_baseline
    server = next(row for row in labor.roles if row.role == "server")
    shortages = tuple(row for row in inventory.coverage if row.status == "Potential shortage")
    near = tuple(row for row in inventory.coverage if row.status == "Near threshold")
    wait = next(row for row in feedback.trends if row.topic == "wait_time")
    food = next(row for row in feedback.trends if row.topic == "food_quality")

    if above_typical and server.status == "Below":
        signals.append(ReadinessSignal(
            "HIGH PRIORITY", "Review server coverage",
            "Demand above the typical Friday and below-range server coverage could constrain service capacity.",
            (f"Expected covers: {demand.expected_covers} (range {demand.range_low}–{demand.range_high})",
             f"Typical Friday covers: {demand.weekday_baseline:.0f}",
             f"Scheduled servers: {server.scheduled}; planning range: {server.planning_low}–{server.planning_high}"),
            "Is server coverage still appropriate for tonight's forecast?",
        ))
    if shortages or near:
        affected = shortages or near
        priority = "HIGH PRIORITY" if shortages else "WATCH"
        signals.append(ReadinessSignal(
            priority, "Verify high-risk inventory" if shortages else "Verify near-threshold inventory",
            "Physical counts and planning assumptions deserve review before service.",
            tuple(f"{row.ingredient.name}: {row.status}; on hand {row.quantity_on_hand:.2f} {row.ingredient.unit}, "
                  f"planning need {row.planning_need:.2f}" for row in affected),
            "Have these ingredient counts and tonight's prep assumptions been physically verified?",
        ))
    wasted = max(inventory.coverage, key=lambda row: row.waste_cost, default=None)
    if wasted is not None and wasted.waste_cost > 0 and wasted.status == "Comfortable":
        signals.append(ReadinessSignal(
            "WATCH", f"Review {wasted.ingredient.name.lower()} prep",
            "The highest recorded waste-cost ingredient also has comfortable coverage, so additional prep deserves attention.",
            (f"Recorded waste cost: ${wasted.waste_cost:.2f} (highest ingredient total)",
             f"Coverage: {wasted.status}; on hand {wasted.quantity_on_hand:.2f} {wasted.ingredient.unit}",
             f"Planning need: {wasted.planning_need:.2f} {wasted.ingredient.unit}"),
            f"Should {wasted.ingredient.name.lower()} prep be reviewed before preparing more?",
        ))
    if above_typical and server.status == "Below" and wait.recent.negative_share >= .50:
        signals.append(ReadinessSignal(
            "HIGH PRIORITY", "Investigate guest-experience capacity",
            "These connected signals create a reason to investigate capacity; they do not establish that staffing caused wait feedback.",
            (f"Expected covers {demand.expected_covers} exceed typical Friday covers {demand.weekday_baseline:.0f}",
             f"Server coverage: {server.status} ({server.scheduled} scheduled vs. {server.planning_low}–{server.planning_high})",
             f"Recent negative wait-time mentions: {wait.recent.negative}/{wait.recent.mentions} ({wait.recent.negative_share:.0%})"),
            "Should service pacing, walk-in expectations, or capacity assumptions be reviewed?",
        ))
    if opportunity is not None:
        signals.append(ReadinessSignal(
            "OPPORTUNITY", f"Consider {opportunity.item.name}",
            "A strong per-sale contributor with lower historical popularity has comfortable recipe-ingredient coverage.",
            (f"Contribution per sale: ${opportunity.contribution_per_sale:.2f}",
             f"Historical units: {opportunity.units_sold} ({opportunity.classification})",
             "Every recipe ingredient is currently classified Comfortable"),
            f"Would tonight be an appropriate service to feature {opportunity.item.name}?",
        ))
    if food.recent.mentions and food.recent.positive_share >= .75:
        signals.append(ReadinessSignal(
            "POSITIVE", "Protect food-quality strength",
            "Recent written food-quality feedback remains strongly positive.",
            (f"Recent positive food-quality mentions: {food.recent.positive}/{food.recent.mentions} "
             f"({food.recent.positive_share:.0%})", f"Trend classification: {food.direction}"),
            "What must the team protect while responding to tonight's other signals?",
        ))
    return tuple(signals)
