"""SBX-FF-5 / SR-22: only runner infrastructure may touch subprocess/Docker; no exec/eval of learner text
in domain, application or api; no cross-module imports."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IMPORTS = {"subprocess", "docker", "ctypes", "importlib", "os.system"}


def _py(layer):
    return [p for p in (ROOT / layer).rglob("*.py")]


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or ""), node.level


def test_should_confine_subprocess_and_docker_to_infrastructure():
    for layer in ("domain", "application", "api"):
        for path in _py(layer):
            names = {n.split(".")[0] for n, _ in _imports(path)}
            assert not (names & FORBIDDEN_IMPORTS), (path, names & FORBIDDEN_IMPORTS)


def test_should_not_exec_or_eval_in_trusted_layers():
    for layer in ("domain", "application", "api"):
        for path in _py(layer):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    assert node.func.id not in ("exec", "eval", "compile", "__import__"), (path, node.lineno)


def test_should_not_import_other_modules():
    allowed_top = {"runner"}
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for name, level in _imports(path):
            if level == 0 and name.split(".")[0] in {"identity", "assessment", "scoring", "evidence", "review",
                                                      "intelligence", "interview", "hr", "integrity"}:
                raise AssertionError((path, name))
        assert allowed_top
