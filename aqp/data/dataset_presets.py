"""Curated dataset preset catalog."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class DatasetPreset:
    name: str
    description: str
    namespace: str
    table: str
    source_kind: str
    ingestion_task: str
    requires_api_key: bool = False
    api_key_env_var: str | None = None
    default_symbols: list[str] = field(default_factory=list)
    interval: str = "1d"
    schedule_cron: str | None = None
    documentation_url: str | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def iceberg_identifier(self) -> str:
        return f"{self.namespace}.{self.table}"

    def to_dict(self) -> dict:
        return {**asdict(self), "iceberg_identifier": self.iceberg_identifier}


PRESETS = [
    DatasetPreset(
        name="equity_universe_sp500_daily",
        description="Daily OHLCV panel for a representative S&P 500 universe.",
        namespace="market",
        table="sp500_daily",
        source_kind="yfinance",
        ingestion_task="aqp.tasks.dataset_preset_tasks.ingest_sp500_daily",
        default_symbols=["SPY", "AAPL", "MSFT"],
        tags=["equity", "daily"],
    ),
    DatasetPreset(
        name="fred_macro_basket",
        description="Small macro basket from FRED.",
        namespace="macro",
        table="fred_macro_basket",
        source_kind="fred",
        ingestion_task="aqp.tasks.dataset_preset_tasks.ingest_fred_macro_basket",
        requires_api_key=True,
        api_key_env_var="AQP_FRED_API_KEY",
        tags=["macro", "fred"],
    ),
]


def list_presets() -> list[DatasetPreset]:
    return list(PRESETS)


def list_preset_names() -> list[str]:
    return [preset.name for preset in PRESETS]


def get_preset(name: str) -> DatasetPreset:
    for preset in PRESETS:
        if preset.name == name:
            return preset
    raise KeyError(name)


def list_presets_by_tag(tag: str | None) -> list[DatasetPreset]:
    if not tag:
        return list_presets()
    return [preset for preset in PRESETS if tag in preset.tags]
