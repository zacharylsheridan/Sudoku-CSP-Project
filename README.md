# Sudoku CSP Solver and Visualizer

This project implements a full Sudoku solver as a Constraint Satisfaction Problem (CSP) with configurable strategies:

* Backtracking Search
* Forward Checking (FC)
* Arc Consistency (AC-3)
* Minimum Remaining Values (MRV)

It also includes a Streamlit front-end that:

* accepts a manual puzzle input
* animates the solving process step by step
* lets users toggle heuristics on or off
* compares multiple configurations side by side
* reports performance metrics such as nodes explored, backtracks, and solve time

## Project structure

sudoku\_csp\_project/
├── app.py
├── requirements.txt
├── README.md
├── sudoku/
│   ├── \_\_init\_\_.py
│   ├── board.py
│   ├── csp.py
│   ├── solver.py
│   ├── puzzles.py
│   └── metrics.py
└── tests/
    └── test\_solver.py


## Install(Virtual Env)

py -3.11 -m venv .venv

.venv\\Scripts\\activate

python -m pip install --upgrade pip

pip install -r requirements.txt

## Run(After venv folder exists)
.venv\\Scripts\\activate
streamlit run app.pyRun



## Input format

Enter a puzzle as 81 characters.

* Digits `1-9` are fixed values
* `0` or `.` mean empty

Example:

530070000600195000098000060800060003400803001700020006060000280000419005000080079


## Notes

* The visualization replays the event log produced by the solver.
* AC-3 can run both as preprocessing and during search after assignments.
* The comparison panel runs several selected strategy combinations on the same puzzle and displays a metrics table and charts.
