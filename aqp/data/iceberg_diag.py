"""Diagnostic helpers for the Iceberg catalog."""
from __future__ import annotations

from typing import Any

from aqp.data import iceberg_catalog


def collect_status() -> dict[str, Any]:
    """Collect health, namespace, and table status for operators."""
    health = iceberg_catalog.health_check()
    try:
        namespaces = iceberg_catalog.list_namespaces()
    except Exception as exc:  # noqa: BLE001
        namespaces = []
        health = {**health, "ok": False, "error": str(exc)}
    tables_by_namespace: dict[str, list[str]] = {}
    for namespace in namespaces:
        try:
            tables_by_namespace[namespace] = iceberg_catalog.list_tables(namespace)
        except Exception as exc:  # noqa: BLE001
            tables_by_namespace[namespace] = []
            health = {**health, "ok": False, "error": str(exc)}
    return {
        "health": health,
        "namespaces": namespaces,
        "tables_by_namespace": tables_by_namespace,
    }
