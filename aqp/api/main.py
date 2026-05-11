"""FastAPI gateway — the synchronous entry point for the UI and external clients.

This module also mounts the Dash visualization engine at ``/dash`` so the
whole platform is reachable from a single port.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aqp.config import settings
from aqp.observability import (
    configure_tracing,
    instrument_fastapi,
    shutdown_tracing,
)
from aqp.observability.tracing import instrument_httpx, instrument_redis

logger = logging.getLogger(__name__)


def _load_route(name: str):
    try:
        return import_module(f"aqp.api.routes.{name}")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Route module %s disabled: %s", name, exc)
        return None


def _include_route(name: str, *, alias: str | None = None) -> None:
    module = _load_route(alias or name)
    router = getattr(module, "router", None) if module is not None else None
    if router is not None:
        app.include_router(router)


configure_tracing(service_name=f"{settings.otel_service_name}-api")
instrument_httpx()
instrument_redis()


def _maybe_run_iceberg_bootstrap() -> None:
    """Run the Polaris/Iceberg bootstrap manager when ``AQP_ICEBERG_AUTO_BOOTSTRAP`` is enabled.

    Failures are logged but never block startup so the API can still
    expose the manual ``/service-manager/iceberg/bootstrap`` endpoint.
    """
    if not settings.iceberg_auto_bootstrap:
        return
    try:
        from aqp.services.iceberg_bootstrap import IcebergBootstrapManager

        with IcebergBootstrapManager() as manager:
            report = manager.bootstrap()
        logger.info(
            "Iceberg auto-bootstrap finished: success=%s steps=%d duration=%.2fs",
            report.success,
            len(report.steps),
            report.duration_seconds,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Iceberg auto-bootstrap failed; manual /service-manager/iceberg/bootstrap available")


def _maybe_install_m2m_store() -> None:
    """Plug the :class:`M2MStore` into the credential resolver when enabled.

    Activates when ``AQP_AUTH_M2M_ENABLED=true`` and the configured
    :class:`IdentityProvider` supports ``client_credentials``. Failure
    is logged but never blocks startup; with M2M off the resolver still
    reads bootstrap-minted file payloads + env defaults.
    """
    if not getattr(settings, "auth_m2m_enabled", False):
        return
    try:
        from aqp.auth.m2m import install_m2m_store

        install_m2m_store()
    except Exception:  # noqa: BLE001
        logger.exception("M2M store install failed; resolver will fall back to file/env stores")


def _maybe_prefetch_metadata_cache() -> None:
    """Warm the metadata cache so EntityPicker dropdowns are instant."""
    if not getattr(settings, "cache_enabled", True):
        return
    try:
        from aqp.cache.lifespan import prefetch_at_startup

        prefetch_at_startup()
    except Exception:  # noqa: BLE001
        logger.exception(
            "metadata cache prefetch failed; UI dropdowns may be empty until a write-through fires",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AQP API starting | env=%s", settings.env)
    _maybe_run_iceberg_bootstrap()
    _maybe_install_m2m_store()
    _maybe_prefetch_metadata_cache()
    try:
        yield
    finally:
        logger.info("AQP API shutting down")
        shutdown_tracing()


app = FastAPI(
    title="Agentic Quant Platform API",
    version="0.3.0",
    description=(
        "Local-first quantitative research + trading API. Drives the agent crew, "
        "backtests, paper / live trading, RL training, and data ingestion. "
        "The Dash monitor is mounted at /dash."
    ),
    lifespan=lifespan,
)

instrument_fastapi(app)

_cors_origins = settings.webui_cors_origin_list or ["*"]
_cors_credentials = _cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core platform routers -----------------------------------------------
for _route_name in (
    "health",
    "auth",
    "chat",
    "agents",
    "agentic",
    "backtest",
    "rl",
    "data",
    "alpha_vantage",
    "portfolio",
    "paper",
    "brokers",
    "strategies",
    "registry",
    "feature_sets",
    "feature_catalog",
    "data_pipelines",
    "data_control",
    "data_entities",
    "datasets",
    "dbt",
    "entities",
    "market_data_live",
    "factors",
    "ml",
    "metadata_catalog",
    "cache",
    "discovery",
    "dagster_sandbox",
    "monitoring",
    "security",
    "visualizations",
):
    _include_route(_route_name)

# --- Data-plane expansion (Phase 5 of the original plan) -----------------
for _route_name in ("sources", "identifiers", "datalinks", "fred", "sec", "gdelt"):
    _include_route(_route_name)

# --- Phase 2 of the agentic-RAG expansion: regulatory data adapters ------
for _route_name in ("cfpb", "fda", "uspto"):
    _include_route(_route_name)

# --- Phase 6 of the agentic-RAG expansion: spec/team/RAG/memory ---------
for _route_name in (
    "agent_specs",
    "research_agents",
    "selection_agents",
    "trader_agents",
    "analysis_agents",
    "rag",
    "memory",
):
    _include_route(_route_name)

# --- Analysis umbrella (hash-locked AnalysisSpec + flow catalog) -------
_include_route("analysis")

# --- Data fabric expansion (Phase 5/6/7 of data-fabric expansion) -------
for _route_name in (
    "engine",
    "fetchers",
    "entity_registry",
    "dagster",
    "datahub",
    "compute",
    "airbyte",
    "airbyte_builder",
    "service_manager",
):
    _include_route(_route_name)

# --- Inspiration rehydration: dataset presets library ------------------
_include_route("dataset_presets")

# --- Bot Entity Refactor — first-class bot CRUD + lifecycle -----------
_include_route("bots")

# --- Tenancy / multi-tenant resource ownership -------------------------
for _route_name in ("orgs", "teams", "users", "workspaces", "projects", "labs", "configs"):
    _include_route(_route_name)

# --- Data layer expansion (sinks / kafka / flink / producers / proxy) --
for _route_name in ("sinks", "kafka", "flink", "producers", "streaming_links", "dataset_loading_agent"):
    _include_route(_route_name)

_cluster_mgmt = _load_route("cluster_mgmt")
if _cluster_mgmt is not None:
    for _router_name in ("router", "legacy_router"):
        _router = getattr(_cluster_mgmt, _router_name, None)
        if _router is not None:
            app.include_router(_router)


# --- Data layer unification: external MCP server router ----------------
# Exposes DATA_MCP_TOOLS via streamable HTTP so external clients
# (Cursor, Claude Desktop, etc.) can call them through the same
# tool catalog the in-process AgentRuntime uses via the bridge.
try:
    from aqp.data.mcp.server import build_mcp_router as _build_data_mcp_router

    app.include_router(_build_data_mcp_router())
except Exception:  # noqa: BLE001 - MCP server is optional at boot
    logger.warning("DataMCP HTTP router not mounted", exc_info=True)


# ---------------------------------------------------------------------------
# Dash sub-app mount.
#
# Dash runs on Flask, which speaks WSGI; Starlette ships a WSGIMiddleware that
# adapts it to ASGI so the whole platform lives behind a single Uvicorn worker.
# The mount is best-effort: if Dash isn't installed (e.g. the paper-only
# container), we skip it without breaking the API.
# ---------------------------------------------------------------------------
def _mount_dash() -> None:
    """Try the modern ``a2wsgi`` adapter first, fall back to ``starlette``."""
    try:
        from aqp.ui.dash_app import create_dash_app
    except Exception:  # pragma: no cover — dash not installed
        logger.warning("Dash not installed; /dash mount skipped", exc_info=True)
        return

    try:
        _dash_app = create_dash_app(requests_pathname_prefix="/dash/")
    except Exception:  # pragma: no cover
        logger.warning("Dash factory failed; /dash mount skipped", exc_info=True)
        return

    try:
        from a2wsgi import WSGIMiddleware  # type: ignore[import-not-found]
    except ImportError:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from starlette.middleware.wsgi import WSGIMiddleware  # type: ignore[assignment]

    app.mount("/dash", WSGIMiddleware(_dash_app.server))
    logger.info("Dash monitor mounted at /dash")


_mount_dash()


@app.get("/")
def root() -> dict:
    return {
        "app": "agentic-quant-platform",
        "version": "0.3.0",
        "docs": "/docs",
        "dash": "/dash/",
        "routes": [r.path for r in app.routes if hasattr(r, "path")],
    }
