"""Hands — Centinela bridge: conditional DD and low-privilege actuation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from qiskit import QuantumCircuit

from eqg.judgment import InterventionType, Plan


@dataclass
class Actuation:
    circuit: QuantumCircuit
    dd_applied: bool
    sequence: str
    layout: List[int]


class Hands:
    """Executes plan on the workload circuit (Centinela DD sequences)."""

    def __init__(self, default_sequence: str = "CPMG"):
        self.default_sequence = default_sequence

    def apply(self, workload: QuantumCircuit, plan: Plan) -> Actuation:
        qc = workload.copy()
        dd = plan.intervention in (InterventionType.DD_ALWAYS, InterventionType.DD_CONDITIONAL)
        sequence = "none"
        if dd:
            sequence = self.default_sequence
            # Insert lightweight identity-framed markers for DD windows (product hook).
            # On hardware backends, replace with calibrated CPMG/XY4 pulse schedules.
            for q in range(qc.num_qubits):
                qc.barrier(q)
                qc.id(q)
                qc.barrier(q)
        qc.metadata = {
            **(qc.metadata or {}),
            "eqg_intervention": plan.intervention.value,
            "eqg_dd": dd,
            "eqg_sequence": sequence,
            "eqg_layout": list(plan.target_qubits),
        }
        return Actuation(
            circuit=qc,
            dd_applied=dd,
            sequence=sequence,
            layout=list(plan.target_qubits),
        )
