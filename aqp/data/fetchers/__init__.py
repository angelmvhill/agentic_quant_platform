"""Bundled data-engine nodes for local development."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from aqp.data.engine.nodes import NodeContext, SinkNode, SourceNode, TransformNode
from aqp.data.engine.registry import register_node


@register_node("source.local_file")
class LocalFileSource(SourceNode):
    """Read a local CSV or Parquet file into row dictionaries."""

    description = "Read a local CSV or Parquet file."
    tags = ["local", "file"]

    def read(self, _context: NodeContext) -> list[dict[str, Any]]:
        path = Path(str(self.kwargs.get("path") or ""))
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)
        return frame.to_dict(orient="records")

    def probe(self) -> dict[str, Any]:
        path = Path(str(self.kwargs.get("path") or ""))
        return {"ok": path.exists(), "path": str(path)}


@register_node("transform.arrow_select")
class SelectTransform(TransformNode):
    """Keep only selected columns."""

    description = "Select a subset of columns."
    tags = ["select"]

    def apply(self, rows: list[dict[str, Any]], _context: NodeContext) -> list[dict[str, Any]]:
        columns = [str(c) for c in self.kwargs.get("columns", [])]
        if not columns:
            return rows
        return [{key: row.get(key) for key in columns} for row in rows]


@register_node("sink.memory")
class MemorySink(SinkNode):
    """Dry-run sink for validating manifests without persistence."""

    description = "Dry-run sink that reports row counts."
    tags = ["dry-run"]

    def write(self, rows: list[dict[str, Any]], context: NodeContext) -> dict[str, Any]:
        return {"rows_written": len(rows), "tables": [f"{context.namespace}.{context.name}"]}


@register_node("sink.iceberg")
class IcebergSink(MemorySink):
    """Iceberg-compatible sink placeholder for manifest validation."""

    description = "Iceberg sink contract; use pipeline ingest tasks for durable writes."
    tags = ["iceberg"]
