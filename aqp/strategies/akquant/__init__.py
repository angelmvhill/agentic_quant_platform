"""akquant-main/examples strategy ports."""
from __future__ import annotations

from aqp.strategies.akquant.alphas import (
    AtrBreakoutAlpha,
    BucketMomentumRotationAlpha,
    CoveredCallStrategy,
    DualMovingAverageAlpha,
    ETFGridStrategy,
    FuturesTrendAlpha,
    GridTradingStrategy,
    MomentumRotationAlpha,
    SixtyFortyRebalanceStrategy,
    TargetWeightsRebalanceStrategy,
    TimerMomentumRotationAlpha,
    TPlusOneStrategy,
)

__all__ = [
    "AtrBreakoutAlpha",
    "BucketMomentumRotationAlpha",
    "CoveredCallStrategy",
    "DualMovingAverageAlpha",
    "ETFGridStrategy",
    "FuturesTrendAlpha",
    "GridTradingStrategy",
    "MomentumRotationAlpha",
    "SixtyFortyRebalanceStrategy",
    "TPlusOneStrategy",
    "TargetWeightsRebalanceStrategy",
    "TimerMomentumRotationAlpha",
]
