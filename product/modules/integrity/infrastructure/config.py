"""Environment-driven configuration (no secrets are involved)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from ..application.service import IntegrityConfig
from ..domain import models as d


def data_dir() -> Path:
    return Path(os.environ.get("DATA_DIR") or "./data")


def _float(name: str, default: float, lo: float, hi: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if lo <= value <= hi else default


def load_config() -> IntegrityConfig:
    weights = dict(d.DEFAULT_WEIGHTS)
    raw = os.environ.get("INTEGRITY_EVENT_WEIGHTS")
    if raw:
        try:
            override = json.loads(raw)
            for key, val in override.items():
                if key in weights and isinstance(val, (int, float)) and not isinstance(val, bool) and 0 <= val <= 100:
                    weights[key] = float(val)
        except (ValueError, AttributeError):
            pass
    return IntegrityConfig(
        chunk_max_bytes=int(_float("INTEGRITY_CHUNK_MAX_BYTES", 5 * 1024 * 1024, 1024, 50 * 1024 * 1024)),
        max_events_per_attempt=int(_float("INTEGRITY_MAX_EVENTS", 5000, 10, 100000)),
        retention_days=int(_float("INTEGRITY_RETENTION_DAYS", 30, 1, 3650)),
        risk_medium=_float("INTEGRITY_RISK_MEDIUM", 5.0, 0, 1e6),
        risk_high=_float("INTEGRITY_RISK_HIGH", 15.0, 0, 1e6),
        weights=weights,
        thresholds=d.PrecheckThresholds(
            _float("PRECHECK_MIN_DOWN_MBPS", 2.0, 0, 10000),
            _float("PRECHECK_MIN_UP_MBPS", 1.0, 0, 10000),
            _float("PRECHECK_MAX_LATENCY_MS", 400.0, 1, 100000)),
        precheck_payload_max_bytes=int(_float("PRECHECK_PAYLOAD_MAX_BYTES", 2 * 1024 * 1024, 1024, 20 * 1024 * 1024)),
    )
