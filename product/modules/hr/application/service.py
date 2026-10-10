"""HR use cases: role requirements (versioned), coverage and gaps, evidence page, receipt verification."""
from __future__ import annotations

import logging
from datetime import timezone

from ..domain import coverage
from .ports import Clock, Contracts, DocStore, EvidencePort, Ids, ReviewPort

log = logging.getLogger("hr")
_CLIENT_KEYS = {"title", "summary", "competencies"}
MAX_PAGES = 20
DEFAULT_ROLE = ("role_adhoc", 1)
NOTE = "Order is not a ranking."
LABEL = "Experimental. Not a validated hiring predictor. These results should support, not replace, your own assessment."


class HrError(Exception):
    code = "error"

    def __init__(self, code: str | None = None, details: list | None = None):
        super().__init__(code or self.code)
        if code:
            self.code = code
        self.details = details or []


class NotFound(HrError):
    code = "not_found"


class Invalid(HrError):
    code = "invalid_role"


class Upstream(HrError):
    code = "upstream_unavailable"


def _iso(dt) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class HrService:
    def __init__(self, store: DocStore, review: ReviewPort, evidence: EvidencePort, clock: Clock, ids: Ids,
                 contracts: Contracts):
        self.s, self.review, self.evidence, self.clock, self.ids, self.contracts = store, review, evidence, clock, ids, contracts

    # ------------------------------------------------------------ roles
    def _validate(self, org: str, role_id: str, version: int, body, created_at: str) -> dict:
        if not isinstance(body, dict):
            raise Invalid(details=[{"field": "(body)", "message": "Expected an object"}])
        extra = sorted(set(body) - _CLIENT_KEYS)
        if extra:
            raise Invalid(details=[{"field": k, "message": "Field is not allowed"} for k in extra])
        doc = {"schema_version": "0.1", "role_id": role_id, "recipient_id": org, "title": body.get("title"),
               "version": version, "competencies": body.get("competencies"), "created_at": created_at}
        if "summary" in body:
            doc["summary"] = body["summary"]
        doc = {k: v for k, v in doc.items() if v is not None}
        errs = self.contracts.errors("role-requirement.schema.json", doc)
        comps = doc.get("competencies")
        if not errs and len({c["competency_id"] for c in comps}) != len(comps):
            errs = [{"field": "competencies", "message": "Each competency may appear once"}]
        if errs:
            raise Invalid(details=errs)
        return doc

    def _view(self, doc: dict) -> dict:
        return {**doc, "readback": [coverage.readback(c) for c in doc["competencies"]]}

    def create_role(self, org: str, body) -> dict:
        role_id = "role_" + self.ids.new_id().replace("-", "")[-12:]
        doc = self._validate(org, role_id, 1, body, _iso(self.clock.now()))
        self.s.put("role_versions", f"{role_id}:1", doc)
        self.s.put("roles", role_id, {"role_id": role_id, "recipient_id": org, "current_version": 1})
        return self._view(doc)

    def update_role(self, org: str, role_id: str, body) -> dict:
        head = self._head(org, role_id)
        version = head["current_version"] + 1
        doc = self._validate(org, role_id, version, body, _iso(self.clock.now()))
        self.s.put("role_versions", f"{role_id}:{version}", doc)
        self.s.put("roles", role_id, {**head, "current_version": version})
        return self._view(doc)

    def _head(self, org: str, role_id: str) -> dict:
        head = self.s.get("roles", role_id)
        if head is None or head["recipient_id"] != org:
            raise NotFound()
        return head

    def get_role(self, org: str, role_id: str, version: int | None = None) -> dict:
        head = self._head(org, role_id)
        doc = self.s.get("role_versions", f"{role_id}:{version or head['current_version']}")
        if doc is None:
            raise NotFound()
        return self._view(doc)

    def list_roles(self, org: str) -> list[dict]:
        out = []
        for head in self.s.all("roles"):
            if head["recipient_id"] != org:
                continue
            d = self.s.get("role_versions", f"{head['role_id']}:{head['current_version']}")
            out.append({"role_id": d["role_id"], "title": d["title"], "version": d["version"], "created_at": d["created_at"]})
        out.sort(key=lambda r: (r["created_at"], r["role_id"]))
        return out

    # ------------------------------------------------------------ querying Trust
    def _query(self, org: str, role_id: str, role_version: int, competency_ids: list[str],
               candidate_refs: list[str] | None = None) -> list[dict]:
        results: list[dict] = []
        cursor = None
        for _ in range(MAX_PAGES):
            req = {"schema_version": "0.1", "request_id": self.ids.new_id(), "recipient_id": org, "role_id": role_id,
                   "role_version": role_version, "competency_ids": competency_ids}
            if candidate_refs:
                req["candidate_refs"] = candidate_refs
            if cursor:
                req["page"] = {"cursor": cursor}
            try:
                resp = self.review.query_shared_evidence(req, org)
            except Exception:
                log.warning("shared_evidence_query_failed")
                raise Upstream() from None
            if not self.contracts.is_valid("shared-evidence-query-response.schema.json", resp):
                log.error("shared_evidence_response_invalid")
                raise Upstream()
            results.extend(resp["results"])
            cursor = resp["page"]["next_cursor"]
            if not cursor:
                break
        return results

    def results(self, org: str, role_id: str) -> dict:
        role = self.get_role(org, role_id)
        comps = role["competencies"]
        as_of = self.clock.now()
        shared = self._query(org, role_id, role["version"], [c["competency_id"] for c in comps])
        by_alias: dict[str, dict[str, dict]] = {}
        for s in shared:
            by_alias.setdefault(s["candidate_ref"], {})[s["competency_id"]] = s
        candidates = []
        for alias in sorted(by_alias):
            rows = []
            for c in comps:
                r = coverage.evaluate(c, by_alias[alias].get(c["competency_id"]), as_of)
                rows.append({"competency_id": c["competency_id"], "priority": c["priority"], "coverage": r["coverage"],
                             "gap": c["priority"] == "required" and r["coverage"] in ("not_met", "no_evidence"),
                             "reasons": r["reasons"], "last_evidence_at": r["last_evidence_at"]})
            candidates.append({"candidate_ref": alias, "competencies": rows})
        return {"role_id": role_id, "role_version": role["version"], "as_of": _iso(as_of), "note": NOTE,
                "label": LABEL, "candidates": candidates}

    def _context(self, org: str, role_id: str | None) -> tuple[str, int]:
        if role_id is None:
            return DEFAULT_ROLE
        head = self._head(org, role_id)
        return role_id, head["current_version"]

    def evidence_page(self, org: str, alias: str, competency_id: str, role_id: str | None) -> dict:
        rid, ver = self._context(org, role_id)
        found = [r for r in self._query(org, rid, ver, [competency_id], [alias])
                 if r["candidate_ref"] == alias and r["competency_id"] == competency_id]
        if not found:
            raise NotFound()
        return found[0]

    def verify_receipt(self, org: str, alias: str, competency_id: str, receipt_hash: str, role_id: str | None) -> dict:
        page = self.evidence_page(org, alias, competency_id, role_id)
        if not any(i["receipt_hash"] == receipt_hash for i in page["evidence_items"]):
            raise NotFound()
        try:
            r = self.evidence.verify_receipt(receipt_hash)
        except Exception:
            return {"status": "unavailable"}
        if r.get("status") not in ("match", "mismatch"):
            return {"status": "unavailable"}
        out = {"status": r["status"]}
        if r["status"] == "match" and r.get("sequence"):
            out["ledger_entry"] = r["sequence"]
        return out
