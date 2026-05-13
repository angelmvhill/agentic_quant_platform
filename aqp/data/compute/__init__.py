"""Compute backend abstractions."""
from __future__ import annotations


class LocalBackend:
    """Local in-process backend used for laptop development."""

    def describe(self) -> dict:
        return {"backend": "local", "available": True}


__all__ = ["LocalBackend"]
