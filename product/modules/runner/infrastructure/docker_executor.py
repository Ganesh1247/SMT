"""Docker-per-run executor (ADR-0003). One locked-down, single-use container per run.

The argument list is a fixed template. The only request-derived value is the
validated `run_id` (canonical UUID) used in the container name and label. The
submission travels only on stdin; no mounts exist; the image is run by its
immutable image ID (SR-07) and is never pulled.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from ..application.run_service import ChildOutcome
from ..domain import models as m
from .capped_process import run_capped

DEFAULT_IMAGE = "python:3.11-slim"
NAME_PREFIX = "crucible-run-"


@lru_cache(maxsize=1)
def harness_source() -> str:
    return (Path(__file__).with_name("child_harness.py")).read_text(encoding="utf-8")


def build_docker_argv(docker_bin: str, image_ref: str, run_id: str, limits: m.Limits) -> list[str]:
    """Fixed template (SBX-FF-10). Only `docker_bin`, `image_ref` (config), `run_id` (validated), and
    constants derived from the closed profile enum are interpolated."""
    if not m.is_canonical_uuid(run_id):
        raise ValueError("run_id must be a canonical UUID")
    mem = "%dm" % limits.memory_mb
    return [
        docker_bin, "run", "--rm", "-i",
        "--name", NAME_PREFIX + run_id,
        "--label", "crucible.run=" + run_id,
        "--pull", "never",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--pids-limit", "64",
        "--memory", mem, "--memory-swap", mem,
        "--cpus", "0.5",
        "--ulimit", "nofile=256:256",
        "--user", "65534",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--workdir", "/tmp",
        image_ref,
        "python", "-I", "-c", harness_source(),
    ]


class DockerExecutor:
    isolation_mode = "container"

    def __init__(self, docker_bin: str | None = None, image: str | None = None, pinned_image_id: str | None = None):
        self._bin = docker_bin or os.environ.get("RUNNER_DOCKER_BIN") or "docker"
        self._image = image or os.environ.get("RUNNER_IMAGE") or DEFAULT_IMAGE
        self._pin = pinned_image_id or os.environ.get("RUNNER_IMAGE_ID") or None

    def _resolved_bin(self) -> str | None:
        return shutil.which(self._bin)

    def preflight(self) -> str | None:
        """Return the immutable image ID if Docker works and the image is present and matches the pin."""
        exe = self._resolved_bin()
        if exe is None:
            return None
        try:
            proc = subprocess.run([exe, "image", "inspect", "--format", "{{.Id}}", self._image],
                                  capture_output=True, timeout=10, shell=False)
        except Exception:  # noqa: BLE001
            return None
        if proc.returncode != 0:
            return None
        image_id = proc.stdout.decode("utf-8", "replace").strip()
        if not image_id.startswith("sha256:"):
            return None
        if self._pin and self._pin != image_id:
            return None  # SBX-FF-4: refuse a non-pinned image
        return image_id

    def available(self) -> bool:
        return self.preflight() is not None

    def execute(self, run_id: str, payload: dict, limits: m.Limits) -> ChildOutcome:
        exe = self._resolved_bin()
        image_id = self.preflight() if exe else None
        if exe is None or image_id is None:
            return ChildOutcome("unavailable")
        argv = build_docker_argv(exe, image_id, run_id, limits)
        name = NAME_PREFIX + run_id

        def kill_container() -> None:
            subprocess.run([exe, "kill", name], capture_output=True, timeout=10, shell=False)

        data = json.dumps(payload).encode("utf-8")
        try:
            rc, out, flag = run_capped(argv, data, limits.wall_seconds, limits.max_output_bytes,
                                       on_kill=kill_container)
        except OSError:
            return ChildOutcome("unavailable")
        finally:
            try:  # reaper for this run: --rm normally removes it; force on every exit path
                subprocess.run([exe, "rm", "-f", name], capture_output=True, timeout=10, shell=False)
            except Exception:  # noqa: BLE001
                pass
        if flag == "timeout":
            return ChildOutcome("timeout")
        if flag == "output_too_large":
            return ChildOutcome("output_too_large")
        if rc in (125, 126, 127):
            return ChildOutcome("unavailable")
        if rc == 137 and not out:
            return ChildOutcome("oom")
        if rc != 0 and not out:
            return ChildOutcome("crashed")
        return ChildOutcome("ok", out)
