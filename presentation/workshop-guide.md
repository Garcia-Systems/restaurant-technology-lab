# Restaurant Technology Lab Workshop

## Audience and objective

Suitable for restaurant owners and managers, hospitality operators, business leaders,
software professionals, and sales/solutions engineering audiences.

By the end, participants should understand:

> How disconnected restaurant data can become operational signals without replacing the
> restaurant's existing systems.

All restaurant details and data are fictional. The primary scenario is **Friday, August 28,
2026**. July sales and earlier summer demand are historical inputs; the schedule and physical
count are August 28 snapshots; feedback is considered only through the scenario date.

## Before the room arrives

```bash
python examples/demo_check.py
python examples/workshop.py --no-pause
```

Use `python examples/workshop.py` as the primary guided entry point. It pauses between the
existing examples; it does not reimplement their calculations.

## 45–60 minute timing

| Section | Minutes |
|---|---:|
| Opening and restaurant story | 4 |
| Restaurant as a system | 5 |
| Menu profitability | 6 |
| Demand forecasting | 7 |
| Labor planning | 6 |
| Inventory and waste | 7 |
| Customer feedback | 6 |
| Friday Night Capstone and scenario | 9 |
| Discovery discussion | 5 |
| **Total** | **55** |

## Presenter prompts

### Opening
- **Objective:** begin with a recognizable restaurant, not architecture.
- **Run:** `python examples/workshop.py`
- **Ask first:** “Which operating question forces you to open more than one system?”
- **Notice/result:** this lab connects evidence but stops before management decisions.
- **Transition:** “First, where does restaurant work become data?”

### Restaurant as a System
- **Objective:** establish operating and information flows.
- **Run individually:** `python examples/restaurant_system.py`
- **Ask first:** “Where does a guest interaction first become data?”
- **Notice/result:** five familiar systems hold different pieces of one service.
- **Transition:** “Once sales arrive, which items contribute value rather than merely volume?”

### Menu Profitability
- **Objective:** separate sales volume from contribution after estimated ingredient cost.
- **Run:** `python examples/menu_profitability.py`
- **Ask first:** “Does your best seller necessarily contribute the most?”
- **Notice/result:** the unit leader and total-contribution leader differ.
- **Transition:** “We know what sold historically, but not how busy this Friday will be.”

### Demand Forecasting
- **Objective:** show an inspectable planning assumption, not certainty.
- **Run:** `python examples/demand_forecast.py`
- **Ask first:** “How many guests do you expect before the doors open?”
- **Notice/result:** reservations are only one visible adjustment to historical demand.
- **Transition:** “If that estimate is reasonable, what does it mean for the people scheduled?”

### Labor Planning
- **Objective:** compare one fixed schedule with forecast-driven role ranges.
- **Run:** `python examples/labor_planning.py`
- **Ask first:** “Does the total headcount tell you whether each role is aligned?”
- **Notice/result:** server coverage deserves attention in the base scenario.
- **Transition:** “Enough people does not answer whether enough food is available.”

### Inventory and Waste
- **Objective:** connect menu mix, recipes, counts, forecast, and recorded waste.
- **Run:** `python examples/inventory_waste.py`
- **Ask first:** “Which count becomes risky only after expected demand changes?”
- **Notice/result:** coverage labels prompt recounting and investigation, not purchasing.
- **Transition:** “The internal numbers are visible; what did guests experience?”

### Customer Feedback
- **Objective:** make guest themes inspectable without claiming a root cause.
- **Run:** `python examples/customer_feedback.py`
- **Ask first:** “Can reviews tell you why a wait occurred, or only that it was experienced?”
- **Notice/result:** wait-time and food-quality evidence provide questions for earlier analyses.
- **Transition:** “Bring every signal into one Friday-afternoon conversation.”

### Friday Night Capstone
- **Objective:** connect evidence while keeping management judgment visible.
- **Run:** `python examples/friday_night_capstone.py --explain`
- **Ask first:** “What would you inspect first at 3:00 PM?”
- **Notice/result:** cross-signals are traceable hypotheses; none is an automatic decision.
- **Scenario:** `python examples/friday_night_capstone.py --reservations 210 --event --weather clear`
- **Transition:** “Which part of this briefing is hardest to assemble in your operation?”

## Discovery close

Choose six or seven, not all: Which questions can current systems answer? Which require Excel?
Which require combining reports? What does Friday-afternoon management look like? Which problem
is discovered too late? What information is separated? Which alert would help rather than add
noise? If one operational question could be answered instantly, what would it be?

## 15-minute path

1. Introduce the fictional restaurant (1 minute).
2. `python examples/restaurant_system.py` (2 minutes).
3. `python examples/demand_forecast.py` (3 minutes).
4. `python examples/labor_planning.py` (3 minutes).
5. `python examples/friday_night_capstone.py --explain` (4 minutes).
6. Ask which signal currently requires manual report combination (2 minutes).

## Five-minute elevator demo

State the restaurant and boundary, then run `python examples/friday_night_capstone.py`. Point to
one cross-signal. Run `python examples/friday_night_capstone.py --reservations 210 --event` and
show that one demand assumption changes downstream questions while source files do not change.
Close with: “Which of these signals would require you to combine multiple systems manually?”

## Failure recovery

```bash
python examples/demo_check.py
python -m unittest discover -s tests -v
clear
python examples/friday_night_capstone.py
```

If one detailed example is too noisy, clear the terminal and use the concise capstone. If a live
run cannot be recovered, use the expected qualitative results in this guide and keep the business
conversation moving. No internet connection is required.
