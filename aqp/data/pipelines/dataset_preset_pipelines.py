"""Dataset preset ingestion placeholders with explicit dry-run semantics."""
from __future__ import annotations

from typing import Any


def _result(name: str, **kwargs: Any) -> dict[str, Any]:
    return {"preset": name, "status": "dry_run", "rows_written": 0, "kwargs": kwargs}


def ingest_etf_intraday_panel(**kwargs: Any) -> dict[str, Any]:
    return _result("intraday_momentum_etf", **kwargs)


def ingest_commodity_futures_panel(**kwargs: Any) -> dict[str, Any]:
    return _result("commodity_futures_panel", **kwargs)


def ingest_akshare_china_panel(**kwargs: Any) -> dict[str, Any]:
    return _result("china_a_shares_top200", **kwargs)


def ingest_crypto_kucoin_intraday(**kwargs: Any) -> dict[str, Any]:
    return _result("crypto_majors_intraday", **kwargs)


def ingest_sp500_daily(**kwargs: Any) -> dict[str, Any]:
    return _result("equity_universe_sp500_daily", **kwargs)


def ingest_fred_macro_basket(**kwargs: Any) -> dict[str, Any]:
    return _result("fred_macro_basket", **kwargs)


def ingest_eod_options_sample(**kwargs: Any) -> dict[str, Any]:
    return _result("eod_options_chain_sample", **kwargs)


def ingest_lob_sample(**kwargs: Any) -> dict[str, Any]:
    return _result("lob_btcusdt_sample", **kwargs)


def ingest_finviz_screener(**kwargs: Any) -> dict[str, Any]:
    return _result("finviz_screener", **kwargs)
