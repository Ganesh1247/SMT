"""Beta-posterior competency estimate with a 10th-90th percentile band. Pure maths."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

HALF_LIFE_DAYS = 180.0
GRID = 4000


@dataclass(frozen=True)
class RawEstimate:
    estimate: float
    lower: float
    upper: float


def decay(age_days: float, half_life: float = HALF_LIFE_DAYS) -> float:
    return 0.5 ** (max(age_days, 0.0) / half_life)


def _quantiles(a: float, b: float, qs: tuple[float, ...]) -> list[float]:
    """Quantiles of Beta(a, b) by cumulative midpoint integration of the log-pdf."""
    log_pdf = [((a - 1) * math.log((i + 0.5) / GRID) + (b - 1) * math.log(1 - (i + 0.5) / GRID))
               for i in range(GRID)]
    peak = max(log_pdf)
    pdf = [math.exp(v - peak) for v in log_pdf]
    total = sum(pdf)
    out, cum, idx = [], 0.0, 0
    for q in qs:
        target = q * total
        while idx < GRID and cum + pdf[idx] < target:
            cum += pdf[idx]
            idx += 1
        frac = (target - cum) / pdf[idx] if idx < GRID and pdf[idx] > 0 else 0.0
        out.append(min(1.0, max(0.0, (idx + frac) / GRID)))
    return out


def estimate_from_items(items: Iterable[tuple[float, float, float]],
                        half_life: float = HALF_LIFE_DAYS) -> RawEstimate:
    """items: (method weight, success fraction 0..1, age in days)."""
    s = f = 0.0
    for weight, success, age in items:
        w = weight * decay(age, half_life)
        s += w * success
        f += w * (1.0 - success)
    a, b = 1.0 + s, 1.0 + f
    lo, hi = _quantiles(a, b, (0.10, 0.90))
    mean = a / (a + b)
    lo, hi = min(lo, mean), max(hi, mean)
    return RawEstimate(round(mean, 4), round(lo, 4), round(hi, 4))
