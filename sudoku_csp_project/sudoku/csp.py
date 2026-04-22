from __future__ import annotations
from collections import deque
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple
from .board import Cell, SudokuBoard

DomainMap = Dict[Cell, Set[int]]
Arc = Tuple[Cell, Cell]

def initial_domains(board: SudokuBoard) -> DomainMap:
    domains: DomainMap = {}
    for cell in SudokuBoard.all_cells():
        r, c = cell
        value = board.get(r, c)
        if value == 0:
            values = board.legal_values(r, c)
            if not values:
                raise ValueError(f"Initial puzzle is inconsistent at {cell}.")
            domains[cell] = set(values)
        else:
            domains[cell] = {value}
    return domains

def clone_domains(domains: DomainMap) -> DomainMap:
    return {cell: set(values) for cell, values in domains.items()}

def all_arcs() -> List[Arc]:
    arcs: List[Arc] = []
    for xi in SudokuBoard.all_cells():
        r, c = xi
        for xj in SudokuBoard.neighbors(r, c):
            arcs.append((xi, xj))
    return arcs

def revise(domains: DomainMap, xi: Cell, xj: Cell) -> bool:
    revised = False
    to_remove = set()
    for x in domains[xi]:
        if not any(x != y for y in domains[xj]):
            to_remove.add(x)
    if to_remove:
        domains[xi] -= to_remove
        revised = True
    return revised

def ac3(domains: DomainMap, queue: Optional[Iterable[Arc]] = None) -> Tuple[bool, int]:
    q: Deque[Arc] = deque(queue if queue is not None else all_arcs())
    revisions = 0
    while q:
        xi, xj = q.popleft()
        if revise(domains, xi, xj):
            revisions += 1
            if len(domains[xi]) == 0:
                return False, revisions
            rir, cic = xi
            for xk in SudokuBoard.neighbors(rir, cic):
                if xk != xj:
                    q.append((xk, xi))
    return True, revisions
