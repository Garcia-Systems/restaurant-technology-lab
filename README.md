# Restaurant Technology Lab

**Restaurant Technology Lab** is a compact, presentation-first Python simulation about getting more business value from restaurant data. Its fictional business, **James River Kitchen**, is an independent Williamsburg, Virginia restaurant serving seasonal Virginia comfort food.

> Keep the systems you already use. This lab demonstrates what becomes possible when their data is connected, normalized, analyzed, and turned into business decisions.

The lab complements POS, reservation, scheduling, inventory, and review software; it does **not** attempt to replace those products. It gives restaurant operators and technical audiences a shared, executable way to discuss the questions that fall between them.

## Audience

- Restaurant owners, managers, and hospitality professionals
- Employers and technical hiring teams
- Sales and solutions engineers leading discovery conversations
- Developers learning to connect implementation choices to business evidence

All restaurants, operating details, and business data in this repository are **fictional**. James River Kitchen is not a real restaurant.

## Version 1 — complete

Chapters 0–7 are implemented. The completed Version 1:

- loads one readable JSON configuration for James River Kitchen;
- validates capacity, service periods, categories, channels, and required data sources;
- models the operating flow and the software/data flow; and
- prints a presentation-ready operational briefing;
- analyzes fictional July 2026 menu sales with exact decimal contribution calculations; and
- simulates a menu price without changing source data; and
- forecasts covers and revenue with visible weekday, reservation, event, and weather adjustments and a reasonable range; and
- compares a fictional Friday schedule with forecast-driven role ranges and transparent labor cost; and
- connects POS sales, simplified recipes, a physical count, the Chapter 3 forecast, and waste records to ingredient planning signals and financial impact; and
- turns fictional guest feedback into inspectable topic, polarity, and time-window signals with deterministic phrase rules; and
- orchestrates those analyses into one traceable Friday briefing with categorical cross-functional signals.

It intentionally contains no automated management decisions, external integrations, payments, authentication, machine learning, or web dashboard.

## Implemented

- Introduction
- Restaurant system model
- Menu profitability analysis
- Demand forecasting
- Labor planning
- Inventory and food waste
- Customer feedback
- Friday Night Capstone

## Completed architecture at a glance

```text
 Restaurant config        Menu + sales       Demand + reservations       Reviews
        |                       |                       |                    |
 validated Restaurant     analyze_menu()          forecast_demand()    analyze_feedback()
                                |                       |
                                |              +--------+--------+
                                |              |                 |
                                |       analyze_staffing()  analyze_inventory()
                                |              |                 |
                                +--------------+-----------------+
                                               |
                                        build_capstone()
                                               |
                                      CapstoneBriefing result
                                               |
                                        format_capstone()
```

`build_capstone()` is orchestration, not a second calculation path. Chapter 4 and Chapter 5 retain the same `DemandForecast`; the menu opportunity combines Chapter 2's classification with Chapter 5's ingredient coverage; cross-signals use Chapter 6's structured trends. Business logic returns structured immutable results before terminal formatting.

The restaurant itself has a parallel operational flow:

```text
Guest → Reservation or Order → Kitchen / Service → Inventory
      → Labor → Payment / POS → Business results
```

The model is deliberately small: immutable Python dataclasses establish reusable contracts, JSON keeps the fictional inputs visible during a presentation, and the standard library keeps setup friction low.

## Setup

Requirements: Python 3.10 or newer. No third-party packages are required.

```bash
git clone <repository-url>
cd restaurant-technology-lab
```

## Run the operational briefing

From the repository root:

```bash
python examples/restaurant_system.py
```

The example locates `src/` and `data/` relative to its own file, so it needs no installation step.

## Run the menu profitability analysis

```bash
python examples/menu_profitability.py
```

Simulate a $17.50 River Burger price at unchanged sales volume (the source CSV remains unchanged):

```bash
python examples/menu_profitability.py --item river-burger --price 17.50
```

## Run the demand forecast

Run the default Friday, August 28, 2026 scenario:

```bash
python examples/demand_forecast.py
```

Compare the default with a local-event scenario:

```bash
python examples/demand_forecast.py --event
```

Compare the default with rain and 190 booked covers:

```bash
python examples/demand_forecast.py --weather rain --reservations 190
```

## Run the labor planning analysis

Default fixed-schedule comparison:

```bash
python examples/labor_planning.py
```

Lower-demand comparison:

```bash
python examples/labor_planning.py --weather rain --reservations 100
```

Higher-demand event comparison:

```bash
python examples/labor_planning.py --event --reservations 210
```

These are fictional James River Kitchen assumptions, not industry standards. The result is a planning signal—not automatic scheduling, payroll, compliance, or a personnel recommendation.

## Run the inventory and food-waste analysis

```bash
python examples/inventory_waste.py
python examples/inventory_waste.py --weather rain --reservations 100
python examples/inventory_waste.py --event --reservations 210
python examples/inventory_waste.py --ingredient-cost rockfish-fillet=12.00
```

These menu-mix, recipe, count, 10% buffer, cost, and waste assumptions are fictional. Results are planning signals—not guaranteed requirements, automated purchasing, or purchase orders. Chapter 5 consumes Chapter 3's forecast and reconciles recipe-derived costs with Chapter 2.

## Run the customer-feedback analysis

Run the default comparison of two adjacent 30-day windows:

```bash
python examples/customer_feedback.py
```

Trace the wait-time or online-ordering summary to the original fictional evidence:

```bash
python examples/customer_feedback.py --topic wait_time
python examples/customer_feedback.py --topic online_ordering
```

Compare shorter aggregation windows without changing source data:

```bash
python examples/customer_feedback.py --period-days 14
python examples/customer_feedback.py --period-days 7
```

All review text is original fictional demonstration data. The method uses visible phrases and a documented directional threshold—not external review APIs, scraping, AI, machine learning, or a production sentiment system. A customer signal describes an experience and suggests where to investigate; it does not establish operational root cause.

## Run the Friday Night Capstone

Run the concise default Friday, August 28, 2026 readiness briefing:

```bash
python examples/friday_night_capstone.py
```

Trace every conclusion to its structured evidence and management question:

```bash
python examples/friday_night_capstone.py --explain
```

Show how one demand assumption propagates through labor, inventory, menu, and customer-experience signals:

```bash
python examples/friday_night_capstone.py --reservations 210 --event --weather clear
python examples/friday_night_capstone.py --reservations 120 --weather storms
```

The capstone calls the Chapters 2–6 analysis functions; it does not copy their formulas. Priorities are categorical and documented, source data is never edited, and connected evidence generates hypotheses rather than automatic operating decisions.

## 45–60 Minute Workshop Path

| Time | Conversation | Executable command |
|---:|---|---|
| 5 min | Restaurant and systems | `python examples/restaurant_system.py` |
| 7 min | Menu profitability | `python examples/menu_profitability.py` |
| 7 min | Demand forecast | `python examples/demand_forecast.py` |
| 7 min | Labor planning | `python examples/labor_planning.py` |
| 7 min | Inventory and waste | `python examples/inventory_waste.py` |
| 6 min | Customer feedback | `python examples/customer_feedback.py` |
| 10–12 min | Friday capstone, evidence trace, scenario change, and discussion | `python examples/friday_night_capstone.py --explain` |

The path takes roughly 49–51 minutes before optional audience discussion. The presenter guides in `presentation/` provide prompts rather than a separate slide deck.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests use only the Python standard library and cover the system foundation, menu profitability, demand forecasting, labor, inventory and waste, feedback loading and validation, deterministic classification, mixed topics, aggregation, trend windows, non-mutating scenarios, and executable output.

## Repository map

```text
chapters/       Presentation-friendly teaching narrative
data/           Fictional, editable restaurant configuration
examples/       Executable presentation entry points
src/            Validated restaurant model and summary behavior
tests/          Behavior-focused standard-library tests
presentation/   Concise presenter support (see its README)
```

Start with [Chapter 0](chapters/00-introduction.md), continue through [Chapter 1](chapters/01-restaurant-system.md) and [Chapter 2](chapters/02-menu-profitability.md), forecast a busy night in [Chapter 3](chapters/03-demand-forecasting.md), connect that forecast to labor in [Chapter 4](chapters/04-labor-planning.md), trace demand into inventory and waste in [Chapter 5](chapters/05-inventory-waste.md), turn guest language into evidence in [Chapter 6](chapters/06-customer-feedback.md), and combine the signals in [Chapter 7](chapters/07-friday-night-capstone.md).

## Possible Future Experiments

- adapters for real CSV export shapes;
- a richer but still explainable demand model;
- an anonymized real-business pilot; or
- an optional presentation dashboard over the same structured results.

These are possible experiments, not Version 1 features or commitments.
