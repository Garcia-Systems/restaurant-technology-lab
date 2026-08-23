# Chapter 7 Presenter Guide — Friday Night Capstone

## Purpose

Finish with one operating conversation, not five dashboards. Keep asking the audience to distinguish evidence from a management decision. Allow 10–12 minutes.

## Live sequence

1. Put Friday, August 28, 2026 and the base scenario on screen.
2. Ask the audience what they would check first.
3. Run `python examples/demand_forecast.py` and reveal the demand range.
4. Run `python examples/labor_planning.py` and reveal labor alignment.
5. Run `python examples/inventory_waste.py` and reveal inventory risks.
6. Run `python examples/menu_profitability.py` and ask what makes an opportunity credible.
7. Run `python examples/customer_feedback.py` and reveal experience evidence.
8. Run `python examples/friday_night_capstone.py` for the integrated briefing.
9. Add `--explain`; walk through the guest-experience cross-signal and causal caveat.
10. Run `python examples/friday_night_capstone.py --reservations 210 --event`.
11. Show how demand, labor, inventory, and questions change while schedules and counts stay fixed.
12. Optionally contrast `python examples/friday_night_capstone.py --reservations 120 --weather storms`.
13. Ask the audience what they would do—and emphasize that software stopped before the decision.

## The cross-signal reveal

Write these inputs separately: above-typical expected demand; below-range server coverage; a high recent negative share among wait-time mentions. Then reveal the hypothesis: service capacity deserves investigation. Say explicitly that the evidence does **not** establish that staffing caused historical wait feedback.

Use `--explain` to trace the result to forecast covers and range, scheduled and planned servers, and recent classified wait-time mentions. An inspectable rule earns a business conversation.

## Final workshop move

Ask the restaurant operators in the room **which of these questions is hardest for their own systems to answer**. That moves the conversation from demonstration to discovery without prescribing their operation.
