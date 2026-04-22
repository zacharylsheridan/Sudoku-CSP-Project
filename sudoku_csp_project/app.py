from __future__ import annotations
import time
from typing import Dict, List
import pandas as pd
import plotly.express as px
import streamlit as st
from sudoku.board import SudokuBoard
from sudoku.puzzles import PUZZLES
from sudoku.solver import SolveResult, SolverConfig, SudokuSolver

st.set_page_config(page_title="Sudoku CSP Solver", layout="wide")

def render_board_html(grid, active_cell=None, highlight_type="select"):
    active_style = "#fff3cd" if highlight_type == "select" else "#d1e7dd"
    html = """
    <style>
    .sudoku-wrapper { display: inline-block; }
    .sudoku-grid {
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 24px;
        margin: 8px 0;
    }
    .sudoku-grid td {
        width: 42px;
        height: 42px;
        text-align: center;
        vertical-align: middle;
        border: 1px solid #888;
        font-weight: 600;
    }
    .thick-bottom { border-bottom: 3px solid #000 !important; }
    .thick-right  { border-right: 3px solid #000 !important; }
    .thick-top    { border-top: 3px solid #000 !important; }
    .thick-left   { border-left: 3px solid #000 !important; }
    .fixed { color: var(--text-color, #f5f5f5); }
    .empty { color: rgba(255,255,255,0.22); }
    </style>
    <div class="sudoku-wrapper"><table class="sudoku-grid">
    """
    for r in range(9):
        html += "<tr>"
        for c in range(9):
            classes = []
            if r == 0:
                classes.append("thick-top")
            if c == 0:
                classes.append("thick-left")
            if r in (2, 5, 8):
                classes.append("thick-bottom")
            if c in (2, 5, 8):
                classes.append("thick-right")
            value = grid[r][c]
            display = "&nbsp;" if value == 0 else str(value)
            css_class = "empty" if value == 0 else "fixed"
            style = ""
            if active_cell == (r, c):
                style = f' style="background:{active_style};"'
            html += f'<td class="{" ".join(classes)} {css_class}"{style}>{display}</td>'
        html += "</tr>"
    html += "</table></div>"
    return html


def parse_puzzle(text: str) -> SudokuBoard:
    return SudokuBoard.from_string(text)

def solve_once(board: SudokuBoard, config: SolverConfig) -> SolveResult:
    solver = SudokuSolver(config)
    return solver.solve(board)

def replay_events(events: List[dict], speed: float):
    board_placeholder = st.empty()
    caption_placeholder = st.empty()
    domain_placeholder = st.empty()
    for idx, event in enumerate(events, start=1):
        snapshot = event.get("snapshot", {})
        grid = snapshot.get("board")
        if not grid:
            continue
        active_cell = tuple(event.get("cell")) if event.get("cell") is not None else None
        highlight_type = "assign" if event["type"] == "assign" else "select"
        board_placeholder.markdown(render_board_html(grid, active_cell, highlight_type), unsafe_allow_html=True)
        caption_placeholder.markdown(
            f"**Step {idx}:** `{event['type']}`"
            + (f" at cell {active_cell}" if active_cell else "")
            + (f" with value {event.get('value')}" if event.get("value") is not None else "")
        )
        domains = snapshot.get("domains", {})
        if active_cell:
            key = f"{active_cell[0]},{active_cell[1]}"
            domain_placeholder.write({"active_cell_domain": domains.get(key, [])})
        else:
            domain_placeholder.write({})
        time.sleep(speed)

st.title("Sudoku CSP Solver and Visualizer")
st.caption("Constraint-based Sudoku solving with Backtracking, Forward Checking, AC-3, and MRV.")

left, right = st.columns([1.1, 1.4], gap="large")

with left:
    st.subheader("Puzzle input")
    preset = st.selectbox("Choose a preset", ["Custom"] + list(PUZZLES.keys()))
    default_value = PUZZLES.get(preset, "") if preset != "Custom" else PUZZLES["Easy"]
    puzzle_text = st.text_area("Enter 81-character puzzle string", value=default_value, height=110)

    st.markdown("**Solver configuration**")
    use_fc = st.checkbox("Forward Checking (FC)", value=True)
    use_ac3 = st.checkbox("Arc Consistency (AC-3)", value=True)
    use_mrv = st.checkbox("Minimum Remaining Values (MRV)", value=True)

    compare_options = {
        "Backtracking": SolverConfig(False, False, False),
        "Backtracking + FC": SolverConfig(True, False, False),
        "Backtracking + AC-3": SolverConfig(False, True, False),
        "Backtracking + MRV": SolverConfig(False, False, True),
        "Backtracking + FC + MRV": SolverConfig(True, False, True),
        "Backtracking + AC-3 + MRV": SolverConfig(False, True, True),
        "Backtracking + FC + AC-3 + MRV": SolverConfig(True, True, True),
    }
    selected_comparisons = st.multiselect(
        "Comparison configurations",
        options=list(compare_options.keys()),
        default=["Backtracking", "Backtracking + FC + AC-3 + MRV"],
    )

    speed = st.slider("Animation delay (seconds)", min_value=0.0, max_value=0.50, value=0.05, step=0.01)

    solve_clicked = st.button("Solve selected configuration", type="primary")
    compare_clicked = st.button("Run comparison panel")

with right:
    st.subheader("Visualization / results")

    if solve_clicked:
        try:
            board = parse_puzzle(puzzle_text)
            config = SolverConfig(use_fc, use_ac3, use_mrv)
            result = solve_once(board, config)

            c1, c2 = st.columns([1.05, 1.0])
            with c1:
                st.markdown("**Initial board**")
                st.markdown(render_board_html(board.grid), unsafe_allow_html=True)
            with c2:
                st.markdown("**Final board**")
                st.markdown(render_board_html(result.board.grid), unsafe_allow_html=True)

            st.success(result.message if result.solved else result.message)

            metrics_df = pd.DataFrame([result.metrics.to_dict()])
            st.markdown("**Metrics**")
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

            st.markdown("**Step-by-step replay**")
            replay_events(result.events, speed)

        except Exception as exc:
            st.error(f"Could not solve puzzle: {exc}")

    if compare_clicked:
        try:
            board = parse_puzzle(puzzle_text)
            comparison_rows: List[Dict[str, object]] = []
            solved_boards = {}
            with st.spinner("Running selected configurations..."):
                for label in selected_comparisons:
                    config = compare_options[label]
                    result = solve_once(board, config)
                    row = {"configuration": label, "solved": result.solved, **result.metrics.to_dict()}
                    comparison_rows.append(row)
                    solved_boards[label] = result.board.grid

            if comparison_rows:
                df = pd.DataFrame(comparison_rows)
                st.markdown("**Performance comparison**")
                st.dataframe(df, use_container_width=True, hide_index=True)

                chart_metric = st.selectbox(
                    "Metric to chart",
                    ["Elapsed ms", "Nodes Explored", "Backtracks", "Assignments", "Domain Prunes", "AC3 Revisions"],
                    index=0,
                )
                fig = px.bar(df, x="configuration", y=chart_metric, color="solved", title=f"Comparison: {chart_metric}")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("**Solved boards**")
                cols = st.columns(max(1, min(3, len(solved_boards))))
                for idx, (label, grid) in enumerate(solved_boards.items()):
                    with cols[idx % len(cols)]:
                        st.markdown(f"**{label}**")
                        st.markdown(render_board_html(grid), unsafe_allow_html=True)
            else:
                st.info("Choose at least one comparison configuration.")
        except Exception as exc:
            st.error(f"Comparison failed: {exc}")

st.divider()
st.markdown(
    """
    **How the solver works**
    - Backtracking tries values recursively until the puzzle is solved.
    - Forward Checking removes impossible values from neighboring domains after each assignment.
    - AC-3 enforces arc consistency to propagate constraints.
    - MRV picks the most constrained unassigned cell first.
    """
)
