"""Test bootstrap: make `runner` importable and give every test an isolated DATA_DIR."""
import os
import sys
from pathlib import Path

MODULES_DIR = str(Path(__file__).resolve().parents[2])
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.delenv("RUNNER_ALLOW_FALLBACK", raising=False)
    monkeypatch.delenv("RUNNER_DOCKER_BIN", raising=False)
    from runner.api import _reset_for_tests
    _reset_for_tests()
    yield
    _reset_for_tests()
