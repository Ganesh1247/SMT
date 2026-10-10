"""SessionStart hook: injects a compact (<~600 token) project brief so a new, resumed or
compacted session recovers context without reading files. Silent on any error."""
import os
import subprocess
import sys


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    script = os.path.join(root, "platform", "scripts", "memory.py")
    if not os.path.exists(script):
        return
    try:
        res = subprocess.run([sys.executable, script, "brief"], cwd=root, capture_output=True,
                             text=True, encoding="utf-8", timeout=15)
        if res.returncode == 0 and res.stdout.strip():
            print("[project brief]\n" + res.stdout.strip())
    except Exception:
        pass


if __name__ == "__main__":
    main()
