"""Synchronize dataset coverage into the unified entity registry."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select

from aqp.core.types import Symbol
from aqp.persistence.models import Instrument
from aqp.persistence.models_entity_registry import EntityDatasetLink, EntityRow

logger = logging.getLogger(__name__)


def active_instruments(*, session: Any, refresh: bool = False, limit: int = 5000) -> list[dict[str, Any]]:
    """Return active instruments in a JSON-friendly shape.

    ``refresh`` is accepted for API compatibility with graph-backed
    deployments; the SQL-backed local registry reads the current instrument
    table directly.
    """
    del refresh
    rows = (
        session.execute(select(Instrument).order_by(Instrument.vt_symbol).limit(int(limit)))
        .scalars()
        .all()
    )
    return [
        {
            "id": row.id,
            "vt_symbol": row.vt_symbol,
            "ticker": row.ticker,
            "exchange": row.exchange,
            "asset_class": row.asset_class,
            "security_type": row.security_type,
            "instrument_class": row.instrument_class,
        }
        for row in rows
    ]


def sync_active_instruments_to_graph(*, session: Any, limit: int = 5000) -> dict[str, int]:
    """Seed active instruments into the generic entity registry."""
    rows = active_instruments(session=session, limit=limit)
    result = sync_dataset_version_entities(
        session=session,
        catalog=None,
        version=None,
        vt_symbols=[row["vt_symbol"] for row in rows],
    )
    return {"instruments_seen": len(rows), **result}


def sync_dataset_version_entities(
    *,
    session: Any,
    catalog: Any,
    version: Any,
    vt_symbols: list[str],
    coverage_start: datetime | None = None,
    coverage_end: datetime | None = None,
) -> dict[str, int]:
    """Link a market dataset version to canonical security entities.

    The catalog writer already upserts :class:`Instrument` rows before
    calling this helper. This function mirrors those instruments into the
    generic entity registry so data-discovery and graph surfaces can answer
    "which datasets cover this entity?" without reading market tables.
    """
    created_entities = 0
    created_links = 0
    skipped = 0
    normalized = sorted({str(symbol).strip().upper() for symbol in vt_symbols if str(symbol).strip()})

    for vt_symbol in normalized:
        try:
            symbol = Symbol.parse(vt_symbol)
        except Exception:  # noqa: BLE001
            logger.debug("Skipping invalid vt_symbol during entity sync: %s", vt_symbol, exc_info=True)
            skipped += 1
            continue

        instrument = session.execute(
            select(Instrument).where(Instrument.vt_symbol == vt_symbol).limit(1)
        ).scalar_one_or_none()
        entity = session.execute(
            select(EntityRow)
            .where(EntityRow.kind == "security")
            .where(EntityRow.primary_identifier_scheme == "vt_symbol")
            .where(EntityRow.primary_identifier == vt_symbol)
            .limit(1)
        ).scalar_one_or_none()

        if entity is None:
            entity = EntityRow(
                kind="security",
                canonical_name=vt_symbol,
                short_name=symbol.ticker,
                primary_identifier=vt_symbol,
                primary_identifier_scheme="vt_symbol",
                instrument_id=getattr(instrument, "id", None),
                source_dataset=getattr(catalog, "name", None),
                source_extractor="dataset_catalog",
                attributes={
                    "ticker": symbol.ticker,
                    "exchange": symbol.exchange.value,
                    "asset_class": symbol.asset_class.value,
                    "security_type": symbol.security_type.value,
                },
                tags=["market_bars"],
                confidence=1.0,
            )
            session.add(entity)
            session.flush()
            created_entities += 1
        else:
            if instrument is not None and not entity.instrument_id:
                entity.instrument_id = instrument.id
            entity.short_name = entity.short_name or symbol.ticker
            entity.updated_at = datetime.utcnow()
            session.add(entity)

        existing_link = session.execute(
            select(EntityDatasetLink)
            .where(EntityDatasetLink.entity_id == entity.id)
            .where(EntityDatasetLink.dataset_catalog_id == getattr(catalog, "id", None))
            .where(EntityDatasetLink.dataset_version_id == getattr(version, "id", None))
            .limit(1)
        ).scalar_one_or_none()
        if existing_link is not None:
            continue

        link = EntityDatasetLink(
            entity_id=entity.id,
            dataset_catalog_id=getattr(catalog, "id", None),
            dataset_version_id=getattr(version, "id", None),
            iceberg_identifier=getattr(catalog, "iceberg_identifier", None),
            row_count=getattr(version, "row_count", None),
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            role="coverage",
            meta={"vt_symbol": vt_symbol},
        )
        session.add(link)
        created_links += 1

    return {
        "symbols_seen": len(normalized),
        "entities_created": created_entities,
        "links_created": created_links,
        "symbols_skipped": skipped,
    }


__all__ = [
    "active_instruments",
    "sync_active_instruments_to_graph",
    "sync_dataset_version_entities",
]
