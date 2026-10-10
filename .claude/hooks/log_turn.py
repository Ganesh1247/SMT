"""Stop hook: records one telemetry event per completed turn (gate + counts only). Never blocks."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _telemetry  # noqa: E402


def main():
    gate = "?"
    try:
        root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        with open(os.path.join(root, "delivery", "state", "lifecycle-state.yaml"), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("current_gate:"):
                    gate = line.split(":", 1)[1].split("#")[0].strip()
    except Exception:
        pass
    _telemetry.log("turn_end", gate=gate)


if __name__ == "__main__":
    main()
