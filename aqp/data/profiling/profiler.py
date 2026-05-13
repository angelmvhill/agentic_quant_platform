"""Lightweight Arrow/Pandas dataset profiler."""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def compute_profile(table: Any, *, topk: int = 10, sample_rows: int = 200_000) -> dict[str, Any]:
    """Return a JSON-serializable column profile for an Arrow-like table.

    The analysis framework expects a dict with dataset-level metrics and a
    ``columns`` list. This implementation intentionally uses Pandas as the
    common denominator so it works for PyArrow tables, Pandas frames, and
    simple records in local smoke tests.
    """
    frame = _to_frame(table)
    if sample_rows > 0 and len(frame) > sample_rows:
        frame = frame.head(sample_rows)

    columns: list[dict[str, Any]] = []
    for name in frame.columns:
        series = frame[name]
        non_null = series.dropna()
        row: dict[str, Any] = {
            "column": str(name),
            "dtype": str(series.dtype),
            "n": int(len(series)),
            "n_null": int(series.isna().sum()),
            "null_fraction": float(series.isna().mean()) if len(series) else 0.0,
            "n_distinct": int(non_null.nunique(dropna=True)) if len(non_null) else 0,
            "topk": _topk(non_null, topk),
        }
        if len(non_null):
            row["min"] = _json_scalar(non_null.min())
            row["max"] = _json_scalar(non_null.max())
        else:
            row["min"] = None
            row["max"] = None
        columns.append(row)

    return {
        "rows": int(len(frame)),
        "bytes": int(frame.memory_usage(deep=True).sum()) if not frame.empty else 0,
        "engine": "pandas",
        "columns": columns,
    }


def _to_frame(table: Any) -> pd.DataFrame:
    if isinstance(table, pd.DataFrame):
        return table.copy()
    if hasattr(table, "to_pandas"):
        return table.to_pandas()
    return pd.DataFrame(table)


def _topk(series: pd.Series, topk: int) -> list[dict[str, Any]]:
    if topk <= 0 or series.empty:
        return []
    counts = series.value_counts().head(topk)
    total = int(len(series))
    return [
        {
            "value": _json_scalar(value),
            "count": int(count),
            "share": float(count) / total if total else 0.0,
        }
        for value, count in counts.items()
    ]


def _json_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:  # noqa: BLE001
            pass
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:  # noqa: BLE001
            pass
    return value


__all__ = ["compute_profile"]
