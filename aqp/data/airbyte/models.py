"""Airbyte pydantic models used by routes and Celery tasks."""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ConnectorKind(StrEnum):
    SOURCE = "source"
    DESTINATION = "destination"


class ConnectorRuntime(StrEnum):
    EMBEDDED = "embedded"
    FULL_AIRBYTE = "full_airbyte"


class SyncStatus(StrEnum):
    UNKNOWN = "unknown"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AirbyteConnectorDefinition(BaseModel):
    id: str
    name: str
    kind: ConnectorKind = ConnectorKind.SOURCE
    docker_image: str | None = None
    version: str | None = None
    tags: list[str] = Field(default_factory=list)
    streams: list[dict[str, Any]] = Field(default_factory=list)


class ConnectorRef(BaseModel):
    connector_id: str
    config: dict[str, Any] = Field(default_factory=dict)
    airbyte_source_id: str | None = None
    airbyte_destination_id: str | None = None


class AirbyteStreamSpec(BaseModel):
    name: str
    sync_mode: str = "full_refresh"
    destination_sync_mode: str = "append"


class AirbyteConnectionSpec(BaseModel):
    name: str
    source: ConnectorRef
    destination: ConnectorRef
    namespace: str = "aqp_airbyte"
    airbyte_connection_id: str | None = None
    catalog: dict[str, Any] = Field(default_factory=dict)
    streams: list[AirbyteStreamSpec] = Field(default_factory=list)
    entity_mappings: list[dict[str, Any]] = Field(default_factory=list)
    materialization_manifest: dict[str, Any] = Field(default_factory=dict)
    schedule: dict[str, Any] = Field(default_factory=dict)
    compute_backend: str = "auto"
    enabled: bool = True


class AirbyteDiscoverRequest(BaseModel):
    connector_id: str
    config: dict[str, Any] = Field(default_factory=dict)
    runtime: ConnectorRuntime = ConnectorRuntime.EMBEDDED


class AirbyteEmbeddedReadRequest(BaseModel):
    connector_id: str
    config: dict[str, Any] = Field(default_factory=dict)
    streams: list[str] = Field(default_factory=list)
    limit: int = 100
    dry_run: bool = True


class AirbyteSyncRequest(BaseModel):
    connection_id: str | None = None
    airbyte_connection_id: str | None = None
    wait: bool = False
