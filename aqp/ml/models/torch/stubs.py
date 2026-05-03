"""Tier-B PyTorch model stubs kept for compatibility tests.

Concrete ports live in their per-model modules. This module intentionally
preserves the historical "not implemented" contract for YAMLs/tests that
import from ``aqp.ml.models.torch.stubs``.
"""
from __future__ import annotations


class _TierBStub:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def fit(self, *args, **kwargs):
        raise NotImplementedError("Tier-B model stub; import the concrete per-model module")

    def predict(self, *args, **kwargs):
        raise NotImplementedError("Tier-B model stub; import the concrete per-model module")


class ADARNNModel(_TierBStub):
    pass


class ADDModel(_TierBStub):
    pass


class GATsModel(_TierBStub):
    pass


class HISTModel(_TierBStub):
    pass


class IGMTFModel(_TierBStub):
    pass


class KRNNModel(_TierBStub):
    pass


class SandwichModel(_TierBStub):
    pass


class SFMModel(_TierBStub):
    pass


class TCTSModel(_TierBStub):
    pass


class TRAModel(_TierBStub):
    pass

__all__ = [
    "ADARNNModel",
    "ADDModel",
    "GATsModel",
    "HISTModel",
    "IGMTFModel",
    "KRNNModel",
    "SFMModel",
    "SandwichModel",
    "TCTSModel",
    "TRAModel",
]
