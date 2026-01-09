# 🧩 CSP Sudoku Solver

An AI-powered Sudoku solver that implements **Constraint Satisfaction Problem (CSP)** algorithms to efficiently solve puzzles of varying difficulties. Built with a clean GUI for interactive solving and visualization of algorithm behavior.

## 🎯 Project Overview

This project demonstrates the application of advanced AI search algorithms to solve Sudoku puzzles. The solver uses **AC-3 (Arc Consistency)** for constraint propagation and **Backtracking with MAC (Maintaining Arc Consistency)** for intelligent search, showcasing how CSP techniques can efficiently solve complex constraint problems.

## ✨ Key Features

- **Smart Puzzle Generation**: Generates valid Sudoku puzzles with guaranteed unique solutions across Easy, Medium, and Hard difficulties
- **AC-3 Algorithm**: Implements arc consistency to reduce domain sizes before search
- **Backtracking with MAC**: Uses Minimum Remaining Values (MRV) heuristic for optimal variable selection
- **Interactive GUI**: Tkinter-based interface with real-time domain visualization and conflict detection
- **Visual Feedback**: Shows possible values (domains) for each cell and highlights conflicts during manual solving

## 🧠 What We Learned

### Constraint Satisfaction Problems
- Modeling Sudoku as a CSP with variables, domains, and constraints
- Understanding binary constraints in row, column, and 3×3 box relationships
- Implementing constraint propagation for early pruning

### AI Search Algorithms
- **AC-3 Algorithm**: Enforcing arc consistency to reduce search space
- **Backtracking Search**: Recursive depth-first search with intelligent variable ordering
- **Minimum Remaining Values (MRV)**: Heuristic for selecting the most constrained variable first
- **Maintaining Arc Consistency (MAC)**: Running AC-3 after each assignment to detect failures early

### Software Engineering
- Separation of concerns with modular architecture (GUI, solver, generator)
- Deep copying domains to maintain state during backtracking
- Queue management for constraint propagation efficiency

## 🏗️ Architecture

```
src/
├── arc3.py              # AC-3 algorithm implementation
├── back_track.py        # Backtracking with MAC and MRV heuristic
├── make_constrain.py    # Constraint graph generation
├── solve_puzzle.py      # Main solving pipeline
├── sudoku_generator.py  # Puzzle generation with difficulty levels
├── gui.py               # Interactive Tkinter interface
└── main.py              # Application entry point
```

## 🚀 Usage

Run the application:
```bash
python src/main.py
```

**Mode 1 - Generate & Solve**: Generate a random puzzle and watch the AI solve it step by step  
**Mode 2 - Manual Entry**: Input your own puzzle and solve it manually or with AI assistance

## 🛠️ Technologies

**Language**: Python  
**GUI Framework**: Tkinter  
**Algorithms**: AC-3, Backtracking, MRV Heuristic, MAC  
**Concepts**: Constraint Satisfaction Problems, Search, Constraint Propagation
