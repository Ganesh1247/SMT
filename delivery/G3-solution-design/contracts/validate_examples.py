"""Validate contract examples against the draft schemas.

Every file named valid.* must pass; every file named invalid.* must fail.
Run from this folder:  python validate_examples.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).parent
SCHEMAS = {
    "evidence-event": HERE / "evidence-event.schema.json",
    "share-grant": HERE / "share-grant.schema.json",
    "shared-evidence": HERE / "shared-evidence.schema.json",
    "role-requirement": HERE / "role-requirement.schema.json",
}


def schema_for(name: str) -> str:
    # valid.evidence-event.criterion-result.json -> evidence-event
    return name.split(".")[1]


def main() -> int:
    validators = {
        key: Draft202012Validator(json.loads(path.read_text(encoding="utf-8")), format_checker=FormatChecker())
        for key, path in SCHEMAS.items()
    }
    failures = 0
    for path in sorted((HERE / "examples").glob("*.json")):
        expected_valid = path.name.startswith("valid.")
        validator = validators[schema_for(path.name)]
        errors = list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))))
        ok = (not errors) if expected_valid else bool(errors)
        status = "ok  " if ok else "FAIL"
        detail = "" if ok else f" -> {errors[0].message if errors else 'expected a failure, got none'}"
        if expected_valid is False and errors:
            detail = f" (rejected as intended: {errors[0].message[:70]})"
        print(f"{status} {path.name}{detail}")
        failures += 0 if ok else 1
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
