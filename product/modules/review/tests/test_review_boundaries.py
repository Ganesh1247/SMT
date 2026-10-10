"""Architecture: review may touch other modules only through their api/ package; domain stays pure."""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = ROOT.parent
SELF = ROOT.name
OTHERS = {p.name for p in MODULES.iterdir() if p.is_dir() and p.name != SELF and (p / "MODULE.md").exists()}
FORBIDDEN_IN_DOMAIN = {"fastapi", "sqlite3", "httpx", "requests", "sqlalchemy", "os", "pathlib"}


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            base = node.module.split(".")
            for a in node.names:  # `from other import api` is the public surface
                yield base + [a.name] if len(base) == 1 else base
        elif isinstance(node, ast.ImportFrom) and node.level > 2:
            yield ["<escapes-module>"]


def test_should_only_import_other_modules_through_api():
    bad = []
    for f in ROOT.rglob("*.py"):
        if "tests" in f.relative_to(ROOT).parts:
            continue
        for parts in _imports(f):
            if parts[0] in OTHERS and (len(parts) < 2 or parts[1] != "api"):
                bad.append((f.name, ".".join(parts)))
            if parts[0] == "<escapes-module>":
                bad.append((f.name, "relative import escapes module"))
    assert bad == []


def test_domain_should_not_import_frameworks_or_io():
    bad = []
    for f in (ROOT / "domain").rglob("*.py"):
        for parts in _imports(f):
            if parts[0] in FORBIDDEN_IN_DOMAIN:
                bad.append((f.name, ".".join(parts)))
    assert bad == []
