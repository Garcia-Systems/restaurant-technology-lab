"""Presentation formatter for the Friday capstone structured result."""

from .capstone import CapstoneBriefing, PRIORITIES


def format_capstone(briefing: CapstoneBriefing, *, explain: bool = False) -> str:
    demand, labor, inventory, feedback = briefing.demand, briefing.labor, briefing.inventory, briefing.feedback
    server = next(row for row in labor.roles if row.role == "server")
    status_counts = {status: sum(row.status == status for row in inventory.coverage)
                     for status in ("Potential shortage", "Near threshold", "Comfortable")}
    wait = next(row for row in feedback.trends if row.topic == "wait_time")
    food = next(row for row in feedback.trends if row.topic == "food_quality")
    line = "=" * 62
    sections = [
        briefing.restaurant.name,
        "Friday Night Readiness Briefing",
        demand.scenario.target_date.strftime("%A, %B %d, %Y"), "", line,
        "1. DEMAND", line,
        f"Reservations booked: {demand.scenario.reservations_booked}",
        f"Expected covers:     {demand.expected_covers} ({demand.range_low}–{demand.range_high})",
        f"Expected revenue:    ${demand.expected_revenue:,.2f}",
        f"Signal: {'BUSIER THAN TYPICAL' if demand.expected_covers > demand.weekday_baseline else 'AT OR BELOW TYPICAL'}",
        "", line, "2. LABOR", line,
        f"Server coverage: {server.status.upper()} — {server.scheduled} scheduled; planning range {server.planning_low}–{server.planning_high}",
        "Other roles: " + ", ".join(f"{row.role} {row.status.lower()}" for row in labor.roles if row.role != "server"),
        "", line, "3. INVENTORY + WASTE", line,
        f"Potential shortages: {status_counts['Potential shortage']}",
        f"Near threshold:      {status_counts['Near threshold']}",
        f"Comfortable:         {status_counts['Comfortable']}",
        f"Recorded waste cost: ${inventory.total_waste_cost:,.2f}",
        "", line, "4. MENU OPPORTUNITY", line,
        (f"{briefing.opportunity.item.name}: ${briefing.opportunity.contribution_per_sale:.2f} contribution per sale; "
         "comfortable recipe coverage" if briefing.opportunity else "No item meets the transparent opportunity rule."),
        "", line, "5. CUSTOMER EXPERIENCE", line,
        f"Wait-time negative mentions (recent): {wait.recent.negative}/{wait.recent.mentions} — trend {wait.direction.lower()}",
        f"Food-quality positive mentions (recent): {food.recent.positive}/{food.recent.mentions}",
        "Customer signals describe experience; they do not establish operational cause.",
        "", line, "TONIGHT'S READINESS", line,
    ]
    for priority in PRIORITIES:
        rows = [signal for signal in briefing.signals if signal.priority == priority]
        if rows:
            sections.extend((priority, *(f"- {row.title}" for row in rows), ""))
    sections.append("QUESTIONS FOR MANAGEMENT")
    sections.extend(f"- {signal.management_question}" for signal in briefing.signals)
    sections.extend(("", "The software surfaces evidence and hypotheses. Management makes the decision."))
    if explain:
        sections.extend(("", line, "EVIDENCE TRACE", line))
        for signal in briefing.signals:
            sections.extend((f"[{signal.priority}] {signal.title}", f"Interpretation: {signal.interpretation}", "Evidence:"))
            sections.extend(f"- {item}" for item in signal.evidence)
            sections.extend((f"Question: {signal.management_question}", ""))
    return "\n".join(sections).rstrip() + "\n"
