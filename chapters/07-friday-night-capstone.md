# Chapter 7 — Friday Night at James River Kitchen

### 3:00 PM — The Question

It is Friday, August 28, 2026. Tonight is expected to be busy. Reservations, weather, the local-event flag, the unchanged labor schedule, the physical inventory count, recent waste, July menu sales, and recent fictional reviews are available—but they live in different evidence paths.

**What should management inspect before service?** The capstone does not introduce a sixth dashboard or recommendation engine. It orchestrates the structured results already produced by Chapters 2–6.

### Start with demand

```bash
python examples/demand_forecast.py
```

The Chapter 3 forecast provides expected covers, a reasonable range, revenue, and visible adjustments. It remains a planning assumption rather than knowledge of the future.

### Add labor

```bash
python examples/labor_planning.py
```

Chapter 4 consumes that forecast and compares its range with the unchanged schedule. It does not independently forecast covers or make a personnel decision.

### Add inventory

```bash
python examples/inventory_waste.py
```

Chapter 5 uses the same forecast, historical menu mix, recipes, physical counts, a visible buffer, and waste records. “Near threshold” and “Potential shortage” are prompts to recount and inspect—not purchase orders.

### Add menu economics

```bash
python examples/menu_profitability.py
```

Chapter 2 distinguishes popularity, contribution per sale, and total contribution. Here, a possible opportunity must have lower historical popularity, high contribution per sale, and comfortable coverage for every recipe ingredient. It is a question, not an instruction to promote or discount an item.

### Add the customer voice

```bash
python examples/customer_feedback.py
```

Chapter 6 reports written experience signals. A high share of negative wait-time mentions can be considered beside demand and staffing, but it cannot prove why guests waited. Positive food-quality evidence remains a strength worth protecting.

### Combine the evidence

```bash
python examples/friday_night_capstone.py
python examples/friday_night_capstone.py --explain
```

The first command keeps the live briefing concise. `--explain` prints each signal's interpretation, source metrics, and management question so a presenter can answer, “Where did that come from?”

The transparent rules are:

1. Forecast demand above the historical Friday baseline plus below-range server coverage is **high priority**.
2. A potential ingredient shortage is **high priority**; near-threshold inventory is a **watch** item.
3. If the ingredient with the highest recorded waste cost also has comfortable coverage, additional prep is a **watch** question.
4. Above-typical demand plus below-range servers plus at least 50% recent negative wait-time mentions creates a **guest-experience investigation hypothesis**. It does not assert causation.
5. A lower-popularity/high-contribution item whose recipe ingredients are all comfortable is an **opportunity** question.
6. At least 75% positive recent food-quality mentions is **positive** context worth protecting.

These categories are intentionally plain: **high priority** can affect tonight; **watch** deserves review; **opportunity** describes possible upside; **positive** preserves useful context. There is no opaque score.

### Change one assumption

```bash
python examples/friday_night_capstone.py --reservations 210 --event --weather clear
```

### Run again

```bash
python examples/friday_night_capstone.py --reservations 120 --weather storms
```

The fixed schedule and counts do not change. Expected covers do, so labor alignment, inventory coverage, the menu opportunity, and cross-functional signals can change downstream. One assumption propagates while source evidence remains untouched.

### Interpret

```text
DATA
What happened or what exists.

SIGNAL
Something in that evidence worth noticing.

HYPOTHESIS
A possible explanation or consequence to investigate.

DECISION
What management chooses to do after adding judgment and local context.
```

For example:

```text
DATA
Server planning range is 8–10. Seven servers are scheduled.

SIGNAL
Server coverage is below the modeled range.

HYPOTHESIS
Service capacity could be strained if demand reaches the forecast.

DECISION
A manager decides whether any staffing or pacing change is appropriate.
```

The software stops before the decision. It creates traceable questions and earlier warnings without pretending correlation is cause or a model is operator judgment.

## Ask a Restaurant Operator

- Which of these signals can your current systems already provide?
- Which require managers to combine information manually?
- What does your Friday-afternoon management routine look like?
- Which operational surprises are most expensive?
- Which problems do you usually discover too late?
- Which reports do managers open before a busy service?
- What information exists in separate systems today?
- Where are spreadsheets used to connect those systems?
- Which alert would actually be useful before service?
- Which alert would just create noise?
- If you could answer one operational question instantly, what would it be?

> The purpose of this lab is not to prescribe restaurant operations. It is to demonstrate how disconnected operational data can become better questions, earlier warnings, and more informed decisions.
