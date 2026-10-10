"""Append-only local telemetry used by the self-improvement loop. Never raises.
Stores intents and counts, not prompt content (short scrubbed snippets only for unmatched prompts)."""
import json
import os
import re
import time

SECRET = re.compile(r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_\-]{16,}|xox[baprs]-[\w\-]{8,}|"
                    r"(?i:password|secret|token|api[_-]?key)\s*[:=]\s*\S+)")


def log(event, **fields):
    try:
        root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        d = os.path.join(root, "kaizen", "telemetry")
        os.makedirs(d, exist_ok=True)
        rec = {"ts": int(time.time()), "event": event}
        for k, v in fields.items():
            if isinstance(v, str):
                v = SECRET.sub("[redacted]", v)[:120]
            rec[k] = v
        with open(os.path.join(d, "events.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass
