# Workshop cheat sheet

**Fictional scenario:** James River Kitchen — Friday, August 28, 2026.  
**Preflight:** `python examples/demo_check.py`  
**Guided run:** `python examples/workshop.py`

| Order | Command | Major result (avoid brittle numbers) | Ask |
|---:|---|---|---|
| 1 | `python examples/restaurant_system.py` | Five systems describe one operation. | What question crosses systems? |
| 2 | `python examples/menu_profitability.py` | Best seller differs from contribution leader. | Does volume equal value? |
| 3 | `python examples/demand_forecast.py` | Reservations adjust, but do not equal, demand. | How do you estimate Friday? |
| 4 | `python examples/labor_planning.py` | Role coverage can differ from total headcount. | Which role constrains service? |
| 5 | `python examples/inventory_waste.py` | Demand changes ingredient coverage signals. | What do you recount first? |
| 6 | `python examples/customer_feedback.py` | Guest symptoms prompt investigation, not diagnosis. | What can a review prove? |
| 7 | `python examples/friday_night_capstone.py --explain` | Connected evidence creates traceable questions. | What would you inspect first? |

**High demand:** `python examples/friday_night_capstone.py --reservations 210 --event --weather clear`  
**Lower demand:** `python examples/friday_night_capstone.py --reservations 120 --weather storms`  
**Full rehearsal:** `python examples/workshop.py --no-pause`  
**Rerun/recover:** `clear`; `python examples/demo_check.py`; `python examples/friday_night_capstone.py`  
**Tests:** `python -m unittest discover -s tests -v`

**Close:** “Which of these signals requires you to combine multiple systems manually today?”
