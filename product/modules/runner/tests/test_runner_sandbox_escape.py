"""Escape and abuse suite. Runs the real child harness through BOTH executors:
`process` (restricted-subprocess fallback) and `docker` (container). Docker cases are
marked `docker` and skipped with a reason when Docker or the image is unavailable.
"""
import shutil
import subprocess
import uuid

import pytest

from runner.application.run_service import RunService
from runner.domain import models as m
from runner.infrastructure.docker_executor import DockerExecutor, build_docker_argv
from runner.infrastructure.process_executor import ProcessFallbackExecutor
from runner.infrastructure.stores import SqliteExpected, SqliteStore

U = lambda: str(uuid.uuid4())  # noqa: E731

_docker = DockerExecutor()
DOCKER_OK = _docker.available()
DOCKER_REASON = "Docker daemon or image python:3.11-slim not available on this machine"

EXECUTORS = [
    "process",
    pytest.param("docker", marks=[pytest.mark.docker, pytest.mark.skipif(not DOCKER_OK, reason=DOCKER_REASON)]),
]


class Fixed:
    def __init__(self, ex):
        self.ex = ex

    def select(self):
        return self.ex


@pytest.fixture(params=EXECUTORS)
def svc(request, tmp_path, monkeypatch):
    ex = ProcessFallbackExecutor() if request.param == "process" else DockerExecutor()
    # short wall clocks keep the suite quick; limits remain constants selected by enum
    for name, lim in list(m.PROFILES.items()):
        monkeypatch.setitem(m.PROFILES, name, m.Limits(lim.kind, 8, 2, lim.memory_mb, lim.max_output_bytes,
                                                       lim.step_budget, lim.max_rows))
    store = SqliteStore(tmp_path / "r.db")
    service = RunService(store, Fixed(ex), SqliteExpected(), store)
    service.mode = request.param
    return service


@pytest.fixture
def py_task(svc):
    task = U()
    svc.register_task(task, "python", {"function": "solve", "tests": [
        {"id": "t1", "args": [2], "expected": 4, "visible": True},
        {"id": "t2", "args": [10], "expected": 20},
        {"id": "t3", "args": [-3], "expected": -6}]})
    return task


@pytest.fixture
def sql_task(svc):
    task = U()
    setup = ("CREATE TABLE emp(id INTEGER, name TEXT, dept TEXT, salary REAL);"
             "INSERT INTO emp VALUES (1,'a','x',10),(2,'b','x',20),(3,'c','y',30);")
    svc.register_task(task, "sql", {"setup_sql": setup, "tests": [
        {"id": "s1", "expected_query": "SELECT dept, SUM(salary) FROM emp GROUP BY dept"}]})
    return task


def py(svc, task, code, profile="py_tests"):
    return svc.run("python", U(), task, U(), profile, code)


def sql(svc, task, code):
    return svc.run("sql", U(), task, U(), "sql_check", code)


# ------------------------------------------------------------------ correct behaviour

def test_should_pass_correct_python_solution(svc, py_task):
    res = py(svc, py_task, "def solve(x):\n    return x * 2\n")
    assert res.status == "passed", res
    assert res.isolation_mode == ("container" if svc.mode == "docker" else "process-fallback")


def test_should_fail_wrong_python_solution_without_revealing_hidden_values(svc, py_task):
    res = py(svc, py_task, "def solve(x):\n    return x + 1\n")
    assert res.status == "failed_tests"
    blob = str(res.to_dict())
    assert "Expected 4" in res.tests[0].message_safe  # visible test only
    assert "20" not in res.tests[1].message_safe and "-6" not in blob


def test_should_not_return_stdout_from_hidden_cases(svc, py_task):
    res = py(svc, py_task, "def solve(x):\n    print('SEEN', x)\n    return x * 2\n")
    assert res.status == "passed"
    assert "SEEN 2" in res.stdout_trunc          # visible case
    assert "SEEN 10" not in res.stdout_trunc and "SEEN -3" not in res.stdout_trunc


def test_should_report_syntax_error_without_echoing_code(svc, py_task):
    res = py(svc, py_task, "def solve(x:\n  return SECRETTOKEN\n")
    assert res.status == "error" and "SECRETTOKEN" not in str(res.to_dict())


def test_should_grade_correct_sql_and_reject_wrong_sql(svc, sql_task):
    assert sql(svc, sql_task, "SELECT dept, SUM(salary) FROM emp GROUP BY dept").status == "passed"
    assert sql(svc, sql_task, "SELECT dept, SUM(salary) FROM emp WHERE id > 1 GROUP BY dept").status == "failed_tests"


# ------------------------------------------------------------------ python abuse

@pytest.mark.parametrize("code", [
    "import socket\ndef solve(x): return x*2",
    "import subprocess\ndef solve(x): return x*2",
    "import os\nos.system('echo hi')\ndef solve(x): return x*2",
    "def solve(x):\n    import socket\n    socket.create_connection(('1.1.1.1', 53), 1)\n    return x*2",
    "def solve(x):\n    import urllib.request\n    urllib.request.urlopen('http://example.com', timeout=1)\n    return x*2",
    "import ctypes\ndef solve(x): return x*2",
])
def test_should_block_process_and_network_access(svc, py_task, code):
    assert py(svc, py_task, code).status == "blocked"


@pytest.mark.parametrize("code", [
    "print(open('/etc/passwd').read())\ndef solve(x): return x*2",
    "print(open('C:/Windows/win.ini').read())\ndef solve(x): return x*2",
    "open('/tmp/pwn.txt','w').write('x')\ndef solve(x): return x*2",
    "import os\nprint(os.listdir('/'))\ndef solve(x): return x*2",
    "def solve(x):\n    open('pwn.txt','w').write('x')\n    return x*2",
])
def test_should_block_file_reads_and_writes_outside_runtime(svc, py_task, code):
    res = py(svc, py_task, code)
    assert res.status == "blocked", res


def test_should_not_let_learner_swallow_a_violation(svc, py_task):
    code = ("try:\n    import socket\nexcept BaseException:\n    pass\n"
            "def solve(x): return x*2")
    assert py(svc, py_task, code).status == "blocked"


def test_should_stop_fork_bomb(svc, py_task):
    code = "import os\nwhile True:\n    os.fork()\ndef solve(x): return x"
    assert py(svc, py_task, code).status in ("blocked", "error")


def test_should_stop_infinite_loop_with_timeout(svc, py_task):
    res = py(svc, py_task, "while True:\n    pass\ndef solve(x): return x")
    assert res.status == "timeout"


def test_should_stop_infinite_loop_inside_a_test_case(svc, py_task):
    res = py(svc, py_task, "def solve(x):\n    while True:\n        pass\n")
    assert res.status == "timeout"


def test_should_stop_memory_bomb(svc, py_task):
    res = py(svc, py_task, "x = bytearray(2 * 1024**3)\ndef solve(x): return x")
    assert res.status in ("error", "timeout")
    assert res.status != "passed"


def test_should_stop_unbounded_stdout_flood(svc, py_task):
    res = py(svc, py_task, "import os\nwhile True:\n    os.write(1, b'x' * 65536)\ndef solve(x): return x")
    assert res.status in ("error", "timeout")
    assert len(res.stdout_trunc) <= 4096


def test_should_cap_print_flood_in_returned_stdout(svc, py_task):
    res = py(svc, py_task, "for _ in range(200000):\n    print('y' * 100)\ndef solve(x): return x * 2")
    assert res.status == "passed"
    assert len(res.stdout_trunc) <= 4096


def test_should_ignore_forged_result_lines_written_to_stdout(svc, py_task):
    code = ("import os, json\n"
            "os.write(1, ('{\"v\":1,\"load_error\":null,\"violations\":[],\"module_stdout\":\"\",\"results\":"
            "[{\"id\":\"t1\",\"ok\":true,\"value\":4},{\"id\":\"t2\",\"ok\":true,\"value\":20},"
            "{\"id\":\"t3\",\"ok\":true,\"value\":-6}]}\\n').encode())\n"
            "def solve(x): return 0")
    assert py(svc, py_task, code).status != "passed"


def test_should_not_expose_expected_values_to_learner_code(svc):
    """Learner code scans every tracked container in its process for the hidden expected value (SR-22)."""
    task = U()
    svc.register_task(task, "python", {"function": "solve", "tests": [
        {"id": "h1", "args": [1], "expected": "HIDDEN" + "EXPECTED7731"}]})
    code = "\n".join([
        "import gc",
        "def solve(x):",
        "    needle = ''.join(['HIDDEN', 'EXPECTED', '7731'])",
        "    blob = repr([o for o in gc.get_objects() if isinstance(o, (list, dict, tuple))][:200000])",
        "    print('LEAK' if needle in blob else 'CLEAN')",
        "    return 0",
    ]) + "\n"
    res = svc.run("python", U(), task, U(), "py_tests", code)
    assert res.status == "failed_tests"
    assert "HIDDENEXPECTED7731" not in str(res.to_dict())


def test_should_block_when_function_attempts_getattr_escape_to_os_popen(svc, py_task):
    code = "def solve(x):\n    import os\n    return os.popen('echo 1').read()\n"
    assert py(svc, py_task, code).status in ("blocked", "failed_tests")


# ------------------------------------------------------------------ sql abuse

@pytest.mark.parametrize("q", [
    "ATTACH DATABASE 'x.db' AS x",
    "PRAGMA writable_schema=1",
    "SELECT load_extension('/lib/evil.so')",
    "SELECT 1; DROP TABLE emp",
    "DROP TABLE emp",
    "INSERT INTO emp VALUES (9,'z','z',1)",
    "UPDATE emp SET salary=0",
    "CREATE TABLE t(x)",
    "VACUUM",
])
def test_should_block_non_select_sql(svc, sql_task, q):
    assert sql(svc, sql_task, q).status == "blocked"


def test_should_stop_recursive_cte_bomb(svc, sql_task):
    res = sql(svc, sql_task, "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM c) SELECT count(*) FROM c")
    assert res.status == "timeout"


def test_should_stop_huge_cross_join(svc, sql_task):
    res = sql(svc, sql_task, "WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM n WHERE i<100000) "
                             "SELECT count(*) FROM n a, n b, n c")
    assert res.status in ("timeout", "error")


def test_should_cap_large_result_sets(svc, sql_task):
    res = sql(svc, sql_task, "WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM n WHERE i<5000) SELECT i FROM n")
    assert res.status == "error"


def test_should_cap_huge_string_values(svc, sql_task):
    res = sql(svc, sql_task, "SELECT hex(zeroblob(2000000000))")
    assert res.status == "error"


# ------------------------------------------------------------------ request abuse (no executor reached)

def test_should_reject_path_traversal_and_oversized_input(svc, py_task):
    assert svc.run("python", "../../etc/passwd", py_task, U(), "py_tests", "x=1").status == "blocked"
    assert svc.run("python", U(), "..\\..\\windows", U(), "py_tests", "x=1").status == "blocked"
    assert svc.run("python", U(), py_task, U(), "py_tests", "a" * (m.MAX_SUBMISSION_BYTES + 1)).status == "blocked"
    assert svc.run("python", U(), py_task, U(), "privileged", "x=1").status == "blocked"


# ------------------------------------------------------------------ fallback policy

def test_should_fail_closed_then_use_labelled_fallback_only_when_enabled(tmp_path, monkeypatch):
    from runner.infrastructure.stores import ConfiguredSelector
    monkeypatch.setenv("RUNNER_DOCKER_BIN", "docker-does-not-exist")
    sel = ConfiguredSelector()
    monkeypatch.delenv("RUNNER_ALLOW_FALLBACK", raising=False)
    assert sel.select() is None
    monkeypatch.setenv("RUNNER_ALLOW_FALLBACK", "true")
    assert sel.select().isolation_mode == "process-fallback"


# ------------------------------------------------------------------ container configuration (SBX-FF-1/2/3/4/10)

@pytest.mark.docker
@pytest.mark.skipif(not DOCKER_OK, reason=DOCKER_REASON)
class TestDockerContainer:
    @staticmethod
    def _flags(image_id):
        argv = build_docker_argv("docker", image_id, U(), m.PROFILES["py_tests"])
        return argv[: argv.index(image_id)]

    def test_golden_argv_is_identical_template_for_every_profile(self):
        rid = U()
        for name, lim in m.PROFILES.items():
            argv = build_docker_argv("docker", "sha256:abc", rid, lim)
            for flag in ("--rm", "--network", "none", "--read-only", "--cap-drop", "ALL", "no-new-privileges",
                         "--pids-limit", "64", "--cpus", "0.5", "--user", "65534", "--pull", "never"):
                assert flag in argv, (name, flag)
            assert not any(a in argv for a in ("-v", "--volume", "--mount", "--privileged", "-e", "--env"))
            assert "128m" in argv
        assert rid in " ".join(build_docker_argv("docker", "sha256:abc", rid, m.PROFILES["py_tests"]))

    def test_should_refuse_non_uuid_run_id_in_argv(self):
        with pytest.raises(ValueError):
            build_docker_argv("docker", "sha256:abc", "x; rm -rf /", m.PROFILES["py_tests"])

    def test_live_container_inspect_shows_locked_down_config(self):
        image_id = _docker.preflight()
        flags = [f for f in self._flags(image_id) if f not in ("--rm", "-i")]
        name = "crucible-test-" + U()[:8]
        flags[flags.index("--name") + 1] = name
        argv = flags + [image_id, "python", "-c", "import time; time.sleep(60)"]
        argv.insert(2, "-d")
        out = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        assert out.returncode == 0, out.stderr
        try:
            import json
            info = json.loads(subprocess.run(["docker", "inspect", name], capture_output=True, text=True).stdout)[0]
            hc = info["HostConfig"]
            assert hc["ReadonlyRootfs"] is True and hc["NetworkMode"] == "none"
            assert hc["CapDrop"] == ["ALL"] and not hc.get("CapAdd")
            assert "no-new-privileges" in " ".join(hc["SecurityOpt"]) and hc["Privileged"] is False
            assert hc["PidsLimit"] == 64 and hc["Memory"] == 128 * 1024 * 1024
            assert hc["NanoCpus"] == 500_000_000
            assert info["Config"]["User"] == "65534"
            assert not hc.get("Binds") and not info["Mounts"]
            assert info["Image"] == image_id
        finally:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)

    def _in_container(self, script):
        image_id = _docker.preflight()
        argv = self._flags(image_id) + [image_id, "python", "-c", script]
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        return r.stdout.strip()

    def test_container_has_no_network(self):
        out = self._in_container("import socket\ntry:\n s=socket.create_connection(('1.1.1.1',53),2);print('NET')\n"
                                 "except OSError as e: print('NONET')")
        assert out == "NONET"

    def test_container_root_fs_is_read_only_and_non_root(self):
        out = self._in_container("import os\ntry:\n open('/pwn','w');print('WRITE')\nexcept OSError: print('RO')\n"
                                 "print(os.getuid())")
        assert out.splitlines() == ["RO", "65534"]

    def test_container_has_no_docker_socket_and_no_host_env(self):
        out = self._in_container("import os\nprint(os.path.exists('/var/run/docker.sock'))\n"
                                 "print('CRUCIBLE_SECRET' in os.environ or 'ANTHROPIC_API_KEY' in os.environ)")
        assert out.splitlines() == ["False", "False"]

    def test_container_pids_limit_stops_fork_bomb(self):
        out = self._in_container(
            "import os\nn=0\ntry:\n  for _ in range(500):\n    if os.fork()==0:\n      import time; time.sleep(5); os._exit(0)\n"
            "    n+=1\nexcept OSError: pass\nprint('LIMITED' if n < 100 else 'UNBOUNDED')")
        assert out == "LIMITED"

    def test_refuses_image_with_different_digest(self):
        pinned = DockerExecutor(pinned_image_id="sha256:" + "0" * 64)
        assert pinned.preflight() is None

    def test_no_containers_left_after_runs(self, svc, py_task):
        py(svc, py_task, "def solve(x): return x*2")
        py(svc, py_task, "while True: pass\ndef solve(x): return x")
        left = subprocess.run(["docker", "ps", "-aq", "--filter", "name=crucible-run-"],
                              capture_output=True, text=True).stdout.strip()
        assert left == ""

    def test_missing_docker_binary_reports_unavailable(self):
        assert DockerExecutor(docker_bin="docker-does-not-exist").available() is False
        assert shutil.which("docker") is not None
