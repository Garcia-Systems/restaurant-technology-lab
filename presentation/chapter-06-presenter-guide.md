# Chapter 6 Presenter Guide — Customer Feedback

## Purpose

Turn fictional guest language into inspectable business evidence without presenting a phrase heuristic as AI or confusing a customer symptom with its cause.

## Suggested live sequence

1. Show three or four fictional reviews and ask what patterns the audience notices.
2. Open the CSV fields and explicit `TOPIC_RULES` taxonomy.
3. Run `python examples/customer_feedback.py`.
4. Reveal discussed topics and reinforce that ratings do not overwrite mixed text.
5. Highlight the wait-time negative-share change; say “directional signal,” not “significant.”
6. Run `python examples/customer_feedback.py --topic wait_time` and trace matches to source text.
7. Run `python examples/customer_feedback.py --period-days 14`.
8. Compare conclusions and explain the responsiveness/sample-size tradeoff.
9. Ask whether feedback reveals a cause or only a symptom.
10. Ask which demand, staffing, kitchen, inventory, or sales evidence to inspect next.

## Presenter cautions

- All feedback is fictional; never imply it came from a public platform or real guest.
- Mixed signals count as positive and negative and also appear in “Other.”
- The 20-percentage-point threshold is a workshop rule, not a statistical test.
- Phrase matching can miss context. Invite correction through drill-down rather than defending the classifier.
- Do not diagnose kitchen, staffing, or reservation failures from review text alone.

## Discovery and transition

Use the chapter's operator questions to learn how feedback arrives, what gets missed, and how a signal is investigated today. Then ask:

> **What happens when all of these signals appear on the same Friday night?**

That is the completed Friday Night Capstone. Keep its reveal for the next section.
