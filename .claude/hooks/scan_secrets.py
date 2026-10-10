"""PreToolUse hook: blocks writes that contain likely secrets or that create .env files."""
import json
import os
import re
import sys

PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub token"),
    (r"github_pat_[A-Za-z0-9_]{50,}", "GitHub fine-grained token"),
    (r"sk-[A-Za-z0-9_\-]{24,}", "API secret key"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token"),
    (r"(?i)(api[_-]?key|secret|passwd|password|token)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]", "hard-coded credential"),
]
PLACEHOLDER = re.compile(r"(?i)(example|placeholder|changeme|your[_-]|xxxx|<.+>|\$\{.+\}|dummy|redacted)")


def gather(tool_input):
    parts = []
    for key in ("content", "new_string"):
        if isinstance(tool_input.get(key), str):
            parts.append(tool_input[key])
    for edit in tool_input.get("edits") or []:
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            parts.append(edit["new_string"])
    return "\n".join(parts)


def _log():
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import _telemetry
        _telemetry.log("block", hook="secret_scan")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path", "")
    name = os.path.basename(path)
    if name == ".env" or (name.startswith(".env.") and not name.endswith((".example", ".sample", ".template"))):
        _log()
        sys.stderr.write("BLOCKED: do not write .env files; use an .env.example with placeholders.\n")
        sys.exit(2)
    text = gather(ti)
    for line in text.splitlines():
        for pattern, label in PATTERNS:
            m = re.search(pattern, line)
            if m and not PLACEHOLDER.search(line):
                _log()
                sys.stderr.write(
                    f"BLOCKED: possible secret ({label}) in write to {path}. "
                    "Use environment variables or a secret manager (governance/policies/security-policy.md).\n"
                )
                sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
