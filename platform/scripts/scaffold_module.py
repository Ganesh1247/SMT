"""Scaffold a bounded-context module under product/modules/.
Usage: python platform/scripts/scaffold_module.py <module-name> "<one-line responsibility>"
Requires G3 and G4 approved (the gate lock hook enforces this for agent writes too)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402

MODULE_MD = """# Module: {name}

**Responsibility:** {resp}
**Owner:** TBD (set at G4)
**Status:** scaffolded

## Public surface (`api/`)
Only symbols exported from `api/` may be used by other modules. List them here.

## Depends on (other modules' `api/` only)
-

## Data owned
-

## Events published / consumed
-

## Layers
- `domain/` - entities, value objects, domain services; no framework or I/O imports
- `application/` - use cases, orchestration, ports (interfaces)
- `infrastructure/` - adapters implementing ports (DB, HTTP clients, queues)
- `api/` - the module's public contract (facade, DTOs, events)
- `tests/` - unit tests and contract tests for `api/`
"""


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    name, resp = argv[0], argv[1]
    if not re.fullmatch(r"[a-z][a-z0-9\-]*", name) or name in {"utils", "common", "misc", "helpers", "shared"}:
        print("Module name must be kebab-case and name a business capability (not utils/common/shared).")
        return 1
    gates = cfg.read_state().get("gates", {})
    if gates.get("G3") != "approved" or gates.get("G4") != "approved":
        print("Refusing: G3 and G4 must be approved before scaffolding product modules.")
        return 1
    base = os.path.join(cfg.ROOT, "product", "modules", name)
    if os.path.exists(base):
        print(f"Module {name} already exists.")
        return 1
    for sub in ("domain", "application", "infrastructure", "api", "tests"):
        os.makedirs(os.path.join(base, sub))
        open(os.path.join(base, sub, ".gitkeep"), "w").close()
    with open(os.path.join(base, "MODULE.md"), "w", encoding="utf-8") as fh:
        fh.write(MODULE_MD.format(name=name, resp=resp))
    print(f"Scaffolded product/modules/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
