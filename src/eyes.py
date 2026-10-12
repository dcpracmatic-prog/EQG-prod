"""Eyes — observation layer (health, friction, regime)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


class Regime(str, Enum):
    ESTABLE = "ESTABLE"
    INESTABLE = "INESTABLE"
    CONFLICTO = "CONFLICTO"


@dataclass
class QubitHealth:
    qubit: int
    score: float
    friction: float
    regime: Regime


@dataclass
class Observation:
    health: Dict[int, QubitHealth]
    layout_score: float
    regime_global: Regime
    candidates: List[int]


class Eyes:
    """Privilege-free observer over probe / calibration signals."""

    def __init__(self, health_threshold: float = 0.92, seed: int = 0):
        self.health_threshold = health_threshold
        self.rng = np.random.default_rng(seed)

    def observe(
        self,
        n_qubits: int,
        calibration: Optional[Dict[int, float]] = None,
        live_friction: Optional[Dict[int, float]] = None,
    ) -> Observation:
        health: Dict[int, QubitHealth] = {}
        scores = []
        for q in range(n_qubits):
            base = 1.0
            if calibration and q in calibration:
                base = float(calibration[q])
            friction = 0.0
            if live_friction and q in live_friction:
                friction = float(live_friction[q])
            else:
                friction = float(self.rng.uniform(0.0, 0.08))
            score = max(0.0, min(1.0, base - 0.5 * friction))
            if score >= self.health_threshold:
                regime = Regime.ESTABLE
            elif score >= 0.75:
                regime = Regime.INESTABLE
            else:
                regime = Regime.CONFLICTO
            health[q] = QubitHealth(qubit=q, score=score, friction=friction, regime=regime)
            scores.append(score)

        layout_score = float(np.mean(scores)) if scores else 0.0
        if layout_score >= self.health_threshold:
            global_regime = Regime.ESTABLE
        elif layout_score >= 0.75:
            global_regime = Regime.INESTABLE
        else:
            global_regime = Regime.CONFLICTO

        candidates = sorted(health.keys(), key=lambda q: health[q].score, reverse=True)
        return Observation(
            health=health,
            layout_score=layout_score,
            regime_global=global_regime,
            candidates=candidates,
        )
