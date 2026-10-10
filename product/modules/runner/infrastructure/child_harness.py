"""Child-process harness. Executes learner text and reports raw outputs ONLY.

Runs as `python -I -c <this file's text>` inside the container (or the restricted
subprocess). Standard library only. It receives JSON on stdin and never receives
expected values or expected queries (SR-22): the trusted parent compares outputs.

Defence in depth (the container is the boundary): an audit hook refuses sockets,
process creation, file writes and reads outside the interpreter prefix. A refused
action is recorded and the whole run reports `blocked` even if the learner catches
the exception.
"""
import io
import json
import os
import sys


def _main():
    sys.dont_write_bytecode = True
    raw = sys.stdin.buffer.read()
    payload = json.loads(raw.decode("utf-8"))
    nonce = payload["nonce"]
    real_out = sys.stdout
    violations = []

    def emit(obj):
        real_out.write(nonce + json.dumps(obj, allow_nan=False) + "\n")
        real_out.flush()

    # ------------------------------------------------------------ guard
    roots = set()
    for p in (sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix):
        try:
            roots.add(os.path.normcase(os.path.realpath(p)))
        except Exception:
            pass
    roots = tuple(roots)
    blocked_modules = {"subprocess", "socket", "_socket", "ctypes", "_ctypes", "multiprocessing",
                       "pty", "_posixsubprocess", "_winapi", "ftplib", "smtplib", "telnetlib",
                       "http.client", "urllib.request", "asyncio.subprocess"}
    blocked_prefix = ("socket.", "subprocess.", "ctypes.", "os.exec", "os.spawn", "os.posix_spawn",
                      "os.fork", "os.system", "os.remove", "os.rename", "os.replace", "os.rmdir",
                      "os.mkdir", "os.chmod", "os.chown", "os.truncate", "os.symlink", "os.link",
                      "os.chdir", "os.kill", "os.putenv", "os.startfile",
                      "shutil.", "_winapi.", "pty.", "urllib.", "http.client.", "smtplib.", "ftplib.",
                      "webbrowser.", "winreg.", "glob.glob", "tempfile.")
    write_bits = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
    armed = [False]
    devnull = {os.devnull, "/dev/null", "nul"}

    def hook(event, args):
        if not armed[0]:
            return
        why = None
        if event == "open":
            path, mode, flags = args[0], args[1], args[2]
            if isinstance(path, int):
                return
            if isinstance(mode, str) and any(c in mode for c in "wax+"):
                why = "file_write"
            elif mode is None and isinstance(flags, int) and flags & write_bits:
                why = "file_write"
            else:
                try:
                    real = os.path.normcase(os.path.realpath(os.fsdecode(path)))
                except Exception:
                    real = ""
                if os.fsdecode(path) in devnull or os.fsdecode(path) == "<submission>":
                    return
                if not (real and any(real == r or real.startswith(r + os.sep) for r in roots)):
                    why = "file_read"
        elif event in ("os.listdir", "os.scandir"):
            try:
                target = args[0] if args and args[0] is not None else "."
                if isinstance(target, int):
                    why = event
                else:
                    real = os.path.normcase(os.path.realpath(os.fsdecode(target)))
                    if not any(real == r or real.startswith(r + os.sep) for r in roots):
                        why = event
            except Exception:
                why = event
        elif event == "import":
            if args[0] in blocked_modules:
                why = "import"
        elif event.startswith(blocked_prefix):
            why = event
        if why:
            violations.append(why)
            raise PermissionError("operation not permitted in the sandbox")

    class CappedWriter(io.TextIOBase):
        def __init__(self, cap):
            self.cap, self.n, self.parts, self.truncated = cap, 0, [], False

        def writable(self):
            return True

        def write(self, s):
            if self.n < self.cap:
                take = s[: self.cap - self.n]
                self.parts.append(take)
                self.n += len(take)
                if len(take) < len(s):
                    self.truncated = True
            else:
                self.truncated = True
            return len(s)

        def value(self):
            return "".join(self.parts)

    def safe_json(value):
        text = json.dumps(value, allow_nan=False)
        return json.loads(text)

    kind = payload["kind"]
    code = payload["code"]
    max_stdout = int(payload.get("max_stdout", 8192))
    results = []
    module_stdout = ""

    try:
        if kind == "python":
            import signal
            has_alarm = hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer")

            class _CaseTimeout(BaseException):
                pass

            def _on_alarm(signum, frame):
                raise _CaseTimeout()

            if has_alarm:
                signal.signal(signal.SIGALRM, _on_alarm)
            case_seconds = float(payload.get("case_seconds", 2))
            sys.addaudithook(hook)
            armed[0] = True
            ns = {"__name__": "__submission__", "__builtins__": __builtins__}
            buf = CappedWriter(max_stdout)
            sys.stdout = buf
            load_error = None
            try:
                if has_alarm:
                    signal.setitimer(signal.ITIMER_REAL, case_seconds * 2)
                exec(compile(code, "<submission>", "exec"), ns)
            except _CaseTimeout:
                load_error = ("timeout", "")
            except SyntaxError as e:
                load_error = ("syntax", "line %s" % (e.lineno,))
            except BaseException as e:  # noqa: BLE001
                load_error = ("exception", type(e).__name__[:40])
            finally:
                if has_alarm:
                    signal.setitimer(signal.ITIMER_REAL, 0)
            module_stdout = buf.value()
            if load_error is not None:
                sys.stdout = real_out
                armed[0] = False
                emit({"v": 1, "load_error": list(load_error), "violations": violations,
                      "module_stdout": module_stdout, "results": []})
                return
            fn = ns.get(payload["function"])
            for case in payload["cases"]:
                rec = {"id": case["id"], "ok": False, "etype": "", "emsg": "", "value": None, "stdout": ""}
                if not callable(fn):
                    rec["etype"] = "missing_function"
                    results.append(rec)
                    continue
                cbuf = CappedWriter(max_stdout)
                sys.stdout = cbuf
                try:
                    if has_alarm:
                        signal.setitimer(signal.ITIMER_REAL, case_seconds)
                    value = fn(*case.get("args", []), **case.get("kwargs", {}))
                    if has_alarm:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    try:
                        rec["value"] = safe_json(value)
                        rec["ok"] = True
                    except Exception:  # noqa: BLE001
                        rec["etype"] = "not_serialisable"
                except _CaseTimeout:
                    rec["etype"] = "timeout"
                except BaseException as e:  # noqa: BLE001
                    if has_alarm:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    rec["etype"] = type(e).__name__[:40]
                    rec["emsg"] = str(e)[:120]
                finally:
                    if has_alarm:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                    sys.stdout = real_out
                rec["stdout"] = cbuf.value()
                results.append(rec)
            sys.stdout = real_out
            armed[0] = False
            emit({"v": 1, "load_error": None, "violations": violations,
                  "module_stdout": module_stdout, "results": results})
        elif kind == "sql":
            import sqlite3
            max_rows = int(payload["max_rows"])
            budget = int(payload["step_budget"])
            sys.addaudithook(hook)
            armed[0] = True
            SELECT, READ, FUNCTION, RECURSIVE = 21, 20, 31, 33

            def authorizer(action, a1, a2, db, src):
                if action in (SELECT, READ, RECURSIVE):
                    return sqlite3.SQLITE_OK
                if action == FUNCTION and str(a2).lower() not in ("load_extension",):
                    return sqlite3.SQLITE_OK
                return sqlite3.SQLITE_DENY

            def norm(v):
                if isinstance(v, bytes):
                    return v.hex()
                if isinstance(v, float) and v != v:
                    return None
                return v

            for case in payload["cases"]:
                rec = {"id": case["id"], "ok": False, "etype": "", "rows": None}
                conn = sqlite3.connect(":memory:")
                try:
                    conn.executescript(case["setup_sql"])
                    conn.execute("PRAGMA query_only=ON")
                    conn.execute("PRAGMA max_page_count=2000")
                    conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1000000)
                    conn.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 30000)
                    conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
                    state = {"n": 0}

                    def progress():
                        state["n"] += 1
                        return 1 if state["n"] > budget else 0

                    conn.set_authorizer(authorizer)
                    conn.set_progress_handler(progress, 1000)
                    stmt = code.strip()
                    parts = stmt.lstrip("( \t\r\n").split(None, 1)
                    first = parts[0].lower() if parts else ""
                    if first not in ("select", "with", "values"):
                        rec["etype"] = "not_authorized"
                        results.append(rec)
                        conn.close()
                        continue
                    cur = conn.execute(stmt)
                    fetched = cur.fetchmany(max_rows + 1)
                    if len(fetched) > max_rows:
                        rec["etype"] = "too_many_rows"
                    else:
                        rec["rows"] = [[norm(c) for c in row] for row in fetched]
                        rec["ok"] = True
                except sqlite3.DatabaseError as e:
                    msg = str(e).lower()
                    if "one statement" in msg:
                        rec["etype"] = "multi_statement"
                    elif "interrupt" in msg:
                        rec["etype"] = "timeout"
                    elif "not authorized" in msg or "prohibited" in msg:
                        rec["etype"] = "not_authorized"
                    else:
                        rec["etype"] = "sql_error"
                except (sqlite3.Warning, ValueError, OverflowError) as e:
                    rec["etype"] = "multi_statement" if "one statement" in str(e).lower() else "sql_error"
                finally:
                    try:
                        conn.close()
                    except Exception:  # noqa: BLE001
                        pass
                results.append(rec)
            armed[0] = False
            emit({"v": 1, "load_error": None, "violations": violations,
                  "module_stdout": "", "results": results})
        else:
            emit({"v": 1, "load_error": ["bad_kind", ""], "violations": [], "module_stdout": "", "results": []})
    except BaseException as e:  # noqa: BLE001
        sys.stdout = real_out
        emit({"v": 1, "load_error": ["harness", type(e).__name__[:40]], "violations": violations,
              "module_stdout": "", "results": []})


_main()
