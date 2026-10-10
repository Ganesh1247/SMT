"""Default adapters over sibling modules' public api/ (imports are lazy and api-only)."""
from __future__ import annotations


class IntelligenceApiAdapter:
    def evaluate_interview(self, transcript, solution_code, rubric_version):
        from intelligence import api as intelligence_api
        return intelligence_api.evaluate_interview(transcript, solution_code, rubric_version).to_dict()


class ReviewApiAdapter:
    def enqueue_case(self, **kw):
        from review import api as review_api
        return review_api.enqueue_case(**kw)
