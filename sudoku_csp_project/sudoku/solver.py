from __future__ import annotations
from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Set
from .board import Cell, SudokuBoard
from .csp import ac3, clone_domains, initial_domains
from .metrics import Event, SolverMetrics


@dataclass(frozen=True)
class SolverConfig:
    use_forward_checking: bool = False
    use_ac3: bool = False
    use_mrv: bool = False

    @property
    def label(self) -> str:
        enabled = []
        if self.use_forward_checking:
            enabled.append("FC")
        if self.use_ac3:
            enabled.append("AC-3")
        if self.use_mrv:
            enabled.append("MRV")
        return "Backtracking" if not enabled else "Backtracking + " + " + ".join(enabled)

@dataclass
class SolveResult:
    solved: bool
    board: SudokuBoard
    metrics: SolverMetrics
    events: List[Event] = field(default_factory=list)
    config: Optional[SolverConfig] = None
    message: str = ""

class SudokuSolver:
    def __init__(self, config: SolverConfig):
        self.config = config
        self.metrics = SolverMetrics()
        self.events: List[Event] = []

    def solve(self, board: SudokuBoard) -> SolveResult:
        if not board.is_valid():
            return SolveResult(False, board, self.metrics, [], self.config, "Puzzle is invalid.")
        working_board = board.copy()
        try:
            domains = initial_domains(working_board)
        except ValueError as exc:
            return SolveResult(False, board, self.metrics, [], self.config, str(exc))

        start = time.perf_counter()

        if self.config.use_ac3:
            consistent, revisions = ac3(domains)
            self.metrics.ac3_revisions += revisions
            self.events.append({
                "type": "ac3_preprocess",
                "revisions": revisions,
                "snapshot": self._snapshot(working_board, domains),
            })
            if not consistent:
                self.metrics.elapsed_ms = (time.perf_counter() - start) * 1000
                return SolveResult(False, board, self.metrics, self.events, self.config, "AC-3 found inconsistency.")

        solved = self._backtrack(working_board, domains, depth=0)
        self.metrics.elapsed_ms = (time.perf_counter() - start) * 1000

        return SolveResult(
            solved=solved,
            board=working_board,
            metrics=self.metrics,
            events=self.events,
            config=self.config,
            message="Solved successfully." if solved else "No solution found.",
        )

    def _select_unassigned(self, board: SudokuBoard, domains: Dict[Cell, Set[int]]) -> Optional[Cell]:
        unassigned = [(r, c) for r in range(9) for c in range(9) if board.get(r, c) == 0]
        if not unassigned:
            return None
        if self.config.use_mrv:
            return min(unassigned, key=lambda cell: (len(domains[cell]), cell[0], cell[1]))
        return unassigned[0]

    def _ordered_domain(self, cell: Cell, domains: Dict[Cell, Set[int]]) -> List[int]:
        return sorted(domains[cell])

    def _snapshot(self, board: SudokuBoard, domains: Dict[Cell, Set[int]]) -> Dict[str, object]:
        flat_domains = {
            f"{r},{c}": sorted(list(values))
            for (r, c), values in domains.items()
            if board.get(r, c) == 0
        }
        return {
            "board": [row[:] for row in board.grid],
            "domains": flat_domains,
        }

    def _backtrack(self, board: SudokuBoard, domains: Dict[Cell, Set[int]], depth: int) -> bool:
        cell = self._select_unassigned(board, domains)
        if cell is None:
            return True

        self.metrics.nodes_explored += 1
        r, c = cell
        candidate_values = self._ordered_domain(cell, domains)
        self.events.append({
            "type": "select_cell",
            "cell": cell,
            "domain": candidate_values[:],
            "depth": depth,
            "snapshot": self._snapshot(board, domains),
        })

        for value in candidate_values:
            if not board.is_valid_assignment(r, c, value):
                continue

            self.metrics.assignments += 1
            next_board = board.copy()
            next_domains = clone_domains(domains)

            next_board.set(r, c, value)
            next_domains[cell] = {value}

            self.events.append({
                "type": "assign",
                "cell": cell,
                "value": value,
                "depth": depth,
                "snapshot": self._snapshot(next_board, next_domains),
            })

            consistent = True

            if self.config.use_forward_checking:
                pruned = 0
                for neighbor in SudokuBoard.neighbors(r, c):
                    if next_board.get(*neighbor) == 0 and value in next_domains[neighbor]:
                        next_domains[neighbor].discard(value)
                        pruned += 1
                        if not next_domains[neighbor]:
                            consistent = False
                            break
                self.metrics.domain_prunes += pruned
                self.events.append({
                    "type": "forward_check",
                    "cell": cell,
                    "value": value,
                    "consistent": consistent,
                    "depth": depth,
                    "snapshot": self._snapshot(next_board, next_domains),
                })

            if consistent and self.config.use_ac3:
                queue = [((nr, nc), cell) for (nr, nc) in SudokuBoard.neighbors(r, c)]
                consistent, revisions = ac3(next_domains, queue=queue)
                self.metrics.ac3_revisions += revisions
                self.events.append({
                    "type": "ac3_propagate",
                    "cell": cell,
                    "value": value,
                    "consistent": consistent,
                    "revisions": revisions,
                    "depth": depth,
                    "snapshot": self._snapshot(next_board, next_domains),
                })

            if consistent:
                if self._backtrack(next_board, next_domains, depth + 1):
                    board.grid = [row[:] for row in next_board.grid]
                    return True

            self.metrics.backtracks += 1
            self.events.append({
                "type": "backtrack",
                "cell": cell,
                "value": value,
                "depth": depth,
                "snapshot": self._snapshot(board, domains),
            })

        return False
