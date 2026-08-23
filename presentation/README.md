# Presentation assets

This directory holds concise presenter support for executable chapters. No separate slide deck is needed; the terminal output and chapter prompts are the presentation aids.

## Chapter 2 live-demo sequence

1. Ask the audience which item they think matters most.
2. Show the sales ranking in the observations.
3. Show the contribution ranking in the table.
4. Highlight why River Burger and Crab Cake Dinner trade places.
5. Ask the audience to predict a $17.50 River Burger scenario.
6. Run `python examples/menu_profitability.py --item river-burger --price 17.50`.
7. Ask how they currently answer this question and which report requires Excel.

## Chapter 3 live-demo sequence

1. Ask the audience how they predict Friday demand.
2. Show the historical Friday rows and explain that a cover means one guest served.
3. Reveal the 174 covers already booked; remind the room that reservations can cancel or no-show.
4. Ask for a quieter/typical/busier prediction and a cover number.
5. Run `python examples/demand_forecast.py`.
6. Explain the weekday, reservation, event, and weather lines before revealing the total.
7. Ask the audience to predict the effect of an event.
8. Run `python examples/demand_forecast.py --event`.
9. Compare 266 with 294 and reinforce **forecast ≠ fact** and the reasonable range.
10. Ask what operational decision they would make next.

Close without answering the bridge to the next chapter: **If we expect about 290 guests, how many people should we schedule?**

## Chapter 4

Use the dedicated [Chapter 4 presenter guide](chapter-04-presenter-guide.md) for the fixed-schedule forecast comparison and transition to Chapter 5.

## Chapter 5

Use the dedicated [Chapter 5 presenter guide](chapter-05-presenter-guide.md) for the sales-to-ingredient chain, demand scenarios, waste-cost analysis, and transition to Chapter 6.
