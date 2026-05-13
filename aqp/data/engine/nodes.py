"""Node contracts for the lightweight data-engine manifest runner."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeKind(StrEnum):
    SOURCE = "source"
    TRANSFORM = "transform"
    SINK = "sink"


@dataclass
class NodeContext:
    namespace: str
    name: str
    extras: dict[str, Any] = field(default_factory=dict)


class BaseNode:
    kind: NodeKind
    description = ""
    tags: list[str] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def describe(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "description": self.description,
            "tags": list(self.tags),
            "kwargs": dict(self.kwargs),
        }


class SourceNode(BaseNode):
    kind = NodeKind.SOURCE

    def read(self, context: NodeContext) -> list[dict[str, Any]]:
        return []

    def probe(self) -> dict[str, Any]:
        return {"ok": True}


class TransformNode(BaseNode):
    kind = NodeKind.TRANSFORM

    def apply(self, rows: list[dict[str, Any]], context: NodeContext) -> list[dict[str, Any]]:
        return rows


class SinkNode(BaseNode):
    kind = NodeKind.SINK

    def write(self, rows: list[dict[str, Any]], context: NodeContext) -> dict[str, Any]:
        return {"rows_written": len(rows), "tables": []}
