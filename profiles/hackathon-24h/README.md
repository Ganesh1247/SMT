# Profile: hackathon-24h

For the SAMARTHA / 24-Hour Hackathon (problem-statement format). Source documents: `reference/24_Hour_Hackathon_Handbook.pdf` (authoritative, 20 pages) and `reference/SAMARTHA_Handbook.pdf` (8-page themed summary).

## What this profile changes
- Maps lifecycle gates onto the five event stages (see `timeline.md`).
- Adds the scoring rubric (`rubric.md`) so every artifact is written for the evidence the judges score.
- Adds agents `hackathon-judge-simulator` and `demo-defence-coach`, and skills `score-against-rubric`, `plan-demo`, `rehearse-defence`.
- Keeps all constitution rules: the gate lock still applies, but gates are compressed - artifacts are one-pagers.

## Activate
```
python platform/scripts/activate_profile.py hackathon-24h
```
Then say "start the hackathon" - the Chief of Staff runs the compressed timeline.

## Non-negotiables from the handbooks
- Work only on the issued problem; do not alter its scope.
- Disclose all third-party libraries, APIs, datasets and pretrained models (`dependency-register.md`).
- Never present a mock-up, video or simulation as functional.
- Keep version history as evidence.
- Demo the final submitted version live.
