"""Hybrid Airbyte connector registry."""
from __future__ import annotations

from aqp.data.airbyte.models import (
    AirbyteConnectionSpec,
    AirbyteConnectorDefinition,
    AirbyteDiscoverRequest,
    AirbyteEmbeddedReadRequest,
    AirbyteSyncRequest,
    ConnectorKind,
    ConnectorRuntime,
    SyncStatus,
)

_CONNECTORS = [
    AirbyteConnectorDefinition(
        id="alpha-vantage",
        name="Alpha Vantage",
        kind=ConnectorKind.SOURCE,
        tags=["market-data", "fundamentals"],
        streams=[{"name": "timeseries_daily"}, {"name": "overview"}],
    ),
    AirbyteConnectorDefinition(
        id="local-json",
        name="Local JSON",
        kind=ConnectorKind.SOURCE,
        tags=["local", "embedded"],
        streams=[{"name": "records"}],
    ),
]


def list_connectors(kind: ConnectorKind | None = None, tag: str | None = None):
    rows = _CONNECTORS
    if kind is not None:
        rows = [c for c in rows if c.kind == kind]
    if tag:
        rows = [c for c in rows if tag in c.tags]
    return rows


def list_connector_ids() -> list[str]:
    return [c.id for c in _CONNECTORS]


def get_connector(connector_id: str) -> AirbyteConnectorDefinition:
    for connector in _CONNECTORS:
        if connector.id == connector_id:
            return connector
    raise KeyError(connector_id)


def connector_summary() -> dict:
    return {
        "total": len(_CONNECTORS),
        "sources": len([c for c in _CONNECTORS if c.kind == ConnectorKind.SOURCE]),
        "destinations": len([c for c in _CONNECTORS if c.kind == ConnectorKind.DESTINATION]),
        "connectors": [c.model_dump(mode="json") for c in _CONNECTORS],
    }


def stream_entity_mappings(connector_id: str) -> list[dict]:
    connector = get_connector(connector_id)
    return [{"stream": s["name"], "entity": "instrument"} for s in connector.streams]


__all__ = [
    "AirbyteConnectionSpec",
    "AirbyteConnectorDefinition",
    "AirbyteDiscoverRequest",
    "AirbyteEmbeddedReadRequest",
    "AirbyteSyncRequest",
    "ConnectorKind",
    "ConnectorRuntime",
    "SyncStatus",
    "connector_summary",
    "get_connector",
    "list_connector_ids",
    "list_connectors",
    "stream_entity_mappings",
]
