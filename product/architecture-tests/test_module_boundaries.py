"""Architecture fitness functions (rules/product-modules.md, api-contracts.md).

1. A module may import another module only through `<other>.api`.
2. Entrypoints (composition roots) may import modules only through their `api`.
3. Layer direction inside a module: domain imports no other layer or framework;
   application imports neither infrastructure nor api.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

PRODUCT = Path(__file__).resolve().parents[1]
MODULES = PRODUCT / "modules"
ENTRYPOINTS = PRODUCT / "entrypoints"
LAYERS = ("domain", "application", "infrastructure", "api")
FRAMEWORKS = {"fastapi", "starlette", "sqlalchemy", "uvicorn", "httpx", "requests"}


def module_names() -> set[str]:
    return {p.name for p in MODULES.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))}


def _imported_names(tree: ast.AST, package: list[str]) -> list[list[str]]:
    """Dotted names imported by a file, as component lists (relative imports resolved)."""
    out: list[list[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend(a.name.split(".") for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module.split(".") if node.module else []
            if node.level:
                anchor = package[: len(package) - (node.level - 1)] if node.level - 1 <= len(package) else []
                base = anchor + base
                if not node.module:  # `from . import x` / `from .. import x`
                    out.extend(base + [a.name] for a in node.names)
                    continue
            out.append(base)
            # `from pkg import api` imports the submodule pkg.api
            out.extend(base + [a.name] for a in node.names)
    return out


def violations_in_source(source: str, relpath: tuple[str, ...], modules: set[str]) -> list[str]:
    """relpath: path parts of the file below modules/ (e.g. ('identity','api','http.py'))."""
    tree = ast.parse(source)
    this = relpath[0]
    package = list(relpath[:-1])
    found: list[str] = []
    for dotted in _imported_names(tree, package):
        if not dotted:
            continue
        head = dotted[0]
        if head in modules and head != this:
            if len(dotted) < 2 or dotted[1] != "api":
                if len(dotted) == 1:
                    # `import other` / `from other import x` : x must be `api`; handled via the expanded names
                    continue
                found.append(f"{'/'.join(relpath)} imports {'.'.join(dotted)} (not via {head}.api)")
        if head == this and len(relpath) > 2 and relpath[1] in ("domain", "application") and len(dotted) > 1:
            layer = relpath[1]
            target = dotted[1]
            if layer == "domain" and target in LAYERS and target != "domain":
                found.append(f"{'/'.join(relpath)}: domain imports {target}")
            if layer == "application" and target in ("infrastructure", "api"):
                found.append(f"{'/'.join(relpath)}: application imports {target}")
        if len(relpath) > 2 and relpath[1] == "domain" and head in FRAMEWORKS:
            found.append(f"{'/'.join(relpath)}: domain imports framework {head}")
    return found


def entrypoint_violations(source: str, relpath: str, modules: set[str]) -> list[str]:
    tree = ast.parse(source)
    found = []
    for dotted in _imported_names(tree, []):
        if dotted and dotted[0] in modules and len(dotted) > 1 and dotted[1] != "api":
            found.append(f"entrypoints/{relpath} imports {'.'.join(dotted)} (not via {dotted[0]}.api)")
    return found


def _python_files(root: Path):
    for path in root.rglob("*.py"):
        if "node_modules" in path.parts or "__pycache__" in path.parts:
            continue
        yield path


def test_should_not_import_other_modules_except_through_api():
    mods = module_names()
    problems: list[str] = []
    for path in _python_files(MODULES):
        rel = path.relative_to(MODULES).parts
        if len(rel) < 2:
            continue
        problems += violations_in_source(path.read_text(encoding="utf-8"), rel, mods)
    assert not problems, "\n".join(problems)


def test_should_keep_entrypoints_to_module_api_imports_only():
    mods = module_names()
    problems: list[str] = []
    for path in _python_files(ENTRYPOINTS):
        problems += entrypoint_violations(path.read_text(encoding="utf-8"), str(path.relative_to(ENTRYPOINTS)), mods)
    assert not problems, "\n".join(problems)


# ---- the detector itself must be able to fail ---------------------------------------------
MODS = {"identity", "assessment", "scoring", "evidence", "runner"}


@pytest.mark.parametrize("source", [
    "from runner.domain.models import Limits",
    "import runner.infrastructure.stores",
    "from runner.application import run_service",
    "from runner import domain",
])
def test_detector_should_flag_cross_module_internals(source):
    found = violations_in_source(source, ("assessment", "application", "x.py"), MODS)
    assert found, source


@pytest.mark.parametrize("source", [
    "from runner.api import run_python",
    "import runner.api",
    "from runner import api",
    "from assessment.domain.rules import Rules",
    "import os, json",
])
def test_detector_should_allow_api_and_own_module_imports(source):
    assert violations_in_source(source, ("assessment", "application", "x.py"), MODS) == []


def test_detector_should_flag_layer_violations():
    assert violations_in_source("from assessment.infrastructure.bank import JsonBank", ("assessment", "application", "x.py"), MODS)
    assert violations_in_source("from assessment.application import plan", ("assessment", "domain", "x.py"), MODS)
    assert violations_in_source("import fastapi", ("assessment", "domain", "x.py"), MODS)


def test_detector_should_resolve_relative_imports():
    assert violations_in_source("from ...runner.domain import x", ("assessment", "application", "x.py"), MODS)
    assert violations_in_source("from ..domain.models import M", ("runner", "api", "__init__.py"), MODS) == []


def test_entrypoint_detector_should_flag_internals():
    assert entrypoint_violations("from identity.domain.model import User", "main.py", MODS)
    assert not entrypoint_violations("import identity.api as i", "main.py", MODS)
