# The Restaurant as a System

A restaurant is both a flow of hospitality work and a collection of software boundaries. James River Kitchen's executable model gives us one shared picture of both.

## Business question

**What must be connected before a manager can explain what happened during a service?**

The answer should be useful to an operator—not merely a list of applications.

## Inspect the evidence

Open `data/james_river_kitchen.json`. It is the actual input used by the example. Look for:

- identity, location, capacity, and operating periods;
- menu categories and sales channels; and
- five source identifiers: `pos`, `reservations`, `scheduling`, `inventory`, and `reviews`.

The loader in `src/restaurant_lab/loader.py` converts that visible input into the contracts in `model.py`. The model rejects impossible hours, non-positive capacity, empty categories, duplicate source identifiers, and a missing required source. This matters because decisions built on malformed inputs only look precise.

## Make a prediction

Before running anything, predict the opening lines:

- What capacity will appear?
- Which services will be listed?
- Which systems contribute evidence?

Then predict the two different flows. The operating business is:

```text
Guest → Reservation or Order → Kitchen / Service → Inventory
      → Labor → Payment / POS → Business results
```

The software/data path is:

```text
POS  Reservations  Scheduling  Inventory  Reviews
                       ↓
               Import / adapters
                       ↓
          Normalized restaurant data
                       ↓
          Analytics / business rules
                       ↓
          Recommendations / alerts
```

## Run the simulation

From the repository root:

```bash
python examples/restaurant_system.py
```

## Interpret the result

The output is an operational briefing, not a Python object dump. Notice what it can and cannot claim:

- It **can** establish what James River Kitchen is, when it serves guests, and which evidence sources exist.
- It **can** show where normalization and future business rules belong.
- It **cannot yet** calculate profit, forecast demand, recommend staffing, estimate waste, or interpret reviews.

That honesty is a design feature. Later chapters can add one decision at a time without pretending that an application name is the same as a business answer.

## Change one input and run again

Try one safe, reversible exercise:

1. In `data/james_river_kitchen.json`, change `"capacity": 120` to `"capacity": 124`.
2. Predict exactly which briefing line will change.
3. Run `python examples/restaurant_system.py` again.
4. Confirm that it now says `Capacity: 124 guests`.
5. Restore the value to `120` so the shared fictional scenario stays consistent.
6. Run `python -m unittest discover -s tests -v` to verify the restored baseline.

## Discuss the business implication

Changing capacity alters the declared operating constraint but does not manufacture sales, reservations, or staffing conclusions. A future question such as “Can we accept another large party?” would need capacity **plus** reservation timing and table availability. A reliable contract makes missing evidence explicit.

For a second discussion, consider why the model refuses to load if `reviews` is removed. “Required” does not mean every decision uses every system. It means the Version 1 lab promises a coherent evidence landscape, and missing evidence should be visible rather than silently ignored.

## Ask a Restaurant Operator

- Where does a guest interaction first become data in your restaurant?
- Which restaurant systems do you use today?
- Which reports require manual spreadsheet work?
- Which systems do you wish shared information automatically?
- What operational question is hardest to answer quickly?
- What information do you wish your POS showed you but does not?
