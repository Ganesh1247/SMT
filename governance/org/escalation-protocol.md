# Escalation Protocol

## Triggers
- Two roles disagree on a decision that crosses their decision rights.
- A gate fails more than `rework_limit` times.
- A security-engineer finding rated High/Critical is disputed.
- A requirement cannot be met within known constraints.
- An agent needs to act outside its tool scope or contract.

## Procedure
1. Raiser creates `delivery/decisions/escalations/ESC-NNNN-<slug>.md` from `platform/templates/escalation.md`.
2. Record: context, options (≥2), each role's position and evidence, recommended option, impact of delay.
3. Chief of Staff presents the escalation to the Founder in chat with the recommendation.
4. Founder decides; the decision is appended to the file with date. If it changes architecture, an ADR is added.
5. Affected artifacts are updated; the gate log notes the escalation ID.

## Rules
- Escalations are concise (one page) and neutral; positions are stated by their owners.
- Work on unaffected slices continues while an escalation is open.
