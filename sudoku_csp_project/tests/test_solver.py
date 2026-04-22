from sudoku.board import SudokuBoard
from sudoku.solver import SolverConfig, SudokuSolver

EASY = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

def test_solver_solves_easy_with_all_heuristics():
    board = SudokuBoard.from_string(EASY)
    solver = SudokuSolver(SolverConfig(use_forward_checking=True, use_ac3=True, use_mrv=True))
    result = solver.solve(board)
    assert result.solved
    assert result.board.is_complete()
    assert result.board.is_valid()

def test_solver_solves_easy_plain_backtracking():
    board = SudokuBoard.from_string(EASY)
    solver = SudokuSolver(SolverConfig(use_forward_checking=False, use_ac3=False, use_mrv=False))
    result = solver.solve(board)
    assert result.solved
    assert result.board.is_complete()
    assert result.board.is_valid()
