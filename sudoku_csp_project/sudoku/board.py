from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Set, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]

def _chunked(seq: Sequence[int], size: int) -> List[List[int]]:
    return [list(seq[i:i + size]) for i in range(0, len(seq), size)]

@dataclass
class SudokuBoard:
    grid: Grid
    
    @classmethod
    def from_string(cls, puzzle: str) -> "SudokuBoard":
        cleaned = [c for c in puzzle.strip() if c in "0123456789."]
        if len(cleaned) != 81:
            raise ValueError("Puzzle must contain exactly 81 digits/dots.")
        values = [0 if c in "0." else int(c) for c in cleaned]
        return cls(_chunked(values, 9))

    @classmethod
    def from_rows(cls, rows: Iterable[Iterable[int]]) -> "SudokuBoard":
        grid = [list(row) for row in rows]
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError("Board must be 9x9.")
        return cls(grid)

    def copy(self) -> "SudokuBoard":
        return SudokuBoard([row[:] for row in self.grid])

    def to_string(self) -> str:
        return "".join(str(v) for row in self.grid for v in row)

    def to_pretty_string(self) -> str:
        lines = []
        for r in range(9):
            if r % 3 == 0 and r != 0:
                lines.append("-" * 21)
            row_parts = []
            for c in range(9):
                if c % 3 == 0 and c != 0:
                    row_parts.append("|")
                value = self.grid[r][c]
                row_parts.append(str(value) if value != 0 else ".")
            lines.append(" ".join(row_parts))
        return "\n".join(lines)

    def is_complete(self) -> bool:
        return all(self.grid[r][c] != 0 for r in range(9) for c in range(9))

    def get(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set(self, row: int, col: int, value: int) -> None:
        self.grid[row][col] = value

    @staticmethod
    def all_cells() -> List[Cell]:
        return [(r, c) for r in range(9) for c in range(9)]

    @staticmethod
    def row_cells(row: int) -> List[Cell]:
        return [(row, c) for c in range(9)]

    @staticmethod
    def col_cells(col: int) -> List[Cell]:
        return [(r, col) for r in range(9)]

    @staticmethod
    def box_cells(row: int, col: int) -> List[Cell]:
        br = (row // 3) * 3
        bc = (col // 3) * 3
        return [(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3)]

    @staticmethod
    def neighbors(row: int, col: int) -> Set[Cell]:
        n = set(SudokuBoard.row_cells(row) + SudokuBoard.col_cells(col) + SudokuBoard.box_cells(row, col))
        n.discard((row, col))
        return n

    def legal_values(self, row: int, col: int) -> Set[int]:
        if self.grid[row][col] != 0:
            return {self.grid[row][col]}
        used = set()
        for rr, cc in self.neighbors(row, col):
            val = self.grid[rr][cc]
            if val != 0:
                used.add(val)
        return set(range(1, 10)) - used

    def is_valid_assignment(self, row: int, col: int, value: int) -> bool:
        for rr, cc in self.neighbors(row, col):
            if self.grid[rr][cc] == value:
                return False
        return True

    def is_valid(self) -> bool:
        for r in range(9):
            vals = [self.grid[r][c] for c in range(9) if self.grid[r][c] != 0]
            if len(vals) != len(set(vals)):
                return False
        for c in range(9):
            vals = [self.grid[r][c] for r in range(9) if self.grid[r][c] != 0]
            if len(vals) != len(set(vals)):
                return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                vals = [self.grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3) if self.grid[r][c] != 0]
                if len(vals) != len(set(vals)):
                    return False
        return True
