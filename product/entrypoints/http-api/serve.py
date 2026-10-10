"""Start the Crucible API.  Usage:  python product/entrypoints/http-api/serve.py

Environment (all optional): DATA_DIR, CRUCIBLE_HOST, CRUCIBLE_PORT, CRUCIBLE_COOKIE_SECURE,
CRUCIBLE_ALLOWED_ORIGINS, RUNNER_ALLOW_FALLBACK, ANTHROPIC_API_KEY, CRUCIBLE_MODEL.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[1]
for p in (PRODUCT / "modules", PRODUCT / "shared-kernel", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main() -> int:
    import uvicorn

    import wiring
    from config import Settings
    from main import create_app

    settings = Settings.from_env()
    try:
        app = create_app(settings)
    except wiring.StartupError as exc:
        print(f"STARTUP ERROR: {exc}", file=sys.stderr)
        return 2
    uvicorn.run(app, host=settings.host, port=settings.port, log_config=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
