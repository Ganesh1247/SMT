---
name: score-against-rubric
description: Simulate hackathon judging for a given round using the weighted 1-5 rubric and produce a ranked list of score-raising fixes. Use before Rounds 1-4 and during hardening.
---
# Score Against Rubric

Delegate to `hackathon-judge-simulator`. Input: round number (1-4). Rubric: `profiles/hackathon-24h/rubric.md`.

1. Collect evidence a judge would see for that round (artifacts, running prototype, tests, evidence pack).
2. Score every criterion 1-5 with an evidence citation; compute weighted scores (rating/5 x weight) and the round total.
3. Output a table: criterion | weight | rating | weighted | evidence | fix.
4. Rank fixes by score gain per hour of effort; mark any rules risks.
5. Chief of Staff schedules the top fixes before the next checkpoint.
