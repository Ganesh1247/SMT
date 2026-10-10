# profiles/ - Context Overlays

A profile reweights or compresses the lifecycle for a specific context without weakening the constitution (rules 1-10 always apply). It can add agents, skills, a rubric and a timeline.

| Profile | Use for |
|---|---|
| `hackathon-24h` | Time-boxed competition judged by a rubric (SAMARTHA / 24-Hour Hackathon handbooks) |

Planned profiles (add as folders when needed): `client-delivery`, `startup-mvp`, `internal-tool`.

Activate: `python platform/scripts/activate_profile.py <profile>`  |  Deactivate: `python platform/scripts/activate_profile.py --off`

Structure of a profile:
```
profiles/<name>/
├─ README.md       what it is and how to run it
├─ timeline.md     how gates map to the available time
├─ rubric.md       external scoring rules, if any
├─ agents/*.md     extra agents (installed to .claude/agents/profile-<name>/)
└─ skills/<s>/SKILL.md   extra skills (installed to .claude/skills/)
```
