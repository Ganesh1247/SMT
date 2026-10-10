"""PreToolUse hook: blocks writes to product/ until G3 and G4 are approved,
and blocks any write to reference/. Exit code 2 = block (stderr is shown to Claude)."""
import json
import os
import re
import sys

REQUIRED_GATES = ("G3", "G4")


def parse_state(path):
    """Section-aware minimal parser for lifecycle-state.yaml (no PyYAML dependency)."""
    data, section = {}, None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip():
                continue
            m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if m:
                key, val = m.groups()
                if val == "":
                    section = key
                    data[section] = {}
                else:
                    section = None
                    data[key] = val
                continue
            m = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
            if m and section:
                data[section][m.group(1)] = m.group(2)
    return data


def block(msg):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import _telemetry
        _telemetry.log("block", hook="gate_lock")
    except Exception:
        pass
    sys.stderr.write(msg + "\n")
    sys.exit(2)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    path = (payload.get("tool_input") or {}).get("file_path")
    if not path:
        sys.exit(0)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    rel = os.path.relpath(os.path.abspath(path), root).replace("\\", "/")

    if rel.startswith("reference/"):
        block("BLOCKED: reference/ is read-only source material (constitution rule 4).")

    if rel.startswith("product/") and rel != "product/README.md":
        state_file = os.path.join(root, "delivery", "state", "lifecycle-state.yaml")
        if not os.path.exists(state_file):
            block("BLOCKED: delivery/state/lifecycle-state.yaml is missing; cannot verify gates.")
        state = parse_state(state_file)
        if state.get("gate_lock", "enforced") == "relaxed":
            sys.exit(0)
        gates = state.get("gates", {})
        missing = [g for g in REQUIRED_GATES if gates.get(g) != "approved"]
        if missing:
            block(
                "BLOCKED by gate lock (constitution rule 1): product/ cannot be written until "
                + ", ".join(REQUIRED_GATES)
                + " are approved. Not yet approved: "
                + ", ".join(missing)
                + ". Current gate: "
                + state.get("current_gate", "?")
                + ". Run the orchestrate-lifecycle skill."
            )
    sys.exit(0)


if __name__ == "__main__":
    main()
