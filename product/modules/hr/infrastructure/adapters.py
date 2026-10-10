"""Default adapters and helpers over sibling modules' public api/ (lazy, api-only imports)."""
from __future__ import annotations

from .contracts import validator


class ReviewApiAdapter:
    def query_shared_evidence(self, request, caller_recipient_id):
        from review import api as review_api
        return review_api.query_shared_evidence(request, caller_recipient_id)


class SchemaContracts:
    def is_valid(self, name, doc):
        return validator(name).is_valid(doc)

    def errors(self, name, doc):
        out = []
        for e in sorted(validator(name).iter_errors(doc), key=lambda e: list(map(str, e.absolute_path))):
            out.append({"field": ".".join(str(p) for p in e.absolute_path) or "(body)", "message": e.message[:200]})
        return out[:20]
