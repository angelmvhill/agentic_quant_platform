"""Pipeline object and run result."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from aqp.data.engine.manifest import PipelineManifest


@dataclass
class PipelineRunResult:
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    tables: list[str] = field(default_factory=list)
    total_rows_written: int = 0
    sink_result: dict[str, Any] = field(default_factory=dict)
    lineage: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    extras: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "tables": self.tables,
            "total_rows_written": self.total_rows_written,
            "sink_result": self.sink_result,
            "lineage": self.lineage,
            "errors": self.errors,
            "extras": self.extras,
        }


class Pipeline:
    def __init__(self, manifest: PipelineManifest) -> None:
        self.manifest = manifest

    @classmethod
    def from_manifest(cls, manifest: PipelineManifest) -> Pipeline:
        return cls(manifest)
