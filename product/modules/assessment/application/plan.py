"""Deterministic attempt plans (seeded item selection and variants) and stable task ids."""
from __future__ import annotations

import random
import uuid
from typing import Any, Mapping, Optional, Sequence

from assessment.domain.rules import Rules, draw

NAMESPACE = uuid.UUID("6f0c9d2e-5b1a-4c7e-9a31-3b2f8e5d7a10")


def task_uuid(track: str, bank_id: str, stage: Optional[str]) -> str:
    return str(uuid.uuid5(NAMESPACE, f"crucible/{track}/{bank_id}/{stage or 'main'}"))


def dataset_uuid(task_id: str, dataset_name: str) -> str:
    return str(uuid.uuid5(uuid.UUID(task_id), dataset_name))


def item_ref(bank_id: str, stage: Optional[str]) -> str:
    return f"{bank_id}:{stage}" if stage else bank_id


def build_plan(track: str, level: int, seed: str, items: Sequence[Mapping[str, Any]], rules: Rules,
               used_before: Sequence[str] = ()) -> list[dict]:
    """Return the ordered list of planned items for an attempt (no answers inside)."""
    rng = random.Random(f"{seed}:{track}:{level}")
    by_id = {it["id"]: it for it in items}
    ids = list(by_id)
    plan: list[dict] = []
    if level == 1:
        for bank_id in draw(ids, rules.l1_count, rng, used_before):
            it = by_id[bank_id]
            variants = 1 + len(it.get("variants", []))
            order = [o["id"] for o in it.get("options", [])]
            rng.shuffle(order)
            plan.append({"ref": bank_id, "bank_id": bank_id, "stage": None,
                         "variant": rng.randrange(variants), "option_order": order})
    elif level == 2:
        for bank_id in draw(ids, rules.l2_count, rng, used_before):
            it = by_id[bank_id]
            ds = rng.randrange(len(it["datasets"]))
            tid = task_uuid(track, bank_id, None)
            name = it["datasets"][ds]["name"]
            plan.append({"ref": bank_id, "bank_id": bank_id, "stage": None, "dataset": name,
                         "task_uuid": tid, "dataset_uuid": dataset_uuid(tid, name)})
    elif level == 3:
        for bank_id in draw(ids, rules.l3_tasks, rng, used_before):
            it = by_id[bank_id]
            for stage in ("base", "mutated"):
                datasets = it["stages"][stage]["datasets"]
                name = datasets[rng.randrange(len(datasets))]["name"]
                tid = task_uuid(track, bank_id, stage)
                plan.append({"ref": item_ref(bank_id, stage), "bank_id": bank_id, "stage": stage,
                             "dataset": name, "task_uuid": tid, "dataset_uuid": dataset_uuid(tid, name)})
    return plan


def task_specs(track: str, level: int, item: Mapping[str, Any]):
    """Yield (task_uuid, kind, spec dict) for one bank item, in the runner's published spec format."""
    if level == 2:
        yield task_uuid(track, item["id"], None), item["kind"], _spec(track, item, item, None)
    elif level == 3:
        for stage in ("base", "mutated"):
            yield (task_uuid(track, item["id"], stage), item["kind"],
                   _spec(track, item, item["stages"][stage], stage))


def _spec(track: str, item: Mapping[str, Any], source: Mapping[str, Any], stage: Optional[str]) -> dict:
    kind = item["kind"]
    tid = task_uuid(track, item["id"], stage)
    datasets: dict[str, Any] = {}
    for ds in source["datasets"]:
        if kind == "python":
            datasets[dataset_uuid(tid, ds["name"])] = {"tests": ds["tests"]}
        else:
            datasets[dataset_uuid(tid, ds["name"])] = {"setup_sql": ds["setup_sql"], "tests": ds["tests"]}
    if kind == "python":
        return {"function": source.get("function") or item["function"], "datasets": datasets}
    return {"datasets": datasets}
