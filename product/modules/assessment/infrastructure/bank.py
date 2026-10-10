"""JSON item bank loader (files under assessment/bank/)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from assessment.domain.rules import Rules

BANK_DIR = Path(__file__).resolve().parents[1] / "bank"
FILES = {("python", 1): "python_l1.json", ("python", 2): "python_l2.json", ("python", 3): "python_l3.json",
         ("data_analyst", 1): "data_analyst_l1.json", ("data_analyst", 2): "data_analyst_l2.json",
         ("data_analyst", 3): "data_analyst_l3.json"}


class JsonBank:
    def __init__(self, directory: Path = BANK_DIR) -> None:
        self._dir = directory
        self.rules = Rules.from_json(json.loads((directory / "rules.json").read_text(encoding="utf-8")))
        self._data: dict[tuple[str, int], dict] = {
            key: json.loads((directory / name).read_text(encoding="utf-8")) for key, name in FILES.items()}

    def items(self, track: str, level: int) -> list[dict]:
        return self._data[(track, level)]["items"]

    def meta(self, track: str, level: int) -> Mapping[str, Any]:
        d = self._data[(track, level)]
        return {"version": d["version"], "rubric_id": d["rubric_id"]}

    def item(self, track: str, level: int, bank_id: str) -> dict:
        for it in self.items(track, level):
            if it["id"] == bank_id:
                return it
        raise KeyError(bank_id)
