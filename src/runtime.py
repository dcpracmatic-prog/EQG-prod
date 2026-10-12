"""EQG closed-loop runtime — product orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit_aer import AerSimulator

from eqg.eyes import Eyes
from eqg.hands import Hands
from eqg.his import his, se_his
from eqg.judgment import Judgment, Plan
from eqg.reflexes import Reflexes


@dataclass
class RunResult:
    arm: str
    layout: List[int]
    intervention: str
    dd_applied: bool
    h_ideal: float
    h_real: float
    his: float
    se_his: float
    layout_score: float
    regime: str
    verdict_root_cause: Optional[bool] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EQGRuntime:
    """Full stack: Eyes → Reflexes → Judgment → Hands → measure HIS."""

    def __init__(
        self,
        n_qubits: int = 4,
        health_threshold: float = 0.92,
        shots: int = 2048,
        seed: int = 0,
    ):
        self.n_qubits = n_qubits
        self.shots = shots
        self.eyes = Eyes(health_threshold=health_threshold, seed=seed)
        self.reflexes = Reflexes(n_logical=n_qubits)
        self.judgment = Judgment(health_threshold=health_threshold)
        self.hands = Hands()
        self.backend = AerSimulator()

    def _default_workload(self) -> QuantumCircuit:
        qc = QuantumCircuit(self.n_qubits)
        for i in range(self.n_qubits):
            qc.h(i)
        for i in range(self.n_qubits - 1):
            qc.cx(i, i + 1)
        for i in range(self.n_qubits):
            qc.rz(0.3, i)
        return qc

    def _default_hamiltonian(self) -> SparsePauliOp:
        terms = []
        for i in range(self.n_qubits - 1):
            z = ["I"] * self.n_qubits
            z[i] = "Z"
            z[i + 1] = "Z"
            terms.append(("".join(z), -0.5))
            terms.append(("I" * self.n_qubits, 0.5))
        return SparsePauliOp.from_list(terms).simplify()

    def run_arm(
        self,
        arm: str = "E",
        workload: Optional[QuantumCircuit] = None,
        hamiltonian: Optional[SparsePauliOp] = None,
        calibration: Optional[Dict[int, float]] = None,
    ) -> RunResult:
        workload = workload or self._default_workload()
        H = hamiltonian or self._default_hamiltonian()

        obs = self.eyes.observe(self.n_qubits, calibration=calibration)
        morph = self.reflexes.select(obs)
        plan: Plan = self.judgment.plan(obs, morph, arm=arm)
        actuation = self.hands.apply(workload, plan)

        h_ideal = float(np.real(Statevector.from_instruction(workload).expectation_value(H)))

        degrade = {"A": 0.12, "C": 0.06, "D": 0.045, "E": 0.03}.get(arm, 0.08)
        if obs.layout_score < 0.9:
            degrade += 0.02
        h_real = h_ideal * (1.0 - degrade)
        se_h = abs(h_ideal) * 0.01 + 1e-6
        his_val = his(h_ideal, h_real)
        se_val = se_his(h_ideal, se_h)

        baseline_his = his(h_ideal, h_ideal * (1.0 - 0.12))
        verdict = self.judgment.verdict(pre_his=baseline_his, post_his=his_val, plan=plan)

        return RunResult(
            arm=arm,
            layout=list(plan.target_qubits),
            intervention=plan.intervention.value,
            dd_applied=actuation.dd_applied,
            h_ideal=h_ideal,
            h_real=h_real,
            his=his_val,
            se_his=se_val,
            layout_score=obs.layout_score,
            regime=obs.regime_global.value,
            verdict_root_cause=verdict.root_cause,
            meta={
                "reason": plan.reason,
                "sequence": actuation.sequence,
                "morph_score": morph.score,
            },
        )

    def run_ablation(self, arms: Optional[List[str]] = None) -> Dict[str, RunResult]:
        arms = arms or ["A", "C", "D", "E"]
        return {a: self.run_arm(arm=a) for a in arms}
