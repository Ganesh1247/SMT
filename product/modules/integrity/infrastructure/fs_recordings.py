"""Filesystem recording store: DATA_DIR/recordings/<attempt_id>/<stream>/<seq>.chunk."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterator

from ..domain import models as d

BLOCK = 64 * 1024


class FsRecordings:
    def __init__(self, root: Path):
        self._root = root
        root.mkdir(parents=True, exist_ok=True)
        self._real_root = root.resolve()

    def _dir(self, attempt_id: str) -> Path:
        d.check_attempt_id(attempt_id)
        path = (self._root / attempt_id).resolve()
        if self._real_root not in path.parents:  # defence against traversal / symlinks
            raise d.InvalidInput("attempt_id")
        return path

    def _chunk_path(self, attempt_id: str, stream: str, seq: int) -> Path:
        d.check_stream(stream)
        d.check_seq(seq)
        return self._dir(attempt_id) / stream / ("%08d.chunk" % seq)

    def write(self, attempt_id, stream, seq, data):
        path = self._chunk_path(attempt_id, stream, seq)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)

    def read(self, attempt_id, stream, seq):
        return self._chunk_path(attempt_id, stream, seq).read_bytes()

    def open_range(self, attempt_id, parts, stream, start, end) -> Iterator[bytes]:
        offset = 0
        for seq, size in parts:
            lo, hi = offset, offset + size - 1
            offset += size
            if hi < start:
                continue
            if lo > end:
                break
            first = max(start, lo) - lo
            last = min(end, hi) - lo
            with open(self._chunk_path(attempt_id, stream, seq), "rb") as fh:
                fh.seek(first)
                remaining = last - first + 1
                while remaining > 0:
                    block = fh.read(min(BLOCK, remaining))
                    if not block:
                        break
                    remaining -= len(block)
                    yield block

    def write_manifest(self, attempt_id, manifest):
        path = self._dir(attempt_id)
        path.mkdir(parents=True, exist_ok=True)
        (path / "manifest.json").write_bytes(manifest)

    def delete_attempt(self, attempt_id):
        shutil.rmtree(self._dir(attempt_id), ignore_errors=True)
