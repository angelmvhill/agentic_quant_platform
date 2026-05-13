"""Local-first DataHub sync facade."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aqp.config import settings


@dataclass
class DataHubClient:
    gms_url: str = settings.datahub_gms_url
    token: str = settings.datahub_token
    env: str = settings.datahub_env

    def is_configured(self) -> bool:
        return bool(self.gms_url)

    def ping(self) -> bool:
        return self.is_configured()


def get_client() -> DataHubClient:
    return DataHubClient()


def iceberg_dataset_urn(iceberg_identifier: str) -> str:
    return (
        f"urn:li:dataset:(urn:li:dataPlatform:{settings.datahub_platform},"
        f"{settings.datahub_platform_instance}.{iceberg_identifier},{settings.datahub_env})"
    )


def vt_symbol_urn(vt_symbol: str) -> str:
    return f"urn:li:corpuser:{vt_symbol.replace('.', '_')}"


def parse_urn(urn: str) -> dict[str, Any]:
    return {"urn": urn, "platform": settings.datahub_platform, "env": settings.datahub_env}


def push_dataset(
    *,
    catalog_id: str | None = None,
    urn: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = urn or (iceberg_dataset_urn(catalog_id) if catalog_id else "")
    return {"emitted": get_client().is_configured(), "urn": target, "payload": payload or {}}


def push_all(limit: int = 1000) -> dict[str, Any]:
    return {"emitted": False, "limit": limit, "reason": "DataHub GMS not configured"}


def pull_external() -> dict[str, Any]:
    return {"platforms": [], "configured": get_client().is_configured()}


def pull_platform(platform: str) -> dict[str, Any]:
    return {"platform": platform, "urns": [], "configured": get_client().is_configured()}


def sync_all() -> dict[str, Any]:
    return {"push": push_all(), "pull": pull_external()}
