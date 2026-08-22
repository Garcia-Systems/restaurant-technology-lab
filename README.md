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

Chapters 1–2 (numbered `00`–`01` in the repository) are implemented. The current slice:

- loads one readable JSON configuration for James River Kitchen;
- validates capacity, service periods, categories, channels, and required data sources;
- models the operating flow and the software/data flow; and
- prints a presentation-ready operational briefing.

It intentionally contains no analytics, forecasts, recommendations, external integrations, payments, authentication, machine learning, or web dashboard yet.

## Version 1 roadmap

1. **Introduction — Meet James River Kitchen** — implemented
2. **The Restaurant as a System** — implemented
3. **What Actually Makes Money? — Menu Profitability** — planned
4. **Predicting a Busy Night — Demand Forecasting** — planned
5. **Labor vs. Demand — Staffing** — planned
6. **Inventory and Food Waste** — planned
7. **What Customers Are Telling You — Customer Feedback** — planned
8. **Friday Night Capstone** — planned

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

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests use only the Python standard library and cover loading, required systems, invalid inputs, readable output, and execution from a clean repository root.

## Repository map

```text
chapters/       Presentation-friendly teaching narrative
data/           Fictional, editable restaurant configuration
examples/       Executable presentation entry points
src/            Validated restaurant model and summary behavior
tests/          Behavior-focused standard-library tests
presentation/   Future presentation assets (see its README)
```

Start with [Chapter 0](chapters/00-introduction.md), then use [Chapter 1](chapters/01-restaurant-system.md) for the first guided exercise.
