"""Compute backend selection helpers."""
from __future__ import annotations

from dataclasses import dataclass

from aqp.config import settings
from aqp.data.engine.manifest import ComputeBackendKind, ComputeSpec


@dataclass(frozen=True)
class SizeHint:
    rows: int = 0
    bytes: int = 0


def pick_backend(
    hint: SizeHint,
    *,
    requested: ComputeBackendKind = ComputeBackendKind.AUTO,
    spec: ComputeSpec | None = None,
) -> ComputeSpec:
    """Pick Local/Dask/Ray using the documented size thresholds."""
    current = spec or ComputeSpec()
    if requested != ComputeBackendKind.AUTO:
        current.backend = requested
        return current
    if hint.rows >= settings.compute_local_to_ray_rows or hint.bytes >= settings.compute_local_to_ray_bytes:
        current.backend = ComputeBackendKind.RAY
    elif hint.rows >= settings.compute_local_to_dask_rows or hint.bytes >= settings.compute_local_to_dask_bytes:
        current.backend = ComputeBackendKind.DASK
    else:
        current.backend = ComputeBackendKind.LOCAL
    return current
