"""Restricted-subprocess executor: the explicit, labelled fallback (`process-fallback`).

Only used when `RUNNER_ALLOW_FALLBACK=true` and Docker is unusable. Weaker than the
container: no network/filesystem namespace. Mitigations: `python -I`, scrubbed env,
empty temp cwd, wall-clock kill, POSIX rlimits or a Windows Job Object (memory and
process-count limit, kill-on-close), plus the harness audit hook.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

from ..application.run_service import ChildOutcome
from ..domain import models as m
from .capped_process import run_capped
from .docker_executor import harness_source


def _assign_job(memory_mb: int):
    """Windows only: return an on_start callback that places the child in a limited Job Object."""
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class IO(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ("a", "b", "c", "d", "e", "f")]

    class EXT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    job = k32.CreateJobObjectW(None, None)
    if not job:
        raise OSError("CreateJobObject failed")
    info = EXT()
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x8
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x100
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    info.BasicLimitInformation.LimitFlags = (JOB_OBJECT_LIMIT_ACTIVE_PROCESS | JOB_OBJECT_LIMIT_PROCESS_MEMORY
                                             | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
    info.BasicLimitInformation.ActiveProcessLimit = 2
    info.ProcessMemoryLimit = memory_mb * 1024 * 1024
    if not k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        raise OSError("SetInformationJobObject failed")

    def on_start(proc) -> None:
        k32.AssignProcessToJobObject(job, wintypes.HANDLE(int(proc._handle)))

    def close() -> None:
        k32.CloseHandle(job)

    return on_start, close


class ProcessFallbackExecutor:
    isolation_mode = "process-fallback"

    def execute(self, run_id: str, payload: dict, limits: m.Limits) -> ChildOutcome:
        workdir = tempfile.mkdtemp(prefix="crucible-run-")
        env = {"PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        if os.name == "nt":
            env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
        argv = [sys.executable, "-I", "-c", harness_source()]
        preexec = None
        on_start = None
        close = None
        if os.name == "posix":
            import resource

            def preexec() -> None:  # runs in the child between fork and exec
                mem = limits.memory_mb * 4 * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                resource.setrlimit(resource.RLIMIT_CPU, (int(limits.wall_seconds), int(limits.wall_seconds)))
                resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
                resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
        else:
            try:
                on_start, close = _assign_job(limits.memory_mb)
            except Exception:  # noqa: BLE001
                on_start = close = None
        try:
            rc, out, flag = run_capped(argv, json.dumps(payload).encode("utf-8"), limits.wall_seconds,
                                       limits.max_output_bytes, env=env, cwd=workdir, preexec_fn=preexec,
                                       on_start=on_start)
        except OSError:
            return ChildOutcome("unavailable")
        finally:
            if close is not None:
                close()
            shutil.rmtree(workdir, ignore_errors=True)
        if flag == "timeout":
            return ChildOutcome("timeout")
        if flag == "output_too_large":
            return ChildOutcome("output_too_large")
        if rc != 0 and not out:
            return ChildOutcome("oom" if rc in (-9, 137, 3221225477, 3221225786) else "crashed")
        return ChildOutcome("ok", out)
