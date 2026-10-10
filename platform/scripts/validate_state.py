"""Validate delivery/state/lifecycle-state.yaml for structural and ordering errors.
Usage: python platform/scripts/validate_state.py   Exit 0 = valid, 1 = invalid."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402

VALID_STATUS = {"pending", "in_progress", "audit", "approved"}


def main():
    errors = []
    state = cfg.read_state()
    gates = state.get("gates", {})
    for g in cfg.GATE_IDS:
        if g not in gates:
            errors.append(f"gates.{g} missing")
        elif gates[g] not in VALID_STATUS:
            errors.append(f"gates.{g} has invalid status '{gates[g]}'")
    # ordering: a gate cannot be approved if an earlier gate is not
    seen_unapproved = None
    for g in cfg.GATE_IDS:
        status = gates.get(g)
        if status != "approved" and seen_unapproved is None:
            seen_unapproved = g
        elif status == "approved" and seen_unapproved is not None:
            errors.append(f"{g} is approved but earlier gate {seen_unapproved} is not")
    current = state.get("current_gate")
    if current not in cfg.GATE_IDS:
        errors.append(f"current_gate '{current}' invalid")
    elif seen_unapproved and current != seen_unapproved and seen_unapproved in cfg.GATE_IDS:
        errors.append(f"current_gate is {current} but first unapproved gate is {seen_unapproved}")
    if state.get("gate_lock") not in ("enforced", "relaxed"):
        errors.append("gate_lock must be 'enforced' or 'relaxed'")
    try:
        limit = int(state.get("rework_limit", "2"))
        for g, n in state.get("rework_count", {}).items():
            if int(n) > limit:
                errors.append(f"{g} rework_count {n} exceeds rework_limit {limit}: escalate to Founder")
    except ValueError:
        errors.append("rework_limit / rework_count must be integers")
    if errors:
        print("INVALID STATE:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"State valid. project={state.get('project')} profile={state.get('profile')} current_gate={current}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
