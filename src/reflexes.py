"""Reflexes — MORPH layout selection (fast independent-set style mapping)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from eqg.eyes import Observation


@dataclass
class MorphLayout:
    selected: List[int]
    score: float
    edges_avoided: int


class Reflexes:
    """Deterministic ultra-low-latency layout selection from observation."""

    def __init__(self, n_logical: int = 4):
        self.n_logical = n_logical

    def select(
        self,
        observation: Observation,
        coupling_map: Optional[Sequence[Tuple[int, int]]] = None,
    ) -> MorphLayout:
        ranked = list(observation.candidates)
        if not ranked:
            ranked = list(range(self.n_logical))

        selected: List[int] = []
        forbidden = set()
        edges = set()
        if coupling_map:
            for a, b in coupling_map:
                edges.add((min(a, b), max(a, b)))

        avoided = 0
        for q in ranked:
            if q in forbidden:
                avoided += 1
                continue
            selected.append(q)
            if coupling_map:
                for a, b in edges:
                    if a == q:
                        forbidden.add(b)
                    elif b == q:
                        forbidden.add(a)
            if len(selected) >= self.n_logical:
                break

        while len(selected) < self.n_logical:
            for q in ranked:
                if q not in selected:
                    selected.append(q)
                if len(selected) >= self.n_logical:
                    break
            break

        score = 0.0
        for q in selected:
            if q in observation.health:
                score += observation.health[q].score
        score = score / max(len(selected), 1)

        return MorphLayout(selected=selected[: self.n_logical], score=score, edges_avoided=avoided)
