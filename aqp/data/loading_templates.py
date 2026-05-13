"""Documented loading-template helpers for Data Browser exports."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LoadingTemplate:
    """Reusable data-loading template surfaced in the webui."""

    id: str
    name: str
    description: str
    source_kind: str
    default_kwargs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_TEMPLATES = {
    "local_parquet": LoadingTemplate(
        id="local_parquet",
        name="Local Parquet Root",
        description="Read partitioned parquet from a local filesystem root.",
        source_kind="parquet_root",
        default_kwargs={"hive_partitioning": True, "glob_pattern": "*.parquet"},
    ),
    "local_csv": LoadingTemplate(
        id="local_csv",
        name="Local CSV Folder",
        description="Read CSV files from a local folder and normalize them.",
        source_kind="csv",
        default_kwargs={"glob_pattern": "*.csv"},
    ),
}


def list_loading_templates() -> list[dict[str, Any]]:
    return [template.to_dict() for template in _TEMPLATES.values()]


def get_loading_template(template_id: str) -> LoadingTemplate:
    return _TEMPLATES[template_id]


def build_template_payload(template_id: str, **overrides: Any) -> dict[str, Any]:
    template = get_loading_template(template_id)
    payload = template.to_dict()
    payload["kwargs"] = {**template.default_kwargs, **overrides}
    return payload
