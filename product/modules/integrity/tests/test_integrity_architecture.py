"""Module boundary and layering checks for integrity."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OTHER_MODULES = {"identity", "assessment", "scoring", "evidence", "review", "intelligence", "interview", "hr", "runner"}


def _imports(path):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or ""), node.level


def test_should_not_import_other_modules_directly():
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for name, level in _imports(path):
            assert not (level == 0 and name.split(".")[0] in OTHER_MODULES), (path, name)


def test_domain_should_import_no_frameworks_or_io():
    banned = {"fastapi", "starlette", "sqlalchemy", "sqlite3", "os", "pathlib", "shutil", "subprocess"}
    for path in (ROOT / "domain").rglob("*.py"):
        names = {n.split(".")[0] for n, _ in _imports(path)}
        assert not (names & banned), (path, names & banned)


def test_application_should_not_import_infrastructure_or_api():
    for path in (ROOT / "application").rglob("*.py"):
        for name, level in _imports(path):
            assert not name.endswith(("infrastructure", "api")) and "infrastructure" not in name.split("."), (path, name)
