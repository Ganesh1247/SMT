"""Adapters from assessment ports to other modules' public api/ objects.

Stream B facades (runner.api, integrity.api) and intelligence.api are passed in by the composition
root as plain objects, so this module never imports them directly.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Mapping, Optional, Sequence

from assessment.application.ports import RunOutcome


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


class ModuleRunnerAdapter:
    """Wraps an object exposing run_python / run_sql / register_task (runner.api)."""

    def __init__(self, api: Any) -> None:
        self._api = api

    def register(self, task_id: str, kind: str, spec: Mapping[str, Any]) -> None:
        self._api.register_task(task_id, kind, json.dumps(spec))

    def run(self, kind: str, task_id: str, dataset_id: str, profile: str, submission: str) -> RunOutcome:
        run_id = str(uuid.uuid4())
        fn = self._api.run_python if kind == "python" else self._api.run_sql
        res = fn(run_id, task_id, dataset_id, profile, submission)
        tests = tuple({"id": str(_get(t, "id")), "passed": bool(_get(t, "passed")),
                       "message_safe": str(_get(t, "message_safe", ""))[:200]}
                      for t in (_get(res, "tests", ()) or ()))
        return RunOutcome(status=str(_get(res, "status", "error")), tests=tests,
                          stdout_trunc=str(_get(res, "stdout_trunc", ""))[:2000],
                          isolation_mode=str(_get(res, "isolation_mode", "unknown")))


class ModuleIntegrityAdapter:
    """Wraps integrity.api (record_consent, ingest_events, store_chunk, finalize_recording, fingerprint_submit)."""

    def __init__(self, api: Any) -> None:
        self._api = api

    def record_consent(self, attempt_id: str, learner_id: str, version: str, scopes: Sequence[str]) -> None:
        self._api.record_consent(attempt_id, learner_id, version, list(scopes))

    def ingest_events(self, attempt_id: str, learner_id: str, events: Sequence[Mapping[str, Any]]) -> None:
        self._api.ingest_events(attempt_id, learner_id, list(events))

    def store_chunk(self, attempt_id: str, learner_id: str, stream: str, seq: int, data: bytes) -> Any:
        return self._api.store_chunk(attempt_id, learner_id, stream, seq, data)

    def finalize_recording(self, attempt_id: str, learner_id: str) -> Mapping[str, Any]:
        return self._api.finalize_recording(attempt_id, learner_id)

    def fingerprint_submit(self, attempt_id: str, task_id: str, answer_values_hash: str) -> Any:
        return self._api.fingerprint_submit(attempt_id, task_id, answer_values_hash)


class EvidenceLedgerAdapter:
    def __init__(self) -> None:
        import evidence.api as evidence  # cross-module access via api/ only
        self._api = evidence

    def append(self, event_type: str, learner_id: str, payload: dict, idempotency_key: str) -> Any:
        return self._api.append(event_type, learner_id, payload, idempotency_key)


class ScoringGateAdapter:
    def __init__(self) -> None:
        import scoring.api as scoring  # cross-module access via api/ only
        self._api = scoring

    def apply_gated_update(self, learner_id: str, competency: str) -> bool:
        try:
            self._api.apply_gated_update(learner_id, competency)
        except self._api.GateNotMet:
            return False
        return True


class IntelligenceFeedbackAdapter:
    """Wraps intelligence.api.feedback(kind, payload); failures degrade to no feedback."""

    def __init__(self, api: Any) -> None:
        self._api = api

    def explain_failures(self, task_title: str, failed: Sequence[Mapping[str, Any]], passed_count: int) -> Optional[str]:
        res = self._api.feedback("failing_tests", {"failed": [{"id": f["id"], "message_safe": f.get("message_safe", "")} for f in failed],
                                                   "passed_count": passed_count, "task_title": task_title})
        return _get(res, "text") if _get(res, "status") != "unavailable" else None

    def explanation_feedback(self, explanation: str) -> Optional[Mapping[str, Any]]:
        res = self._api.feedback("debug_explanation", {"explanation": explanation})
        if _get(res, "status") == "unavailable":
            return None
        return {"text": _get(res, "text"), "confidence": _get(res, "confidence", 0.5),
                "model_ref": _get(res, "model_ref", "unspecified")}
