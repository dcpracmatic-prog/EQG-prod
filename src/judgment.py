"""Judgment — minimal intervention plan and causal verdict."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from eqg.eyes import Observation, Regime
from eqg.reflexes import MorphLayout


class InterventionType(str, Enum):
    HOLD = "HOLD"
    REMAP_MORPH = "REMAP_MORPH"
    DD_CONDITIONAL = "DD_CONDITIONAL"
    DD_ALWAYS = "DD_ALWAYS"


@dataclass
class Plan:
    intervention: InterventionType
    target_qubits: List[int]
    reason: str
    expected_delta_his: float


@dataclass
class CausalVerdict:
    root_cause: bool
    note: str
    pre_his: Optional[float] = None
    post_his: Optional[float] = None


class Judgment:
    """Evaluates whether to hold, remap, or apply conditional DD."""

    def __init__(self, health_threshold: float = 0.92, his_gain_threshold: float = 0.02):
        self.health_threshold = health_threshold
        self.his_gain_threshold = his_gain_threshold

    def plan(self, observation: Observation, morph: MorphLayout, arm: str = "E") -> Plan:
        if arm == "A":
            return Plan(
                intervention=InterventionType.HOLD,
                target_qubits=list(range(len(morph.selected))),
                reason="baseline_naive",
                expected_delta_his=0.0,
            )
        if arm == "C":
            return Plan(
                intervention=InterventionType.REMAP_MORPH,
                target_qubits=list(morph.selected),
                reason="morph_layout_only",
                expected_delta_his=0.03,
            )
        if arm == "D":
            return Plan(
                intervention=InterventionType.DD_ALWAYS,
                target_qubits=list(morph.selected),
                reason="morph_plus_permanent_dd",
                expected_delta_his=0.04,
            )
        # E — full EQG
        if observation.regime_global == Regime.ESTABLE and observation.layout_score >= self.health_threshold:
            return Plan(
                intervention=InterventionType.REMAP_MORPH,
                target_qubits=list(morph.selected),
                reason="stable_hold_morph",
                expected_delta_his=0.02,
            )
        return Plan(
            intervention=InterventionType.DD_CONDITIONAL,
            target_qubits=list(morph.selected),
            reason="instability_conditional_dd",
            expected_delta_his=0.05,
        )

    def verdict(self, pre_his: float, post_his: float, plan: Plan) -> CausalVerdict:
        delta = post_his - pre_his
        root = delta >= self.his_gain_threshold and plan.intervention != InterventionType.HOLD
        note = "root_cause_gain" if root else "symptom_or_null"
        return CausalVerdict(root_cause=root, note=note, pre_his=pre_his, post_his=post_his)
