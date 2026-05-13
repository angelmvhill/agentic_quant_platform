"""Lightweight unified entity-registry facade backed by in-memory rows."""
from __future__ import annotations

import uuid
from typing import Any

_ENTITIES: dict[str, dict[str, Any]] = {}
_IDENTIFIERS: dict[str, list[dict[str, Any]]] = {}
_RELATIONS: list[dict[str, Any]] = []
_ANNOTATIONS: dict[str, list[dict[str, Any]]] = {}


def list_entities(**filters: Any) -> list[dict[str, Any]]:
    rows = list(_ENTITIES.values())
    kind = filters.get("kind")
    if kind:
        rows = [row for row in rows if row.get("kind") == kind]
    return rows[int(filters.get("offset") or 0) : int(filters.get("limit") or 100)]


def search_entities(q: str, *, kind: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
    needle = q.lower()
    rows = [row for row in list_entities(kind=kind, limit=500) if needle in row["canonical_name"].lower()]
    return rows[:limit]


def upsert_entity(**payload: Any) -> dict[str, Any]:
    entity_id = str(payload.get("id") or uuid.uuid4())
    row = {
        "id": entity_id,
        "kind": str(payload.get("kind") or "unknown"),
        "canonical_name": str(payload.get("canonical_name") or payload.get("name") or entity_id),
        "short_name": payload.get("short_name"),
        "primary_identifier": payload.get("primary_identifier"),
        "primary_identifier_scheme": payload.get("primary_identifier_scheme"),
        "description": payload.get("description"),
        "tags": list(payload.get("tags") or []),
        "confidence": payload.get("confidence"),
        "source_dataset": payload.get("source_dataset"),
        "source_extractor": payload.get("source_extractor"),
        "is_canonical": bool(payload.get("is_canonical", True)),
        "instrument_id": payload.get("instrument_id"),
        "issuer_id": payload.get("issuer_id"),
        "parent_id": payload.get("parent_id"),
        "attributes": dict(payload.get("attributes") or {}),
    }
    _ENTITIES[entity_id] = row
    return row


def get_entity(entity_id: str) -> dict[str, Any] | None:
    row = _ENTITIES.get(entity_id)
    if row is None:
        return None
    return {
        **row,
        "identifiers": list(_IDENTIFIERS.get(entity_id, [])),
        "annotations": list(_ANNOTATIONS.get(entity_id, [])),
    }


def neighbors(entity_id: str, *, depth: int = 1, limit: int = 64) -> dict[str, Any]:
    rels = [rel for rel in _RELATIONS if rel["subject_id"] == entity_id or rel["object_id"] == entity_id][:limit]
    ids = {entity_id}
    for rel in rels:
        ids.add(rel["subject_id"])
        ids.add(rel["object_id"])
    return {"entity_id": entity_id, "depth": depth, "nodes": [get_entity(i) for i in ids if get_entity(i)], "edges": rels}


def link_entity_identifier(entity_id: str, **payload: Any) -> dict[str, Any] | None:
    if entity_id not in _ENTITIES:
        return None
    row = {"id": str(uuid.uuid4()), "entity_id": entity_id, **payload}
    _IDENTIFIERS.setdefault(entity_id, []).append(row)
    return row


def add_entity_relation(entity_id: str, **payload: Any) -> dict[str, Any] | None:
    if entity_id not in _ENTITIES:
        return None
    row = {"id": str(uuid.uuid4()), "subject_id": entity_id, **payload}
    _RELATIONS.append(row)
    return row


def add_entity_annotation(entity_id: str, **payload: Any) -> dict[str, Any] | None:
    if entity_id not in _ENTITIES:
        return None
    row = {"id": str(uuid.uuid4()), "entity_id": entity_id, **payload}
    _ANNOTATIONS.setdefault(entity_id, []).append(row)
    return row


def extract_entities(**payload: Any) -> dict[str, Any]:
    return {"status": "dry_run", "created": 0, "payload": payload}


def enrich_entities(**payload: Any) -> dict[str, Any]:
    return {"status": "dry_run", "updated": 0, "payload": payload}
