"""PreToolUse hook: enforces modular-monolith boundaries inside product/modules/.
A module may import another module only through that module's `api` surface."""
import json
import os
import re
import sys

LAYERS = {"domain", "application", "infrastructure", "api", "tests"}
ABSOLUTE = re.compile(r"modules[/.\\]([A-Za-z0-9_\-]+)[/.\\]([A-Za-z0-9_\-]+)")
RELATIVE = re.compile(r"(?:\.\./)+([A-Za-z0-9_\-]+)/(domain|application|infrastructure)\b")


def gather(ti):
    parts = []
    for key in ("content", "new_string"):
        if isinstance(ti.get(key), str):
            parts.append(ti[key])
    for edit in ti.get("edits") or []:
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            parts.append(edit["new_string"])
    return "\n".join(parts)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path")
    if not path:
        sys.exit(0)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    rel = os.path.relpath(os.path.abspath(path), root).replace("\\", "/")
    m = re.match(r"^product/modules/([^/]+)/", rel)
    if not m:
        sys.exit(0)
    own = m.group(1)
    violations = []
    for line in gather(ti).splitlines():
        for a in ABSOLUTE.finditer(line):
            other, layer = a.groups()
            if other != own and layer != "api":
                violations.append((line.strip(), f"imports {other}.{layer}"))
        for r in RELATIVE.finditer(line):
            other = r.group(1)
            if other != own and other not in LAYERS:
                violations.append((line.strip(), f"relative import into {other}/{r.group(2)}"))
    if violations:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import _telemetry
            _telemetry.log("block", hook="module_boundary")
        except Exception:
            pass
        detail = "; ".join(f"`{l[:80]}` ({why})" for l, why in violations[:3])
        sys.stderr.write(
            f"BLOCKED: module boundary violation in {rel}: {detail}. "
            "Cross-module access must go through the other module's api/ surface "
            "(constitution rule 7, .claude/rules/product-modules.md).\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
