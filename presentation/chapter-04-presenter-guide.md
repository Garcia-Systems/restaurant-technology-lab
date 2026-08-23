# Chapter 4 Presenter Guide — Labor vs. Demand

## Live sequence

1. Recap Chapter 3's 266-cover forecast and 239–293 range.
2. Show `data/labor_schedule_2026-08-28.csv` as readable evidence, not an optimized assignment.
3. Ask whether 22 employees look sufficient; invite role-specific predictions.
4. Run `python examples/labor_planning.py`.
5. Reveal the ranges and server signal; open the assumption JSON so the arithmetic remains contestable.
6. Discuss what management would investigate rather than prescribe a shift change.
7. Run `python examples/labor_planning.py --event --reservations 210`.
8. Point out that the same schedule is now compared with 326 covers; server and cook signals are below range.
9. If time permits, run `python examples/labor_planning.py --weather rain --reservations 100`.
10. Ask what changed, what did not, and which evidence management would seek next.

## Emphasis

- Say: **“The schedule didn't change. Our understanding of demand did.”**
- Call every ratio a **James River Kitchen planning assumption**, never an industry standard.
- “Below” and “above” identify attention areas, not directives.
- Timing, party size, layout, experience, service style, menu complexity, absences, guest behavior, and labor rules remain outside the formula.
- A bad Chapter 3 forecast creates a bad staffing premise.

## Transition

> **Even if we have enough people, do we have enough food—and how much are we wasting?**

That is Chapter 5's question. Do not answer it here.
