"""Validate contract examples against the draft schemas.

Every file named valid.* must pass; every file named invalid.* must fail.
Schemas may $ref each other by $id; they are resolved locally, never over the network.
Run from this folder:  python validate_examples.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

HERE = Path(__file__).parent
SCHEMAS = {
    "evidence-event": "evidence-event.schema.json",
    "share-grant": "share-grant.schema.json",
    "shared-evidence": "shared-evidence.schema.json",
    "role-requirement": "role-requirement.schema.json",
    "shared-evidence-query-request": "shared-evidence-query-request.schema.json",
    "shared-evidence-query-response": "shared-evidence-query-response.schema.json",
}


def schema_for(name: str) -> str:
    # valid.evidence-event.criterion-result.json -> evidence-event
    # invalid.shared-evidence-query-request.leaks-threshold.json -> shared-evidence-query-request
    parts = name.removesuffix(".json").split(".")
    return parts[1]


def main() -> int:
    docs = {key: json.loads((HERE / fn).read_text(encoding="utf-8")) for key, fn in SCHEMAS.items()}
    registry = Registry().with_resources(
        (doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
        for doc in docs.values()
    )
    validators = {
        key: Draft202012Validator(doc, registry=registry, format_checker=FormatChecker())
        for key, doc in docs.items()
    }
    failures = 0
    for path in sorted((HERE / "examples").glob("*.json")):
        expected_valid = path.name.startswith("valid.")
        validator = validators[schema_for(path.name)]
        errors = list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))))
        ok = (not errors) if expected_valid else bool(errors)
        status = "ok  " if ok else "FAIL"
        if ok and not expected_valid:
            detail = f" (rejected as intended: {errors[0].message[:70]})"
        elif ok:
            detail = ""
        else:
            detail = f" -> {errors[0].message if errors else 'expected a failure, got none'}"
        print(f"{status} {path.name}{detail}")
        failures += 0 if ok else 1
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
