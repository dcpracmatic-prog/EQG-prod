"""Hamiltonian Integrity Score (HIS) — product metric API."""

from __future__ import annotations

import math
from typing import Tuple


EPS = 1e-8


def his(h_ideal: float, h_real: float, eps: float = EPS) -> float:
    d = abs(h_ideal)
    if d < eps:
        return float("nan")
    return 1.0 - abs(h_ideal - h_real) / d


def se_his(h_ideal: float, se_h_real: float, eps: float = EPS) -> float:
    d = abs(h_ideal)
    if d < eps:
        return float("nan")
    return se_h_real / d


def z_delta(his_a: float, se_a: float, his_b: float, se_b: float, eps: float = EPS) -> float:
    se = math.sqrt(se_a**2 + se_b**2)
    if se < eps or math.isnan(se):
        return float("nan")
    return (his_a - his_b) / se


def hrf(his_e: float, his_a: float, eps: float = EPS) -> float:
    if abs(his_a) < eps or math.isnan(his_a) or math.isnan(his_e):
        return float("nan")
    return his_e / his_a
