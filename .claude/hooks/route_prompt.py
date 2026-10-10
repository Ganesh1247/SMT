"""UserPromptSubmit hook - the 'main brain' router.
Classifies the prompt against governance/routing/routing-table.txt (+ learned routes), checks the lifecycle
state, and injects a compact route (~100 tokens) for the orchestrator. Never blocks; silent on error."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _telemetry  # noqa: E402


def load_table(root):
    path = os.path.join(root, "governance", "routing", "routing-table.txt")
    records, cur = [], {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.startswith("#"):
                continue
            if line.strip() == "---":
                if cur:
                    records.append(cur)
                cur = {}
                continue
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                cur[m.group(1)] = m.group(2).strip()
    if cur:
        records.append(cur)
    return records


def load_learned(root):
    out = {}
    path = os.path.join(root, "kaizen", "learned-routing.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if "=>" in line and not line.startswith("#"):
                    phrase, intent = (p.strip() for p in line.split("=>", 1))
                    out.setdefault(intent, []).append(phrase.lower())
    return out


def read_state(root):
    data, section = {}, None
    try:
        with open(os.path.join(root, "delivery", "state", "lifecycle-state.yaml"), encoding="utf-8") as fh:
            for raw in fh:
                line = raw.split("#", 1)[0].rstrip()
                if not line.strip():
                    continue
                m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
                if m:
                    k, v = m.groups()
                    if v == "":
                        section = k
                        data[k] = {}
                    else:
                        section = None
                        data[k] = v
                    continue
                m = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
                if m and section:
                    data[section][m.group(1)] = m.group(2)
    except Exception:
        pass
    return data


def score(prompt, rec, learned):
    p = " " + prompt.lower() + " "
    total = 0
    hits = []
    for kw in [k.strip().lower() for k in rec.get("keywords", "").split(",") if k.strip()] + learned.get(rec["intent"], []):
        # short keywords match on word start to avoid 'ui' inside 'build'
        pat = r"(?<![a-z0-9])" + re.escape(kw) + (r"" if len(kw) > 4 else r"(?![a-z0-9])")
        if re.search(pat, p):
            total += 1 + len(kw.split()) - 1
            hits.append(kw)
    return total, hits


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    prompt = (payload.get("prompt") or "").strip()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    if not prompt or prompt.startswith("/") or len(prompt.split()) < 2:
        return
    try:
        table = load_table(root)
    except Exception:
        return
    state = read_state(root)
    profile = state.get("profile", "none")
    learned = load_learned(root)
    scored = []
    for rec in table:
        if rec.get("profile") and rec["profile"] != profile:
            continue
        s, hits = score(prompt, rec, learned)
        if s:
            scored.append((s, rec, hits))
    scored.sort(key=lambda x: -x[0])
    gates = state.get("gates", {})
    cur = state.get("current_gate", "G0")
    locked = [g for g in ("G3", "G4") if gates.get(g) != "approved"]
    status = f"gate {cur} ({gates.get(cur, '?')})"
    if scored:
        top = scored[0]
        also = [r["intent"] for s, r, _ in scored[1:3] if s >= max(1, top[0] * 0.6)]
        rec = top[1]
        lines = [
            f"[route] intent={rec['intent']}" + (f" (also: {', '.join(also)})" if also else "") + f" | {status}"
            + (f" | product/ LOCKED until {','.join(locked)} approved" if locked else ""),
            f"roles: {rec.get('roles')} | skills: {rec.get('skills')} | gate: {rec.get('gate')}",
            f"chain: {rec.get('chain')} | {rec.get('note')}",
            "Orchestrator: confirm this route in one line, follow governance/routing, update memory and handoff after. "
            "If the route is wrong, say so and run: python platform/scripts/improve.py learn \"<phrase>\" <intent>",
        ]
        if rec["intent"] == "implement" and locked:
            lines.append("WARNING: implementation requested but the gate lock is active - route to planning/architecture first.")
        _telemetry.log("route", intent=rec["intent"], also=also, gate=cur, score=top[0], locked=bool(locked))
    else:
        lines = [f"[route] intent=unmatched | {status} | use skill triage-request to classify; if this is a recurring "
                 "request type, run: python platform/scripts/improve.py learn \"<phrase>\" <intent>"]
        _telemetry.log("route", intent="unmatched", gate=cur, snippet=prompt[:80])
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
