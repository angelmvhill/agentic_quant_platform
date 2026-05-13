"""Embedded Airbyte-style dry-run runner."""
from __future__ import annotations

from aqp.data.airbyte import get_connector
from aqp.data.airbyte.models import AirbyteEmbeddedReadRequest


class EmbeddedAirbyteRunner:
    def check(self, connector_id: str, config: dict, *, dry_run: bool = True) -> dict:
        connector = get_connector(connector_id)
        return {"ok": True, "connector_id": connector.id, "dry_run": dry_run, "config_keys": sorted(config)}

    def discover(self, connector_id: str, config: dict, *, dry_run: bool = True) -> dict:
        connector = get_connector(connector_id)
        return {
            "connector_id": connector.id,
            "dry_run": dry_run,
            "streams": connector.streams,
            "config_keys": sorted(config),
        }

    def read(self, request: AirbyteEmbeddedReadRequest) -> dict:
        connector = get_connector(request.connector_id)
        streams = request.streams or [str(s["name"]) for s in connector.streams]
        return {
            "connector_id": connector.id,
            "dry_run": request.dry_run,
            "streams": [{"name": name, "records": []} for name in streams],
            "limit": request.limit,
        }
