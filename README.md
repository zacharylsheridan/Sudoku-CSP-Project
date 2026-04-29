# Sudoku CSP Solver and Visualizer

This project implements a Sudoku solver using Constraint Satisfaction Problem (CSP) techniques, along with an interactive visualization and performance comparison interface.

The solver supports the following strategies:
- Backtracking Search (baseline)
- Forward Checking (FC)
- Arc Consistency (AC-3)
- Minimum Remaining Values (MRV)

A Streamlit-based interface allows users to:
- input custom Sudoku puzzles
- visualize the solving process step-by-step
- toggle solver strategies on or off
- compare multiple configurations side-by-side
- analyze performance metrics

---

## Quick Start

From inside the project folder, using your shell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```
---

# Project Structure

sudoku_csp_project/
├── app.py                 # Streamlit UI
├── requirements.txt
├── README.md
├── sudoku/
│   ├── __init__.py
│   ├── board.py           # Board representation
│   ├── csp.py             # CSP structure
│   ├── solver.py          # Core solving logic
│   ├── metrics.py         # Performance tracking
│   └── puzzles.py         # Preset puzzles
└── tests/
    └── test_solver.py     # Unit tests

# Running the Application
- If the virtual environment is not active: 

```powershell
.venv\Scripts\activate
```
- Then run:
```powershell
streamlit run app.py
```
- A new instance of the program will open in the default browser of your machine.
---
## How to Use the Application

Once the app is running (`streamlit run app.py`), follow the steps below.

---

### Running a Solver Instance

1. **Select a puzzle**
   - Choose a preset puzzle from the dropdown, or
   - Enter a custom puzzle as an 81-character string

2. **Configure the solver**
   - Toggle the following options:
     - Forward Checking (FC)
     - Arc Consistency (AC-3)
     - Minimum Remaining Values (MRV)

3. **Run the solver**
   - Click **"Solve selected configuration"**

4. **View results**
   - The initial and solved boards will be displayed
   - A metrics table will show:
     - nodes explored
     - backtracks
     - assignments
     - domain prunes
     - AC-3 revisions
     - runtime (ms)

5. **Watch the solving process**
   - A step-by-step replay will animate:
     - variable selection
     - assignments
     - backtracking
     - domain updates

---

### Running the Comparison Panel

1. **Select a puzzle**
   - Choose a preset or enter a custom puzzle

2. **Choose comparison configurations**
   - Select one or more solver configurations from the list
   - Example configurations:
     - Backtracking
     - Backtracking + FC
     - Backtracking + AC-3 + MRV

3. **Run comparison**
   - Click **"Run comparison panel"**

4. **View performance results**
   - A table will display metrics for each configuration:
     - nodes explored
     - backtracks
     - assignments
     - domain prunes
     - AC-3 revisions
     - runtime (ms)

5. **Analyze the chart**
   - Use the dropdown to select a metric (e.g., elapsed time, nodes explored)
   - A bar chart will visualize performance differences

6. **Compare solutions**
   - Final solved boards for each configuration are displayed side-by-side

---
# Input Format

Enter a Sudoku puzzle as an 81-character string.
- Digits 1-9 represent fixed values(filled squares)
- 0 or . represent empty cells

Example:
```
530070000600195000098000060800060003400803001700020006060000280000419005000080079
```
---
# Expected Output
After running the application:
- The initial and final Sudoku boards are displayed
- A metrics table shows solver performance
- A step-by-step replay animates the solving process
- A comparison chart appears when multiple configurations are selected
---
# Important Notes
- Plain Backtracking may take a very long time on expert-level puzzles
- Heuristics (FC, AC-3, MRV) significantly improve performance
- The comparison panel runs configurations sequentially
---
# Authors:
- Zachary Sheridan
- Layla Jones
- Minh Nguyen
- Ngoc Vu Khoa Nguyen
