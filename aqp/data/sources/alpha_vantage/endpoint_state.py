"""Runtime state for Alpha Vantage endpoint inclusion and cache TTLs."""
from __future__ import annotations

import json
from typing import Any

from aqp.config import settings

from .catalog import function_by_id


def _path():
    path = settings.data_dir / "runtime" / "alpha_vantage_endpoint_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read() -> dict[str, dict[str, Any]]:
    path = _path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write(data: dict[str, dict[str, Any]]) -> None:
    _path().write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def get_state(function_id: str) -> dict[str, Any]:
    """Return persisted state for one endpoint."""
    fn = _function_ref(function_id)
    meta = _read_meta_state(fn)
    if isinstance(meta, dict):
        return dict(meta)
    return dict(_read().get(function_id, {}))


def set_state(
    function_id: str,
    *,
    enabled_for_bulk: bool | None = None,
    cache_ttl_seconds: float | None = None,
) -> dict[str, Any]:
    """Persist endpoint runtime controls."""
    fn = _function_ref(function_id)
    data = _read()
    state = dict(data.get(function_id, {}))
    if enabled_for_bulk is not None:
        state["enabled_for_bulk"] = bool(enabled_for_bulk)
    if cache_ttl_seconds is not None:
        state["cache_ttl_seconds"] = float(cache_ttl_seconds)
    data[function_id] = state
    _write(data)
    _write_meta_state(fn, state)
    return dict(state)


def _function_ref(function_id: str):
    entry = function_by_id(function_id) or {"id": function_id}

    class _FunctionRef:
        id = str(entry["id"])

    return _FunctionRef()


def _read_meta_state(fn) -> dict[str, Any] | None:
    """Compatibility hook for tests and future DatasetCatalog metadata state."""
    return _read().get(str(fn.id))


def _write_meta_state(fn, state: dict[str, Any]) -> None:
    """Compatibility hook for tests and future DatasetCatalog metadata state."""
    data = _read()
    data[str(fn.id)] = dict(state)
    _write(data)
