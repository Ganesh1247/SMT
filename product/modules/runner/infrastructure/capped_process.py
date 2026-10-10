"""Run a child process with a wall-clock deadline and a hard cap on captured stdout.

The only place in the runner that touches `subprocess` for learner execution. The
argument vector is always a list (never a shell string).
"""
from __future__ import annotations

import subprocess
import threading
from typing import Callable, Optional


def run_capped(argv: list[str], stdin_bytes: bytes, timeout: float, max_out: int, *,
               env: Optional[dict] = None, cwd: Optional[str] = None, preexec_fn=None,
               creationflags: int = 0, on_start: Optional[Callable] = None,
               on_kill: Optional[Callable[[], None]] = None) -> tuple[int | None, bytes, str]:
    """Return (returncode, stdout_bytes, status) where status is ok | timeout | output_too_large."""
    kwargs = {}
    if preexec_fn is not None:
        kwargs["preexec_fn"] = preexec_fn
    if creationflags:
        kwargs["creationflags"] = creationflags
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            env=env, cwd=cwd, shell=False, **kwargs)
    if on_start is not None:
        try:
            on_start(proc)
        except Exception:  # noqa: BLE001
            pass
    chunks: list[bytes] = []
    state = {"n": 0, "flag": "ok"}

    def kill() -> None:
        if on_kill is not None:
            try:
                on_kill()
            except Exception:  # noqa: BLE001
                pass
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass

    def write_stdin() -> None:
        try:
            proc.stdin.write(stdin_bytes)
            proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass

    def read_stdout() -> None:
        try:
            while True:
                data = proc.stdout.read(65536)
                if not data:
                    return
                state["n"] += len(data)
                if state["n"] > max_out:
                    state["flag"] = "output_too_large"
                    kill()
                    return
                chunks.append(data)
        except Exception:  # noqa: BLE001
            return

    tw = threading.Thread(target=write_stdin, daemon=True)
    tr = threading.Thread(target=read_stdout, daemon=True)
    tw.start()
    tr.start()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        if state["flag"] == "ok":
            state["flag"] = "timeout"
        kill()
        try:
            proc.wait(timeout=5)
        except Exception:  # noqa: BLE001
            pass
    tr.join(timeout=5)
    tw.join(timeout=1)
    return proc.returncode, b"".join(chunks), state["flag"]
