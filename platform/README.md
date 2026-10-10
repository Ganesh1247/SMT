# platform/ - Shared Kernel of the Workspace

| Path | Purpose |
|---|---|
| `templates/` | Artifact templates (first line `<!-- STATUS: TEMPLATE -->`); copy to `delivery/...`, then set DRAFT/FINAL |
| `scripts/validate_state.py` | Validates `lifecycle-state.yaml` (valid statuses, gate order, rework limit) |
| `scripts/gate_check.py` | Checks a gate's entry criteria and artifact status; exit 0 = ready for audit |
| `scripts/scaffold_module.py` | Creates a module skeleton under `product/modules/` (requires G3+G4 approved) |
| `scripts/activate_profile.py` | Activates/deactivates a profile overlay from `profiles/` |
| `scripts/memory.py` | Project memory engine: add, search, show, index, lint, archive, handoff, brief, stats (see `memory/README.md`) |
| `scripts/litecfg.py` | Dependency-free readers used by the scripts |
| `ci/` | CI pipeline definitions (created at G4 for the chosen stack) |
| `schemas/` | Reserved for machine-readable artifact schemas |
| `quality-commands.json` | Commands the post-edit hook runs on `product/` edits (set at G3) |

All scripts use only the Python standard library.
Usage examples:
```
python platform/scripts/validate_state.py
python platform/scripts/gate_check.py G2
python platform/scripts/activate_profile.py hackathon-24h
```
