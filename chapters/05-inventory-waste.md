# Chapter 5 — Inventory and Food Waste

Every ingredient, simplified recipe, count, cost, and waste event is **fictional**. This is explainable decision support—not a production inventory system or an industry standard.

### Business question

**Do we have enough ingredients for expected demand, and where are we losing money?**

### Predict

The current count includes 11.14 rockfish fillets, 21.17 crab-cake portions, and 17.53 pounds of ground beef. Chapter 3 forecasts 266 covers (a reasonable range of 239–293). Before running, which ingredients do you expect to be risky? Remember that stock alone cannot answer the question.

### Inspect the evidence

- `menu_sales_july_2026.csv` supplies historical POS units.
- `recipes.csv` connects every existing menu item to a deliberately simplified operational ingredient quantity.
- `ingredients.csv` supplies stable ingredient IDs, small consistent units, and Decimal unit costs.
- `inventory_on_hand_2026-08-28.csv` is one physical-count snapshot.
- `waste_august_2026.csv` records quantities and only the stated reasons: spoilage, prep waste, overproduction, or damage.

The mappings are fictional consumption assumptions, not real recipes. Their derived component costs reconcile to Chapter 2's menu ingredient costs, so this chapter explains those existing estimates rather than creating a competing menu.

### Run

```bash
python examples/inventory_waste.py
```

### Interpret

July item units are divided by all July item units to form the **estimated menu mix**. For this compact simulation, one forecast cover corresponds to one expected menu-item unit distributed across that mix. This simplifying assumption is transparent; real guest checks often contain multiple items.

```text
expected item units = Chapter 3 forecast covers × historical item share
expected ingredient usage = expected item units × recipe quantity
planning need = expected ingredient usage × 1.10
inventory value = quantity on hand × unit cost
waste cost = recorded waste quantity × unit cost
```

The 10% buffer is a configurable, fictional James River Kitchen planning assumption—not an industry recommendation. **Potential shortage** means stock is below buffered planning need. **Near threshold** means stock covers buffered need but has less than one additional 10%-of-usage cushion. Otherwise the signal is **Comfortable**.

The default run flags crab cake, rockfish, and fried-oyster po-boy portions near threshold. It calculates $240.10 of recorded August waste; ground beef has the highest recorded waste cost at $77.00. These facts do not establish why waste occurred beyond the recorded reasons.

### The connected teaching moment

```text
POS sale
   ↓
Menu item
   ↓
Recipe
   ↓
Ingredient usage
   ↓
Inventory
   ↓
Financial consequence
```

A sale is not just revenue. POS data becomes operational inventory evidence once the sold menu item is connected to its recipe.

### Change demand

Predict the risk change, then reuse Chapter 3's real scenario inputs:

```bash
python examples/inventory_waste.py --weather rain --reservations 100
python examples/inventory_waste.py --event --reservations 210
```

### Run again

The lower scenario forecasts 176 covers. The higher scenario forecasts 326 and produces 14 potential-shortage signals. The physical count did not change; the demand assumption changed, which changed the risk assessment. These are potential shortages, not guaranteed usage or purchase orders.

### Change cost

Keep rockfish waste quantity fixed while simulating a unit-cost increase in memory:

```bash
python examples/inventory_waste.py --ingredient-cost rockfish-fillet=12.00
```

Five wasted fillets remain five; their calculated cost changes from $49.00 to $60.00. No CSV is edited.

### Business implication

An operator might recount inventory, adjust prep quantities, review purchasing, investigate recurring spoilage, reconsider a special, or verify recipe assumptions. The analysis makes those conversations timely; it does not decide or buy anything automatically.

## Ask a Restaurant Operator

- How do you currently know what ingredients are likely to run short?
- How often is inventory physically counted?
- Does your POS connect menu sales to ingredient consumption?
- Which ingredients create the most waste?
- How is food waste recorded today?
- Do you know the dollar value of discarded product?
- Which ingredients have become significantly more expensive?
- How do you decide how much to prep before service?
- Do managers use spreadsheets to reconcile sales, recipes, and inventory?
- What inventory problem causes the most operational stress?
- How early would a shortage warning need to arrive to be useful?
