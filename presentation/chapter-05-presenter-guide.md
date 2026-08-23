# Chapter 5 Presenter Guide — Inventory and Food Waste

All evidence is fictional. Aim for 8–10 minutes; keep the operator's judgment—not the table—as the focus.

1. Recap Chapter 3's 266-cover demand forecast.
2. Show the current inventory CSV and ask which ingredient looks risky.
3. Trace one River Burger sale through its 0.5-pound ground-beef mapping.
4. Run `python examples/inventory_waste.py` and reveal the coverage signals.
5. Explain the historical sales mix, one-item-per-cover simplification, and fictional 10% buffer.
6. Run `python examples/inventory_waste.py --event --reservations 210`.
7. Emphasize: the count stayed fixed; changed demand changed risk.
8. Reveal the calculated waste-cost ranking without inventing causes.
9. Run `python examples/inventory_waste.py --ingredient-cost rockfish-fillet=12.00`; quantity stays fixed while financial impact changes.
10. Ask how the restaurant currently reconciles POS sales, recipes, counts, and waste.

Avoid “exact requirement,” “guaranteed shortage,” and “should order.” Prefer “estimated menu mix,” “planning quantity,” and “potential shortage.”

Transition to Chapter 6:

> **We can measure what happens inside the restaurant. But what are customers telling us about their experience?**
