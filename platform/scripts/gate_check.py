"""Check a gate's entry criteria and required artifacts.
Usage: python platform/scripts/gate_check.py [G0..G8] [--require-final]
Defaults to the current gate. Exit 0 = ready, 1 = not ready."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    require_final = "--require-final" in argv or True  # a gate may only close on FINAL artifacts
    state = cfg.read_state()
    gate_id = args[0] if args else state.get("current_gate", "G0")
    gate = cfg.read_gate(gate_id)
    gates = state.get("gates", {})
    problems = []

    for req in gate.get("requires_gates", []):
        if gates.get(req) != "approved":
            problems.append(f"entry: upstream gate {req} is '{gates.get(req)}', must be 'approved'")

    for pattern in gate.get("artifacts", []):
        files = cfg.resolve(pattern)
        if not files:
            problems.append(f"missing artifact: {pattern}")
            continue
        for f in files:
            rel = os.path.relpath(f, cfg.ROOT).replace("\\", "/")
            status = cfg.artifact_status(f)
            if status is None:
                problems.append(f"{rel}: first line must be '<!-- STATUS: DRAFT|FINAL -->'")
            elif status == "TEMPLATE":
                problems.append(f"{rel}: still TEMPLATE")
            elif require_final and status != "FINAL":
                problems.append(f"{rel}: status {status}, must be FINAL to close the gate")

    print(f"Gate {gate_id} ({gate.get('name', '?')}) - owner: {gate.get('owner')}, approver: {gate.get('approver')}")
    if problems:
        print(f"NOT READY - {len(problems)} issue(s):")
        for p in problems:
            print(f"  - {p}")
        print("Exit criteria to satisfy:")
        for c in gate.get("exit_criteria", []):
            print(f"  * {c}")
        return 1
    print("READY: all entry criteria and artifacts satisfied. Next: compliance-auditor verdict, then Founder approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
