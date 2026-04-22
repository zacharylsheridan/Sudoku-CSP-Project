from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class SolverMetrics:
    nodes_explored: int = 0
    backtracks: int = 0
    assignments: int = 0
    domain_prunes: int = 0
    ac3_revisions: int = 0
    elapsed_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes_explored": self.nodes_explored,
            "backtracks": self.backtracks,
            "assignments": self.assignments,
            "domain_prunes": self.domain_prunes,
            "ac3_revisions": self.ac3_revisions,
            "elapsed_ms": round(self.elapsed_ms, 3),
        }


Event = Dict[str, Any]
