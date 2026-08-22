# Chapter 2 — What Actually Makes Money?

Every restaurant, menu item, sale, and cost in this lab is fictional. “Contribution” here means selling price minus estimated ingredient cost—not accounting profit—and excludes labor, occupancy, tax, and other expenses.

### Business question

**Which menu items actually contribute the most value to James River Kitchen?** The operator can see what sells in the POS, but a best seller is not necessarily the strongest contributor after its estimated ingredient cost.

### Predict

Before looking at the result, name the item you expect to lead in units, revenue, contribution per sale, and total contribution. Should one item lead all four measures?

### Inspect the evidence

Open `data/menu.csv`: its 20 rows expose stable IDs, names, categories, prices, and estimated ingredient costs. Then open `data/menu_sales_july_2026.csv`: each readable row is one item's aggregated POS units for July 2026. Calculated values are deliberately absent from both files.

The loader rejects duplicate IDs, malformed money, non-positive prices, negative or excessive ingredient costs, negative units, unknown item references, and ambiguous duplicate sales rows. It does not silently repair source evidence.

### Run

From the repository root:

```bash
python examples/menu_profitability.py
```

### Interpret

For each item the program derives:

```text
revenue                 = units sold × selling price
estimated food cost     = units sold × ingredient cost
contribution per sale   = selling price − ingredient cost
total contribution      = revenue − estimated food cost
contribution margin %   = contribution per sale ÷ selling price
```

Money uses decimal arithmetic. Margin division is safe when aggregate revenue is zero. Contribution measures what remains after this one estimated variable cost; it is **not profit**.

The four menu-engineering descriptions use two visible thresholds: “high popularity” means units at or above mean units per menu item, and “high contribution” means contribution per sale at or above the menu mean. These simple workshop quadrants are not presented as a universal consulting standard.

### Break the assumption

River Burger sells the most units, yet Crab Cake Dinner generates more total contribution. Virginia Beef Tenderloin has the strongest contribution per sale but relatively low volume. Volume, price, and cost work together; a sales ranking alone cannot show that.

### Change one input

Predict first: if River Burger moves from $16.00 to $17.50 while its cost and 610-unit volume remain fixed, what happens to contribution per sale, total contribution, and margin?

```bash
python examples/menu_profitability.py --item river-burger --price 17.50
```

The simulation labels its assumptions and creates a new in-memory menu; it never edits either CSV. In real operations, volume might respond to price, so the fixed-volume result is evidence about the assumption—not a forecast.

### Business implication

An operator might test a price adjustment, renegotiate an ingredient cost, reconsider a portion, promote a high-contribution item, or investigate why a strong item sells poorly. The output identifies useful questions. It cannot know guest expectations, kitchen complexity, competitive context, or the restaurant's strategy. Data informs operator judgment; it does not replace it.

## Ask a Restaurant Operator

- Which menu items do you believe make the most money?
- Can your current POS show contribution after estimated food cost?
- How often are recipe or ingredient costs updated?
- Which popular items have become expensive to produce?
- Are there high-margin items you wish customers ordered more often?
- How do you decide when to raise a menu price?
- Which reports currently require exporting data to Excel?
