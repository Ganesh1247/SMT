"""Self-improvement engine: turns telemetry, state and lessons into ranked signals and change proposals.
Safe by design: it WRITES proposals and learned routing phrases only. Changes to .claude/ and governance/
need Founder approval and are applied by the Chief of Staff.

Usage:
  python platform/scripts/improve.py analyze            read telemetry -> kaizen/signals.md (+ draft proposals)
  python platform/scripts/improve.py status             one-line summary used by the session brief
  python platform/scripts/improve.py learn "<phrase>" <intent>   teach the router a new phrase (auto-applied, reversible)
  python platform/scripts/improve.py resolve CP-0001 approved|rejected|applied|deferred
  python platform/scripts/improve.py unlearn "<phrase>"
"""
import collections
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402

KZ = os.path.join(cfg.ROOT, "kaizen")
EVENTS = os.path.join(KZ, "telemetry", "events.jsonl")
SIGNALS = os.path.join(KZ, "signals.md")
LEARNED = os.path.join(KZ, "learned-routing.txt")
CPDIR = os.path.join(KZ, "change-proposals")
ROUTES = os.path.join(cfg.ROOT, "governance", "routing", "routing-table.txt")

T_UNMATCHED, T_BLOCK, T_LOCKED, T_REWORK = 3, 3, 2, 1

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def events():
    if not os.path.exists(EVENTS):
        return []
    out = []
    with open(EVENTS, encoding="utf-8") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def intents():
    names = set()
    with open(ROUTES, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^intent:\s*(\S+)", line)
            if m:
                names.add(m.group(1))
    return names


def next_cp():
    nums = [int(m.group(1)) for p in glob.glob(os.path.join(CPDIR, "CP-*.md"))
            if (m := re.match(r"CP-(\d+)", os.path.basename(p)))]
    return max(nums, default=0) + 1


def existing_slug(slug):
    return any(slug in os.path.basename(p) for p in glob.glob(os.path.join(CPDIR, "CP-*.md")))


def draft(slug, title, problem, change, effect):
    if existing_slug(slug):
        return None
    n = next_cp()
    name = f"CP-{n:04d}-auto-{slug}.md"
    body = (f"<!-- STATUS: DRAFT -->\n# CP-{n:04d}: {title}\n\nStatus: PROPOSED\n"
            f"Owner: process-improvement-engineer | Date: {time.strftime('%Y-%m-%d')} | Source: telemetry (auto-drafted)\n\n"
            f"## Problem and evidence\n{problem}\n\n## Proposed change\n{change}\n\n"
            f"## Expected effect\n{effect}\n\n## Risk and rollback\nLow; revert the edited file(s) via version history.\n\n"
            f"## Founder decision\n_Pending. Approve with: python platform/scripts/improve.py resolve CP-{n:04d} approved_\n")
    os.makedirs(CPDIR, exist_ok=True)
    with open(os.path.join(CPDIR, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    return name


def pending():
    n = 0
    for p in glob.glob(os.path.join(CPDIR, "CP-*.md")):
        if re.search(r"^Status:\s*PROPOSED", open(p, encoding="utf-8").read(), re.M):
            n += 1
    return n


def cmd_analyze():
    ev = events()
    state = cfg.read_state()
    sig, made = [], []
    routes = [e for e in ev if e.get("event") == "route"]
    by_intent = collections.Counter(e.get("intent") for e in routes)
    unmatched = [e for e in routes if e.get("intent") == "unmatched"]
    blocks = collections.Counter(e.get("hook") for e in ev if e.get("event") == "block")
    locked_impl = [e for e in routes if e.get("intent") == "implement" and e.get("locked")]
    turns = collections.Counter(e.get("gate") for e in ev if e.get("event") == "turn_end")

    if len(unmatched) >= T_UNMATCHED:
        snippets = "; ".join(f"\"{e.get('snippet', '')[:50]}\"" for e in unmatched[-6:])
        sig.append(f"ROUTING GAP: {len(unmatched)} prompts matched no intent. Recent: {snippets}")
        n = draft("routing-gap", "Close routing gaps from unmatched prompts",
                  f"{len(unmatched)} prompts matched no intent. Samples: {snippets}",
                  "Teach phrases with `improve.py learn \"<phrase>\" <intent>` or add keywords/intents to governance/routing/routing-table.txt.",
                  "Fewer misrouted prompts; less triage overhead.")
        made.append(n)
    for hook, c in blocks.items():
        if c >= T_BLOCK:
            sig.append(f"RECURRING BLOCK: hook '{hook}' blocked {c} times - agents keep hitting the same guardrail")
            n = draft(f"recurring-block-{hook}", f"Reduce repeated '{hook}' blocks",
                      f"The '{hook}' hook blocked {c} times.",
                      f"Strengthen the preconditions in the relevant agent/skill prompts (and CLAUDE.md rule) so the guardrail is satisfied before the write is attempted.",
                      "Fewer wasted tool calls and tokens.")
            made.append(n)
    if len(locked_impl) >= T_LOCKED:
        sig.append(f"EARLY BUILD ATTEMPTS: {len(locked_impl)} implementation requests while product/ was locked")
        n = draft("early-build-requests", "Make the plan-before-code path faster",
                  f"{len(locked_impl)} implementation requests arrived while G3/G4 were unapproved.",
                  "Add a quick-start path in orchestrate-lifecycle that explains the lock and proposes the shortest route to G4 for the current project.",
                  "Less friction; faster path to a build-ready state.")
        made.append(n)
    for g, c in state.get("rework_count", {}).items():
        if int(c) >= T_REWORK:
            sig.append(f"REWORK: gate {g} reworked {c}x - review its audit findings for a root cause")
            n = draft(f"rework-{g.lower()}", f"Reduce rework at gate {g}",
                      f"Gate {g} needed {c} rework loop(s) (see delivery/G6-assurance-audit/gate-audits/).",
                      f"Run a retrospective on {g}; tighten the template or owner-agent checklist for the failed criteria.",
                      "Higher first-pass audit rate.")
            made.append(n)
    made = [m for m in made if m]
    lines = [f"analyzed_events: {len(ev)}", "# Improvement Signals", "",
             f"Events: {len(ev)} | turns: {sum(turns.values())} | prompts routed: {len(routes)} | unmatched: {len(unmatched)}",
             "Top intents: " + (", ".join(f"{k} {v}" for k, v in by_intent.most_common(6)) or "none"),
             "Hook blocks: " + (", ".join(f"{k} {v}" for k, v in blocks.items()) or "none"), "", "## Signals"]
    lines += [f"- {s}" for s in sig] or ["- none above thresholds"]
    lines += ["", "## New proposals drafted"] + ([f"- {m}" for m in made] or ["- none"])
    lines += ["", f"Pending Founder review: {pending()}"]
    os.makedirs(KZ, exist_ok=True)
    with open(SIGNALS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[1:]))
    return 0


def cmd_status():
    total = len(events())
    seen = 0
    if os.path.exists(SIGNALS):
        m = re.match(r"analyzed_events:\s*(\d+)", open(SIGNALS, encoding="utf-8").readline())
        seen = int(m.group(1)) if m else 0
    p, fresh = pending(), total - seen
    bits = []
    if p:
        bits.append(f"{p} proposal(s) await Founder review in kaizen/change-proposals/")
    if fresh >= 25:
        bits.append(f"{fresh} new telemetry events - run skill self-improve")
    print("; ".join(bits))
    return 0


def cmd_learn(phrase, intent):
    if intent not in intents():
        print(f"unknown intent '{intent}'. Valid: {', '.join(sorted(intents()))}", file=sys.stderr)
        return 1
    if len(phrase.split()) > 6 or len(phrase) < 3:
        print("phrase must be 3-60 chars and at most 6 words", file=sys.stderr)
        return 1
    line = f"{phrase.lower()} => {intent}"
    existing = open(LEARNED, encoding="utf-8").read() if os.path.exists(LEARNED) else "# phrase => intent (learned by the router; edit freely)\n"
    if line in existing:
        print("already learned")
        return 0
    with open(LEARNED, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(existing.rstrip("\n") + "\n" + line + "\n")
    print(f"learned: {line}")
    return 0


def cmd_unlearn(phrase):
    if not os.path.exists(LEARNED):
        return 0
    lines = [l for l in open(LEARNED, encoding="utf-8").read().splitlines() if not l.lower().startswith(phrase.lower() + " =>")]
    open(LEARNED, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("unlearned")
    return 0


def cmd_resolve(cp, status):
    if status not in ("approved", "rejected", "applied", "deferred"):
        print("status must be approved|rejected|applied|deferred", file=sys.stderr)
        return 1
    files = glob.glob(os.path.join(CPDIR, f"{cp}-*.md"))
    if not files:
        print("not found", file=sys.stderr)
        return 1
    t = open(files[0], encoding="utf-8").read()
    t = re.sub(r"^Status:\s*\w+", f"Status: {status.upper()}", t, count=1, flags=re.M)
    open(files[0], "w", encoding="utf-8", newline="\n").write(t)
    print(f"{cp} -> {status.upper()}")
    return 0


def main(a):
    if not a:
        print(__doc__)
        return 1
    if a[0] == "analyze":
        return cmd_analyze()
    if a[0] == "status":
        return cmd_status()
    if a[0] == "learn" and len(a) == 3:
        return cmd_learn(a[1], a[2])
    if a[0] == "unlearn" and len(a) == 2:
        return cmd_unlearn(a[1])
    if a[0] == "resolve" and len(a) == 3:
        return cmd_resolve(a[1], a[2])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
