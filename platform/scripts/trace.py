"""Traceability and impact analysis across delivery artifacts (ID scanning, stdlib only).
Usage:
  python platform/scripts/trace.py matrix            REQ coverage across artifacts + gaps
  python platform/scripts/trace.py req REQ-001       where one requirement appears (file:line)
  python platform/scripts/trace.py slices            SLICE planned vs built; REQs without slices
  python platform/scripts/trace.py impact <artifact> downstream artifacts and gates to re-open
  python platform/scripts/trace.py orphans           IDs used downstream but not defined upstream
Artifact keys: brief research feasibility prd metrics ux arch threat deps plan tests build report security audit"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402

ART = {
    "brief": ("G0", "delivery/G0-intake/project-brief.md"),
    "research": ("G1", "delivery/G1-discovery/market-and-user-research.md"),
    "feasibility": ("G1", "delivery/G1-discovery/feasibility-assessment.md"),
    "prd": ("G2", "delivery/G2-product-definition/prd.md"),
    "metrics": ("G2", "delivery/G2-product-definition/success-metrics.md"),
    "ux": ("G3", "delivery/G3-solution-design/ux-flows.md"),
    "arch": ("G3", "delivery/G3-solution-design/architecture-overview.md"),
    "threat": ("G3", "delivery/G3-solution-design/threat-model.md"),
    "deps": ("G3", "delivery/G3-solution-design/dependency-register.md"),
    "plan": ("G4", "delivery/G4-delivery-plan/delivery-plan.md"),
    "tests": ("G4", "delivery/G4-delivery-plan/test-strategy.md"),
    "build": ("G5", "delivery/G5-build-log/build-log.md"),
    "report": ("G6", "delivery/G6-assurance-audit/test-report.md"),
    "security": ("G6", "delivery/G6-assurance-audit/security-review.md"),
    "audit": ("G6", "delivery/G6-assurance-audit/audit-report.md"),
}
DOWN = {
    "brief": ["research", "feasibility", "prd", "metrics", "ux", "arch", "threat", "deps", "plan", "tests", "build", "report", "security", "audit"],
    "research": ["prd", "metrics"], "feasibility": ["prd", "arch"],
    "prd": ["metrics", "ux", "arch", "threat", "plan", "tests", "build", "report", "audit"],
    "metrics": ["tests", "report"],
    "ux": ["plan", "build", "report"],
    "arch": ["threat", "deps", "plan", "build", "report", "security"],
    "threat": ["build", "security"], "deps": ["build"],
    "plan": ["build", "report", "audit"], "tests": ["report"],
    "build": ["report", "audit"], "report": ["audit"], "security": ["audit"],
}
REQ = re.compile(r"\bREQ-\d{1,4}\b")
SLICE = re.compile(r"\bSLICE-\d{1,4}\b")
COVER = ["ux", "arch", "plan", "tests", "build", "report"]


def path(key):
    return os.path.join(cfg.ROOT, ART[key][1])


def text(key):
    p = path(key)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def ids(pattern, key):
    t = text(key)
    return set(pattern.findall(t)) if t else set()


def cmd_matrix():
    reqs = sorted(ids(REQ, "prd"))
    if not reqs:
        print("No REQ-### found in prd.md (missing or not yet written).")
        return 1
    present = [k for k in COVER if text(k) is not None]
    print("REQ".ljust(10) + " ".join(k.ljust(6) for k in COVER))
    gaps = []
    for r in reqs:
        row = []
        for k in COVER:
            if text(k) is None:
                row.append("n/a".ljust(6))
            elif r in ids(REQ, k):
                row.append("ok".ljust(6))
            else:
                row.append("-".ljust(6))
                gaps.append((r, k))
        print(r.ljust(10) + " ".join(row))
    if gaps:
        print(f"\nGAPS ({len(gaps)}): " + ", ".join(f"{r} missing in {k}" for r, k in gaps[:20]))
    else:
        print("\nNo gaps in existing artifacts.")
    if len(present) < len(COVER):
        print("Not yet written: " + ", ".join(k for k in COVER if k not in present))
    return 1 if gaps else 0


def cmd_req(rid):
    found = False
    for k in ART:
        t = text(k)
        if not t:
            continue
        for n, line in enumerate(t.splitlines(), 1):
            if rid in line:
                print(f"{ART[k][1]}:{n}: {line.strip()[:110]}")
                found = True
    if not found:
        print(f"{rid}: not found in any artifact")
    return 0 if found else 1


def cmd_slices():
    planned, built = ids(SLICE, "plan"), ids(SLICE, "build")
    print(f"planned {len(planned)} | built/logged {len(built)}")
    print("not built: " + (", ".join(sorted(planned - built)) or "none"))
    print("built but not planned: " + (", ".join(sorted(built - planned)) or "none"))
    plan = text("plan") or ""
    uncovered = [r for r in sorted(ids(REQ, "prd")) if r not in plan]
    print("REQs without a slice: " + (", ".join(uncovered) or "none"))
    return 0


def cmd_impact(key):
    if key not in ART:
        match = [k for k, (_, p) in ART.items() if p.endswith(key) or key in p]
        if not match:
            print("unknown artifact; keys: " + " ".join(ART))
            return 1
        key = match[0]
    state = cfg.read_state().get("gates", {})
    down = DOWN.get(key, [])
    print(f"Change in '{key}' ({ART[key][0]}) affects {len(down)} downstream artifact(s):")
    reopen = set()
    for d in down:
        g = ART[d][0]
        st = state.get(g, "?")
        exists = "exists" if os.path.exists(path(d)) else "not written"
        print(f"  {d:<9} {g}  gate={st:<12} {exists}")
        if st == "approved" and os.path.exists(path(d)):
            reopen.add(g)
    own = ART[key][0]
    if state.get(own) == "approved":
        reopen.add(own)
    if reopen:
        print("Approved gates to RE-OPEN and re-audit (needs Founder approval): " + ", ".join(sorted(reopen)))
    else:
        print("No approved gate is affected.")
    return 0


def cmd_orphans():
    defined = ids(REQ, "prd")
    bad = []
    for k in ("ux", "arch", "threat", "plan", "tests", "build", "report"):
        for r in ids(REQ, k) - defined:
            bad.append(f"{r} in {k}")
    sl_def = ids(SLICE, "plan")
    for s in ids(SLICE, "build") - sl_def:
        bad.append(f"{s} in build")
    print("Orphans: " + ("; ".join(bad) if bad else "none"))
    return 1 if bad else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    c = argv[0]
    if c == "matrix":
        return cmd_matrix()
    if c == "req" and len(argv) > 1:
        return cmd_req(argv[1].upper())
    if c == "slices":
        return cmd_slices()
    if c == "impact" and len(argv) > 1:
        return cmd_impact(argv[1])
    if c == "orphans":
        return cmd_orphans()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
