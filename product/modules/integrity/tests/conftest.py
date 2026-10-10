"""Test bootstrap: make `integrity` importable and isolate DATA_DIR per test."""
import sys
from pathlib import Path

MODULES_DIR = str(Path(__file__).resolve().parents[2])
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    for name in ("INTEGRITY_RETENTION_DAYS", "INTEGRITY_CHUNK_MAX_BYTES", "INTEGRITY_MAX_EVENTS",
                 "INTEGRITY_RISK_MEDIUM", "INTEGRITY_RISK_HIGH", "PRECHECK_MIN_DOWN_MBPS"):
        monkeypatch.delenv(name, raising=False)
    from integrity import api
    api._reset_for_tests()
    yield
    api._reset_for_tests()
