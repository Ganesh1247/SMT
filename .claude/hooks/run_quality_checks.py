"""PostToolUse hook: runs the project's quality commands after an edit under product/.
Commands come from platform/quality-commands.json (set during G3 once the stack is chosen).
No-op while the file is absent or empty. Exit 2 feeds failures back to Claude."""
import json
import os
import subprocess
import sys


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
    if not rel.startswith("product/"):
        sys.exit(0)
    cfg_path = os.path.join(root, "platform", "quality-commands.json")
    if not os.path.exists(cfg_path):
        sys.exit(0)
    try:
        with open(cfg_path, encoding="utf-8") as fh:
            commands = json.load(fh).get("on_edit", [])
    except Exception as exc:
        sys.stderr.write(f"quality-commands.json unreadable: {exc}\n")
        sys.exit(0)
    failures = []
    for cmd in commands:
        try:
            res = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            failures.append(f"$ {cmd}\ntimed out after 120s")
            continue
        if res.returncode != 0:
            failures.append(f"$ {cmd}\n{(res.stdout + res.stderr)[-1500:]}")
    if failures:
        sys.stderr.write("QUALITY CHECKS FAILED after edit of " + rel + ":\n" + "\n\n".join(failures) + "\n")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
