"""Alpha Vantage endpoint catalog used by the API and bulk loaders."""
from __future__ import annotations

from typing import Any


class AlphaVantageFunction:
    """Small value wrapper matching the documented endpoint catalog API."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = dict(payload)
        self.id = str(payload["id"])

    @property
    def iceberg_identifier(self) -> str:
        return f"aqp_alpha_vantage.{self._payload.get('iceberg_table', self.id.replace('.', '_'))}"

    def to_dict(self) -> dict[str, Any]:
        return {**self._payload, "iceberg_identifier": self.iceberg_identifier}

_FUNCTIONS: list[dict[str, Any]] = [
    {
        "id": "timeseries.daily_adjusted",
        "category": "timeseries",
        "function": "daily_adjusted",
        "label": "Daily adjusted OHLCV",
        "required_params": ["symbol"],
        "optional_params": ["outputsize"],
        "lake_supported": True,
        "iceberg_table": "time_series_daily_adjusted",
        "partition_spec": "bucket(vt_symbol, 16) + month(timestamp)",
    },
    {
        "id": "timeseries.intraday",
        "category": "timeseries",
        "function": "intraday",
        "label": "Intraday OHLCV",
        "required_params": ["symbol", "interval"],
        "optional_params": ["month", "outputsize"],
        "lake_supported": True,
        "iceberg_table": "time_series_intraday",
        "partition_spec": "bucket(vt_symbol, 16) + month(timestamp)",
    },
    {
        "id": "fundamentals.overview",
        "category": "fundamentals",
        "function": "overview",
        "label": "Company overview",
        "required_params": ["symbol"],
        "optional_params": [],
        "lake_supported": True,
        "iceberg_table": "fundamentals_overview",
        "partition_spec": "identity(vt_symbol)",
    },
    {
        "id": "fundamentals.income_statement",
        "category": "fundamentals",
        "function": "income_statement",
        "label": "Income statement",
        "required_params": ["symbol"],
        "optional_params": [],
        "lake_supported": True,
        "iceberg_table": "fundamentals_income_statement",
        "partition_spec": "identity(vt_symbol)",
    },
    {
        "id": "intelligence.news",
        "category": "intelligence",
        "function": "news",
        "label": "News sentiment",
        "required_params": [],
        "optional_params": ["tickers", "topics", "time_from", "time_to"],
        "lake_supported": True,
        "iceberg_table": "intelligence_news_sentiment",
        "partition_spec": "bucket(vt_symbol, 16) + month(timestamp)",
    },
    {
        "id": "technicals.sma",
        "category": "technicals",
        "function": "sma",
        "label": "Simple moving average",
        "required_params": ["symbol", "interval", "time_period", "series_type"],
        "optional_params": [],
        "lake_supported": True,
        "iceberg_table": "technicals_sma",
        "partition_spec": "bucket(vt_symbol, 16) + month(timestamp)",
    },
]


def list_functions() -> list[dict[str, Any]]:
    """Return the supported Alpha Vantage lake/catalog functions."""
    return [AlphaVantageFunction(item).to_dict() for item in _FUNCTIONS]


def function_by_id(function_id: str) -> dict[str, Any] | None:
    """Look up a catalog function by stable id."""
    for item in _FUNCTIONS:
        if item["id"] == function_id:
            return AlphaVantageFunction(item).to_dict()
    return None


def lake_supported_functions() -> list[AlphaVantageFunction]:
    """Return functions that can be materialized into the Iceberg lake."""
    return [AlphaVantageFunction(item) for item in _FUNCTIONS if item.get("lake_supported")]
