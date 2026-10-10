"""Project memory engine - structured, searchable, token-frugal.

Usage: python platform/scripts/memory.py <command> [args]
  add     --type T --name SLUG --desc "one line" [--scope S] [--body "text" | stdin] [--update]
  search  <terms...> [--all] [--type T] [-n N]     one-line hits only (cheap)
  show    <name>                                    full body of one memory
  index                                             rebuild memory/INDEX.md (hard line cap)
  lint                                              validate frontmatter, sizes, duplicates
  archive <name>                                    move to memory/archive/ (status archived)
  handoff write "text" | show                       rolling 'where we left off' note
  brief                                             compact session brief (used by SessionStart hook)
  stats                                             counts and approximate token cost

Types: decision | fact | lesson | preference | reference
Memory file: memory/<type>/<name>.md with frontmatter name, description, type, scope, status, updated.
"""
import argparse
import datetime
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import litecfg as cfg  # noqa: E402

MEM = os.path.join(cfg.ROOT, "memory")
TYPES = ["decision", "fact", "lesson", "preference", "reference"]
INDEX_MAX_LINES = 60
BODY_MAX_LINES = 30
DESC_MAX = 140
HANDOFF_MAX_LINES = 25
BRIEF_MAX_CHARS = 2200
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{2,60}$")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def today():
    return datetime.date.today().isoformat()


def parse(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def load_all(include_archived=False):
    items = []
    for t in TYPES:
        for p in sorted(glob.glob(os.path.join(MEM, t, "*.md"))):
            meta, body = parse(p)
            if meta is None:
                continue
            meta["_path"], meta["_body"] = p, body
            if include_archived or meta.get("status", "active") == "active":
                items.append(meta)
    return items


def secret_check(text):
    sys.path.insert(0, os.path.join(cfg.ROOT, ".claude", "hooks"))
    import scan_secrets  # noqa: E402
    for line in text.splitlines():
        for pattern, label in scan_secrets.PATTERNS:
            if re.search(pattern, line) and not scan_secrets.PLACEHOLDER.search(line):
                return label
    return None


def cmd_add(a):
    if a.type not in TYPES:
        return fail(f"type must be one of {TYPES}")
    if not NAME_RE.match(a.name):
        return fail("name must be kebab-case, 3-61 chars")
    if len(a.desc) > DESC_MAX or "\n" in a.desc:
        return fail(f"description must be one line, <= {DESC_MAX} chars")
    body = a.body if a.body is not None else sys.stdin.read()
    body = body.strip()
    if len(body.splitlines()) > BODY_MAX_LINES:
        return fail(f"body exceeds {BODY_MAX_LINES} lines; split into several memories or link an artifact")
    label = secret_check(a.name + "\n" + a.desc + "\n" + body)
    if label:
        return fail(f"refusing to store likely secret ({label})")
    path = os.path.join(MEM, a.type, f"{a.name}.md")
    if os.path.exists(path) and not a.update:
        return fail("exists; use --update to overwrite (or choose a new name)")
    for other in load_all(include_archived=True):
        if other["name"] == a.name and other["_path"] != path:
            return fail(f"name already used in {other['type']}/")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"---\nname: {a.name}\ndescription: {a.desc}\ntype: {a.type}\nscope: {a.scope}\n"
                 f"status: active\nupdated: {today()}\n---\n{body}\n")
    cmd_index(None)
    print(f"stored memory/{a.type}/{a.name}.md")
    return 0


def tokens(text):
    return len(text) // 4


def cmd_search(a):
    terms = [t.lower() for t in a.terms]
    hits = []
    for m in load_all(include_archived=a.all):
        if a.type and m.get("type") != a.type:
            continue
        score = 0
        for t in terms:
            score += 3 * (t in m["name"].lower()) + 2 * (t in m.get("description", "").lower()) \
                + 2 * (t in m.get("scope", "").lower()) + (t in m["_body"].lower())
        if score:
            hits.append((score, m))
    hits.sort(key=lambda x: (-x[0], x[1].get("updated", "")), reverse=False)
    if not hits:
        print("no matches")
        return 0
    for score, m in hits[: a.n]:
        print(f"{m['type']}/{m['name']} - {m.get('description', '')} [{m.get('scope', '')}] ({m.get('updated', '')})")
    print(f"-- {min(len(hits), a.n)} of {len(hits)} shown; read one with: memory.py show <name>")
    return 0


def find(name):
    for m in load_all(include_archived=True):
        if m["name"] == name:
            return m
    return None


def cmd_show(a):
    m = find(a.name)
    if not m:
        return fail("not found")
    print(f"{m['type']}/{m['name']} [{m.get('scope', '')}] status={m.get('status')} updated={m.get('updated')}")
    print(m["_body"])
    return 0


def cmd_index(_):
    items = load_all()
    by_type = {t: sorted([m for m in items if m["type"] == t], key=lambda m: m.get("updated", ""), reverse=True)
               for t in TYPES}
    shown = {t: list(v) for t, v in by_type.items()}

    def render():
        out = ["# Memory Index", "",
               "One line per memory. Find with `python platform/scripts/memory.py search <terms>`; "
               "read with `show <name>`. Do not read all files.", ""]
        for t in TYPES:
            if not by_type[t]:
                continue
            out.append(f"## {t}")
            for m in shown[t]:
                out.append(f"- {m['name']} - {m.get('description', '')}")
            hidden = len(by_type[t]) - len(shown[t])
            if hidden:
                out.append(f"- (+{hidden} older {t} memories: use search)")
            out.append("")
        return out

    lines = render()
    while len(lines) > INDEX_MAX_LINES:
        biggest = max(TYPES, key=lambda t: len(shown[t]))
        if not shown[biggest]:
            break
        shown[biggest].pop()
        lines = render()
    with open(os.path.join(MEM, "INDEX.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return 0


def cmd_lint(_):
    errs, seen = [], {}
    for t in TYPES:
        for p in glob.glob(os.path.join(MEM, t, "*.md")):
            rel = os.path.relpath(p, cfg.ROOT).replace("\\", "/")
            meta, body = parse(p)
            if meta is None:
                errs.append(f"{rel}: missing frontmatter")
                continue
            for k in ("name", "description", "type", "scope", "status", "updated"):
                if not meta.get(k):
                    errs.append(f"{rel}: missing '{k}'")
            if meta.get("type") != t:
                errs.append(f"{rel}: type '{meta.get('type')}' does not match folder")
            if meta.get("name") != os.path.splitext(os.path.basename(p))[0]:
                errs.append(f"{rel}: name does not match filename")
            if len(meta.get("description", "")) > DESC_MAX:
                errs.append(f"{rel}: description > {DESC_MAX} chars")
            if len(body.splitlines()) > BODY_MAX_LINES:
                errs.append(f"{rel}: body > {BODY_MAX_LINES} lines")
            if secret_check(body):
                errs.append(f"{rel}: likely secret")
            if meta.get("name") in seen:
                errs.append(f"{rel}: duplicate name (also {seen[meta['name']]})")
            seen[meta.get("name")] = rel
    idx = os.path.join(MEM, "INDEX.md")
    if os.path.exists(idx) and len(open(idx, encoding="utf-8").read().splitlines()) > INDEX_MAX_LINES + 2:
        errs.append("INDEX.md exceeds line cap; run: memory.py index")
    if errs:
        print("MEMORY LINT FAILED:")
        for e in errs:
            print("  -", e)
        return 1
    print(f"memory lint ok ({len(seen)} memories)")
    return 0


def cmd_archive(a):
    m = find(a.name)
    if not m:
        return fail("not found")
    meta, body = parse(m["_path"])
    meta["status"] = "archived"
    meta["updated"] = today()
    dest_dir = os.path.join(MEM, "archive", m["type"])
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, f"{a.name}.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("---\n" + "\n".join(f"{k}: {v}" for k, v in meta.items()) + f"\n---\n{body}\n")
    os.remove(m["_path"])
    cmd_index(None)
    print(f"archived {a.name}")
    return 0


HANDOFF = os.path.join(MEM, "handoff.md")


def cmd_handoff(a):
    if a.mode == "show":
        print(open(HANDOFF, encoding="utf-8").read() if os.path.exists(HANDOFF) else "(no handoff)")
        return 0
    text = (a.text or sys.stdin.read()).strip()
    if len(text.splitlines()) > HANDOFF_MAX_LINES:
        return fail(f"handoff exceeds {HANDOFF_MAX_LINES} lines; keep only what the next session needs")
    if secret_check(text):
        return fail("refusing to store likely secret")
    with open(HANDOFF, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Handoff ({today()})\n{text}\n")
    print("handoff saved")
    return 0


def gate_snapshot():
    state = cfg.read_state()
    gid = state.get("current_gate", "G0")
    try:
        gate = cfg.read_gate(gid)
    except FileNotFoundError:
        return state, gid, "?", 0, 0
    total = missing = 0
    for pattern in gate.get("artifacts", []):
        total += 1
        files = cfg.resolve(pattern)
        if not files or any(cfg.artifact_status(f) != "FINAL" for f in files):
            missing += 1
    return state, gid, gate.get("name", "?"), total - missing, total


def cmd_brief(_):
    state, gid, gname, done, total = gate_snapshot()
    approved = [g for g, s in state.get("gates", {}).items() if s == "approved"]
    out = [
        f"PROJECT {state.get('project')} | profile {state.get('profile')} | stack {state.get('stack')} | lock {state.get('gate_lock')}",
        f"GATE {gid} {gname}: {done}/{total} artifacts FINAL | approved: {','.join(approved) or 'none'} | "
        f"rework {state.get('rework_count', {}).get(gid, '0')}/{state.get('rework_limit')}",
    ]
    if os.path.exists(HANDOFF):
        h = open(HANDOFF, encoding="utf-8").read().strip().splitlines()
        out.append("HANDOFF: " + " / ".join(l.strip() for l in h[1:] if l.strip())[:900])
    items = load_all()
    counts = ", ".join(f"{sum(1 for m in items if m['type'] == t)} {t}" for t in TYPES)
    recent = sorted(items, key=lambda m: m.get("updated", ""), reverse=True)[:4]
    out.append(f"MEMORY {counts}. Recent: " + "; ".join(f"{m['name']}" for m in recent))
    try:
        import improve
        import io
        buf, old = io.StringIO(), sys.stdout
        sys.stdout = buf
        improve.cmd_status()
        sys.stdout = old
        if buf.getvalue().strip():
            out.append("IMPROVE: " + buf.getvalue().strip())
    except Exception:
        sys.stdout = sys.__stdout__
    out.append("Recall: python platform/scripts/memory.py search <terms> | show <name>. "
               "Next: read delivery/state, then run orchestrate-lifecycle.")
    text = "\n".join(out)
    print(text[:BRIEF_MAX_CHARS])
    return 0


def cmd_stats(_):
    items = load_all()
    idx = open(os.path.join(MEM, "INDEX.md"), encoding="utf-8").read() if os.path.exists(os.path.join(MEM, "INDEX.md")) else ""
    total_chars = sum(len(m["_body"]) + len(m.get("description", "")) for m in items)
    print(f"memories: {len(items)} (full corpus ~{total_chars // 4} tokens - never loaded whole)")
    print(f"INDEX.md: ~{tokens(idx)} tokens  <- cost if loaded")
    import io
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    cmd_brief(None)
    sys.stdout = old
    print(f"session brief: ~{tokens(buf.getvalue())} tokens  <- cost loaded every session")
    return 0


def fail(msg):
    print("ERROR:", msg, file=sys.stderr)
    return 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("--type", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--desc", required=True)
    s.add_argument("--scope", default="project")
    s.add_argument("--body")
    s.add_argument("--update", action="store_true")
    s.set_defaults(fn=cmd_add)
    s = sub.add_parser("search")
    s.add_argument("terms", nargs="+")
    s.add_argument("--all", action="store_true")
    s.add_argument("--type")
    s.add_argument("-n", type=int, default=8)
    s.set_defaults(fn=cmd_search)
    s = sub.add_parser("show")
    s.add_argument("name")
    s.set_defaults(fn=cmd_show)
    for name, fn in (("index", cmd_index), ("lint", cmd_lint), ("brief", cmd_brief), ("stats", cmd_stats)):
        sub.add_parser(name).set_defaults(fn=fn)
    s = sub.add_parser("archive")
    s.add_argument("name")
    s.set_defaults(fn=cmd_archive)
    s = sub.add_parser("handoff")
    s.add_argument("mode", choices=["write", "show"])
    s.add_argument("text", nargs="?")
    s.set_defaults(fn=cmd_handoff)
    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
