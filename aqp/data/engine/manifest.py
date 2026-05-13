"""Pydantic manifest models for declarative data pipelines."""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ComputeBackendKind(StrEnum):
    AUTO = "auto"
    LOCAL = "local"
    DASK = "dask"
    RAY = "ray"


class NodeSpec(BaseModel):
    name: str
    kwargs: dict[str, Any] = Field(default_factory=dict)


class ComputeSpec(BaseModel):
    backend: ComputeBackendKind = ComputeBackendKind.AUTO
    chunk_rows: int = 50_000


class SchedulingSpec(BaseModel):
    cron: str | None = None
    enabled: bool = False


class PipelineManifest(BaseModel):
    name: str
    namespace: str = "aqp"
    description: str | None = None
    owner: str | None = None
    version: int = 1
    enabled: bool = True
    source: NodeSpec
    transforms: list[NodeSpec] = Field(default_factory=list)
    sink: NodeSpec
    compute: ComputeSpec = Field(default_factory=ComputeSpec)
    schedule: SchedulingSpec = Field(default_factory=SchedulingSpec)
    tags: list[str] = Field(default_factory=list)
