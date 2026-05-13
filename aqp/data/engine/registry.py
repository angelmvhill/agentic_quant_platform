"""Process-local registry for data-engine nodes."""
from __future__ import annotations

from typing import Any

from aqp.data.engine.nodes import BaseNode, NodeKind

_NODES: dict[str, type[BaseNode]] = {}


def register_node(name: str):
    def _decorator(cls: type[BaseNode]) -> type[BaseNode]:
        _NODES[name] = cls
        return cls

    return _decorator


def get_node_class(name: str) -> type[BaseNode]:
    if name not in _NODES:
        raise KeyError(f"unknown node: {name}")
    return _NODES[name]


def build_node(name: str, kwargs: dict[str, Any] | None = None) -> BaseNode:
    return get_node_class(name)(**(kwargs or {}))


def list_nodes() -> list[dict[str, Any]]:
    rows = []
    for name, cls in sorted(_NODES.items()):
        rows.append(
            {
                "name": name,
                "kind": cls.kind.value,
                "description": getattr(cls, "description", "") or "",
                "tags": list(getattr(cls, "tags", []) or []),
                "module": cls.__module__,
                "class_name": cls.__name__,
            }
        )
    return rows


def list_nodes_by_kind(kind: NodeKind) -> list[dict[str, Any]]:
    return [row for row in list_nodes() if row["kind"] == kind.value]
