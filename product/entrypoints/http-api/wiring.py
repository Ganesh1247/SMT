"""Composition: load each module's api, configure it, and collect routers. Wiring only, no business logic."""
from __future__ import annotations

import importlib
import inspect
import logging
from typing import Any, Mapping, Optional

from config import Settings

log = logging.getLogger("crucible.wiring")

CORE = ("identity", "evidence", "scoring", "assessment")
REQUIRED_EXTERNAL = ("runner", "integrity")
OPTIONAL = ("intelligence", "interview", "review", "hr")
ROUTER_ORDER = ("identity", "assessment", "scoring", "evidence", "integrity", "interview", "review", "hr",
                "intelligence", "runner")


class StartupError(RuntimeError):
    """A required module is missing or failed to configure; the message says what to do."""


def load_api(name: str) -> Optional[Any]:
    try:
        return importlib.import_module(f"{name}.api")
    except ModuleNotFoundError as exc:
        if exc.name in (name, f"{name}.api"):
            return None
        raise  # the module exists but one of its own imports is broken: surface it


def load_all(settings: Settings, override: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    apis: dict[str, Any] = dict(override or {})
    for name in CORE + REQUIRED_EXTERNAL + OPTIONAL:
        if name in apis:
            continue
        api = load_api(name)
        if api is None:
            if name in CORE or (name in REQUIRED_EXTERNAL and not settings.allow_missing_modules):
                raise StartupError(
                    f"Required module '{name}' is not available (expected product/modules/{name}/api). "
                    "Build it or, for local development only, set CRUCIBLE_ALLOW_MISSING_MODULES=true "
                    "(runs, recording and prechecks will then be unavailable).")
            log.warning("module_missing", extra={"event": "module_missing", "mod": name})
            continue
        apis[name] = api
    return apis


def configure_all(apis: Mapping[str, Any], settings: Settings) -> None:
    identity, evidence, scoring = apis["identity"], apis["evidence"], apis["scoring"]
    identity.configure(data_dir=settings.data_dir, cookie_secure=settings.cookie_secure)
    evidence.configure(data_dir=settings.data_dir)
    scoring.configure(data_dir=settings.data_dir)
    apis["assessment"].configure(data_dir=settings.data_dir, runner=apis.get("runner"),
                                 integrity=apis.get("integrity"), intelligence=apis.get("intelligence"))
    if "runner" in apis:
        count = apis["assessment"].register_tasks()
        log.info("tasks_registered", extra={"event": "tasks_registered", "count": count})
    available = dict(apis, data_dir=settings.data_dir)
    for name in ("interview", "review", "hr"):
        api = apis.get(name)
        configure = getattr(api, "configure", None)
        if configure is None:
            continue
        params = inspect.signature(configure).parameters
        kwargs = {p: available[p] for p in params if p in available and p != name}
        missing = [p for p, spec in params.items() if spec.default is inspect.Parameter.empty
                   and p not in kwargs and spec.kind in (spec.POSITIONAL_OR_KEYWORD, spec.KEYWORD_ONLY)]
        if missing:
            log.warning("module_not_configured", extra={"event": "module_not_configured", "mod": name})
            continue
        configure(**kwargs)


def routers(apis: Mapping[str, Any]):
    for name in ROUTER_ORDER:
        router = getattr(apis.get(name), "router", None)
        if router is not None and getattr(router, "routes", None):
            yield name, router


def wire_dependencies(app: Any, apis: Mapping[str, Any]) -> None:
    integrity = apis.get("integrity")
    placeholder = getattr(integrity, "current_user_dependency", None)
    if placeholder is not None:
        app.dependency_overrides[placeholder] = apis["identity"].current_user
