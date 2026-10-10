"""Loads the G3 contract schemas (authoritative) and builds validators.

Resolution: env CRUCIBLE_CONTRACTS_DIR, else walk up to delivery/G3-solution-design/contracts.
Fails closed (raises) when the schemas cannot be found."""
from __future__ import annotations

import functools
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

_REL = Path("delivery") / "G3-solution-design" / "contracts"


@functools.lru_cache(maxsize=1)
def contracts_dir() -> Path:
    env = os.environ.get("CRUCIBLE_CONTRACTS_DIR")
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        if (parent / _REL).is_dir():
            return parent / _REL
    raise RuntimeError("contract schemas not found; set CRUCIBLE_CONTRACTS_DIR")


@functools.lru_cache(maxsize=1)
def registry() -> Registry:
    reg = Registry()
    for p in contracts_dir().glob("*.schema.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        reg = reg.with_resource(doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
    return reg


@functools.lru_cache(maxsize=None)
def validator(name: str) -> Draft202012Validator:
    schema = json.loads((contracts_dir() / name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=registry())


def is_valid(name: str, doc: dict) -> bool:
    return validator(name).is_valid(doc)
