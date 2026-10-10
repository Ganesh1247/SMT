"""Integrity use cases. Ownership is enforced here: an attempt is bound to the learner who
recorded consent for it, and every learner-facing operation checks that binding. Unknown and
foreign attempts raise the same NotFound.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Mapping, Protocol

from ..domain import models as d


@dataclass(frozen=True)
class IntegrityConfig:
    chunk_max_bytes: int = 5 * 1024 * 1024
    max_events_per_attempt: int = 5000
    retention_days: int = 30
    risk_medium: float = 5.0
    risk_high: float = 15.0
    weights: Mapping[str, float] = field(default_factory=lambda: dict(d.DEFAULT_WEIGHTS))
    thresholds: d.PrecheckThresholds = d.PrecheckThresholds()
    precheck_payload_max_bytes: int = 2 * 1024 * 1024
    consent_current_version: str | None = None


@dataclass(frozen=True)
class ChunkReceipt:
    attempt_id: str
    stream: str
    seq: int
    sha256: str
    size: int


@dataclass(frozen=True)
class Flag:
    code: str
    task_id: str
    attempt_id: str
    matched_attempts: int


@dataclass(frozen=True)
class IntegritySummary:
    attempt_id: str
    counts: Mapping[str, int]
    total_events: int
    dropped_events: int
    weighted_score: float
    risk_label: str
    flags: tuple[Flag, ...]
    consent: Mapping[str, Any] | None
    recording: Mapping[str, Any]
    advisory: str = "For human review only. This summary does not change any result."

    @property
    def risk(self) -> str:
        """Alias of risk_label (low | medium | high) for consumers that expect `risk`."""
        return self.risk_label

    def to_dict(self) -> dict:
        return {"attempt_id": self.attempt_id, "counts": dict(self.counts), "total_events": self.total_events,
                "dropped_events": self.dropped_events, "weighted_score": self.weighted_score,
                "risk_label": self.risk_label,
                "risk": self.risk_label, "flags": [{"code": f.code, "task_id": f.task_id, "matched_attempts": f.matched_attempts}
                          for f in self.flags],
                "consent": dict(self.consent) if self.consent else None,
                "recording": dict(self.recording), "advisory": self.advisory}


@dataclass(frozen=True)
class PlaybackSlice:
    status: int  # 200 | 206 | 416
    total: int
    start: int
    end: int
    headers: Mapping[str, str]
    body: Iterator[bytes]


class Repo(Protocol):
    def attempt_owner(self, attempt_id: str) -> str | None: ...
    def save_consent(self, rec: d.ConsentRecord) -> None: ...
    def latest_consent(self, attempt_id: str) -> d.ConsentRecord | None: ...
    def add_events(self, attempt_id: str, events: list[d.Event], cap: int, now: float) -> tuple[int, int]: ...
    def event_counts(self, attempt_id: str) -> tuple[dict[str, int], int]: ...
    def chunk(self, attempt_id: str, stream: str, seq: int) -> tuple[str, int] | None: ...
    def put_chunk(self, attempt_id: str, stream: str, seq: int, sha: str, size: int, now: float) -> None: ...
    def chunks(self, attempt_id: str) -> list[tuple[str, int, str, int]]: ...
    def manifest(self, attempt_id: str) -> tuple[str, int] | None: ...
    def save_manifest(self, attempt_id: str, manifest_hash: str, chunks: int, now: float) -> None: ...
    def add_fingerprint(self, attempt_id: str, task_id: str, h: str, dataset_id: str | None, now: float) -> None: ...
    def matching_attempts(self, attempt_id: str, task_id: str, h: str, dataset_id: str | None) -> list[str]: ...
    def add_flag(self, attempt_id: str, code: str, task_id: str, matched: int, now: float) -> None: ...
    def flags(self, attempt_id: str) -> list[tuple[str, str, int]]: ...
    def save_precheck(self, learner_id: str, passed: bool, now: float) -> None: ...
    def latest_precheck(self, learner_id: str) -> bool: ...
    def expired_attempts(self, before: float) -> list[str]: ...
    def mark_purged(self, attempt_id: str, now: float) -> None: ...


class Recordings(Protocol):
    def write(self, attempt_id: str, stream: str, seq: int, data: bytes) -> None: ...
    def read(self, attempt_id: str, stream: str, seq: int) -> bytes: ...
    def open_range(self, attempt_id: str, parts: list[tuple[int, int]], stream: str, start: int,
                   end: int) -> Iterator[bytes]: ...
    def write_manifest(self, attempt_id: str, manifest: bytes) -> None: ...
    def delete_attempt(self, attempt_id: str) -> None: ...


class IntegrityService:
    def __init__(self, repo: Repo, recordings: Recordings, config: IntegrityConfig,
                 clock: Callable[[], float] = time.time):
        self._repo, self._rec, self._cfg, self._clock = repo, recordings, config, clock

    # ------------------------------------------------------------ ownership
    def _owned(self, attempt_id: str, learner_id: str) -> None:
        d.check_attempt_id(attempt_id)
        d.check_learner_id(learner_id)
        if self._repo.attempt_owner(attempt_id) != learner_id:
            raise d.NotFound("attempt")

    # ------------------------------------------------------------ consent
    def record_consent(self, attempt_id: str, learner_id: str, version: Any, scopes: Any) -> d.ConsentRecord:
        d.check_attempt_id(attempt_id)
        d.check_learner_id(learner_id)
        version, scopes = d.check_consent(version, scopes)
        owner = self._repo.attempt_owner(attempt_id)
        if owner is not None and owner != learner_id:
            raise d.NotFound("attempt")
        rec = d.ConsentRecord(attempt_id, learner_id, version, scopes, self._clock())
        self._repo.save_consent(rec)
        return rec

    # ------------------------------------------------------------ events
    def ingest_events(self, attempt_id: str, learner_id: str, events: Any) -> int:
        self._owned(attempt_id, learner_id)
        parsed = d.validate_events(events)
        if not parsed:
            return 0
        stored, _dropped = self._repo.add_events(attempt_id, parsed, self._cfg.max_events_per_attempt, self._clock())
        return stored

    # ------------------------------------------------------------ recording
    def store_chunk(self, attempt_id: str, learner_id: str, stream: Any, seq: Any, data: Any) -> ChunkReceipt:
        self._owned(attempt_id, learner_id)
        stream, seq = d.check_stream(stream), d.check_seq(seq)
        if not isinstance(data, (bytes, bytearray)) or len(data) == 0:
            raise d.InvalidInput("chunk")
        if len(data) > self._cfg.chunk_max_bytes:
            raise d.TooLarge("chunk")
        consent = self._repo.latest_consent(attempt_id)
        if consent is None or stream not in consent.scopes:
            raise d.NotFound("attempt")  # no consent for this stream: indistinguishable from unknown
        if self._repo.manifest(attempt_id) is not None:
            raise d.Conflict("recording_finalized")
        sha = hashlib.sha256(bytes(data)).hexdigest()
        existing = self._repo.chunk(attempt_id, stream, seq)
        if existing is not None:
            if existing[0] == sha:
                return ChunkReceipt(attempt_id, stream, seq, sha, len(data))  # idempotent retry
            raise d.Conflict("chunk_exists")
        self._rec.write(attempt_id, stream, seq, bytes(data))
        self._repo.put_chunk(attempt_id, stream, seq, sha, len(data), self._clock())
        return ChunkReceipt(attempt_id, stream, seq, sha, len(data))

    def finalize_recording(self, attempt_id: str, learner_id: str) -> dict:
        self._owned(attempt_id, learner_id)
        done = self._repo.manifest(attempt_id)
        if done is not None:
            return {"manifest_hash": done[0], "chunks": done[1]}
        rows = self._repo.chunks(attempt_id)
        streams: dict[str, list[dict]] = {s: [] for s in d.STREAMS}
        for stream, seq, sha, size in rows:
            streams[stream].append({"seq": seq, "sha256": sha, "size": size})
        for lst in streams.values():
            lst.sort(key=lambda c: c["seq"])
        manifest = {"version": 1, "attempt_id": attempt_id, "streams": streams}
        blob = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        manifest_hash = hashlib.sha256(blob).hexdigest()
        self._rec.write_manifest(attempt_id, blob)
        self._repo.save_manifest(attempt_id, manifest_hash, len(rows), self._clock())
        return {"manifest_hash": manifest_hash, "chunks": len(rows)}

    def verify_recording(self, attempt_id: str) -> bool:
        """Recompute every chunk hash and the manifest hash; True only if all match."""
        d.check_attempt_id(attempt_id)
        done = self._repo.manifest(attempt_id)
        if done is None:
            return False
        streams: dict[str, list[dict]] = {s: [] for s in d.STREAMS}
        for stream, seq, sha, size in self._repo.chunks(attempt_id):
            try:
                data = self._rec.read(attempt_id, stream, seq)
            except OSError:
                return False
            if hashlib.sha256(data).hexdigest() != sha or len(data) != size:
                return False
            streams[stream].append({"seq": seq, "sha256": sha, "size": size})
        for lst in streams.values():
            lst.sort(key=lambda c: c["seq"])
        blob = json.dumps({"version": 1, "attempt_id": attempt_id, "streams": streams},
                          sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest() == done[0]

    def playback_range(self, attempt_id: str, stream: Any, range_header: str | None) -> PlaybackSlice:
        """Reviewer-side helper (caller authorises the reviewer role). Serves the ordered concatenation
        of a stream's chunks with HTTP Range semantics."""
        d.check_attempt_id(attempt_id)
        stream = d.check_stream(stream)
        parts = [(seq, size) for s, seq, _sha, size in self._repo.chunks(attempt_id) if s == stream]
        parts.sort()
        total = sum(size for _seq, size in parts)
        if total == 0:
            raise d.NotFound("recording")
        base = {"Accept-Ranges": "bytes", "Content-Type": "video/webm", "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff"}
        try:
            rng = d.parse_range(range_header, total)
        except d.Unsatisfiable:
            return PlaybackSlice(416, total, 0, 0, {**base, "Content-Range": "bytes */%d" % total}, iter(()))
        if rng is None:
            start, end, status = 0, total - 1, 200
            headers = {**base, "Content-Length": str(total)}
        else:
            start, end = rng
            status = 206
            headers = {**base, "Content-Length": str(end - start + 1),
                       "Content-Range": "bytes %d-%d/%d" % (start, end, total)}
        return PlaybackSlice(status, total, start, end, headers,
                             self._rec.open_range(attempt_id, parts, stream, start, end))

    # ------------------------------------------------------------ summary and similarity
    def summary(self, attempt_id: str) -> IntegritySummary:
        d.check_attempt_id(attempt_id)
        counts, dropped = self._repo.event_counts(attempt_id)
        flags = tuple(Flag(code, task, attempt_id, n) for code, task, n in self._repo.flags(attempt_id))
        merged = dict(counts)
        for f in flags:
            merged[f.code] = merged.get(f.code, 0) + 1
        score, label = d.risk_summary(merged, self._cfg.weights, self._cfg.risk_medium, self._cfg.risk_high)
        consent = self._repo.latest_consent(attempt_id)
        manifest = self._repo.manifest(attempt_id)
        return IntegritySummary(
            attempt_id, dict(sorted(counts.items())), sum(counts.values()), dropped, score, label, flags,
            ({"version": consent.version, "scopes": list(consent.scopes), "recorded_at": consent.recorded_at}
             if consent else None),
            {"finalized": manifest is not None, "manifest_hash": manifest[0] if manifest else None,
             "chunks": manifest[1] if manifest else 0})

    def fingerprint_submit(self, attempt_id: str, task_id: Any, answer_values_hash: Any,
                           dataset_id: str | None = None) -> list[Flag]:
        d.check_attempt_id(attempt_id)
        task_id, h = d.check_task_id(task_id), d.check_sha256(answer_values_hash)
        if dataset_id is not None:
            d.check_task_id(dataset_id)
        now = self._clock()
        self._repo.add_fingerprint(attempt_id, task_id, h, dataset_id, now)
        matches = self._repo.matching_attempts(attempt_id, task_id, h, dataset_id)
        if not matches:
            return []
        self._repo.add_flag(attempt_id, d.SIMILARITY_FLAG, task_id, len(matches), now)
        return [Flag(d.SIMILARITY_FLAG, task_id, attempt_id, len(matches))]

    # ------------------------------------------------------------ pre-check
    def evaluate_precheck(self, learner_id: str, report: Any) -> d.PrecheckResult:
        d.check_learner_id(learner_id)
        result = d.evaluate_precheck(report, self._cfg.thresholds)
        self._repo.save_precheck(learner_id, result.passed, self._clock())
        return result

    def latest_precheck_passed(self, learner_id: str) -> bool:
        d.check_learner_id(learner_id)
        return self._repo.latest_precheck(learner_id)

    # ------------------------------------------------------------ retention
    def purge_expired(self, now: float | None = None) -> int:
        now = self._clock() if now is None else now
        cutoff = now - self._cfg.retention_days * 86400
        purged = 0
        for attempt_id in self._repo.expired_attempts(cutoff):
            self._rec.delete_attempt(attempt_id)
            self._repo.mark_purged(attempt_id, now)
            purged += 1
        return purged
