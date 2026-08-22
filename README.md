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

## Current executable slice

Chapters 0–3 are implemented. The current slice:

- loads one readable JSON configuration for James River Kitchen;
- validates capacity, service periods, categories, channels, and required data sources;
- models the operating flow and the software/data flow; and
- prints a presentation-ready operational briefing;
- analyzes fictional July 2026 menu sales with exact decimal contribution calculations; and
- simulates a menu price without changing source data; and
- forecasts covers and revenue with visible weekday, reservation, event, and weather adjustments and a reasonable range.

It intentionally contains no automated management decisions, external integrations, payments, authentication, machine learning, or web dashboard.

## Implemented

- Introduction
- Restaurant system model
- Menu profitability analysis
- Demand forecasting

## Planned

- Labor planning
- Inventory and food waste
- Customer feedback
- Friday Night Capstone

Planned chapters name future business questions; they are not placeholder features.

## Architecture at a glance

```text
data/james_river_kitchen.json
             ↓
       loader + validation
             ↓
 normalized Restaurant model
             ↓
 presentation-friendly summary
             ↓
examples/restaurant_system.py
```

Chapter 2 adds a parallel, deliberately small path:

```text
data/menu.csv + data/menu_sales_july_2026.csv
                    ↓
         CSV loading + validation
                    ↓
      Decimal profitability analysis
                    ↓
      examples/menu_profitability.py
```

Chapter 3 extends the same validated, presentation-first system:

```text
demand history + reservation snapshots + visible rules
                         ↓
              validated immutable models
                         ↓
        deterministic forecast + explanation
                         ↓
           examples/demand_forecast.py
```

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

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests use only the Python standard library and cover the system foundation, menu profitability, demand/reservation loading, validation, deterministic adjustments, ranges, revenue forecasts, immutable scenarios, and executable output.

## Repository map

```text
chapters/       Presentation-friendly teaching narrative
data/           Fictional, editable restaurant configuration
examples/       Executable presentation entry points
src/            Validated restaurant model and summary behavior
tests/          Behavior-focused standard-library tests
presentation/   Concise presenter support (see its README)
```

Start with [Chapter 0](chapters/00-introduction.md), continue through [Chapter 1](chapters/01-restaurant-system.md) and [Chapter 2](chapters/02-menu-profitability.md), then forecast a busy night in [Chapter 3](chapters/03-demand-forecasting.md).
