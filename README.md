# CNF_Maze

A CNF-based knowledge representation project for **localizing an agent in a maze** using **movement actions** and **sensor observations**.  
The program maintains a **belief state** over all possible positions and updates it with every step using **propositional logic in CNF** and `sympy`.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Maze Representation](#maze-representation)
  - [Knowledge Base & CNF](#knowledge-base--cnf)
  - [Belief Update](#belief-update)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Controls](#controls)
- [Example Scenario](#example-scenario)
- [Limitations and Notes](#limitations-and-notes)
- [Contributors](#contributors)
- [License](#license)

---

## Overview

**CNF_Maze** is a small AI project that demonstrates how to use **propositional logic in CNF** to perform **robot localization** in a maze.

- The true position of the agent in the maze is **hidden** from the user.
- At each time step, the user chooses an **action** (move North/South/East/West or stay).
- The environment returns a **sensor percept**: a 4-bit pattern describing walls around the agent.
- A **CNF knowledge base** uses these actions and percepts to infer which cells are still **logically consistent** with the observations.
- The GUI visualizes the maze and the **current belief** (possible positions).

This project is mainly educational and inspired by topics in **AI knowledge representation**, **uncertainty**, and **logical inference**.

---

## Features

- Grid-based maze loaded from a text file (`maze.txt`)
- Graphical visualization using **pygame**
- CNF-based knowledge base using **sympy**
- Exact-one constraints for agent position at each time step
- Transition constraints based on chosen actions
- Sensor constraints based on 4-bit wall observations
- Step-by-step **belief update**: possible positions are shown in green
- Hidden true position is revealed at the end in blue

---

## Project Structure

```text
CNF_Maze/
├── main.py          # Entry point: loads maze, initializes KB and GUI, starts the loop
├── gui.py           # Pygame-based GUI to visualize maze, belief, and handle user input
├── logic.py         # CNF-based localization knowledge base (LocalizationKB)
├── maze.txt         # Maze layout (0 = free cell, 1 = wall)
├── گزارش پروژه AI.pdf  # Project report in Persian (design and explanation)
└── README.md        # This file
```

### `main.py`

- Loads the maze from `maze.txt`
- Creates the knowledge base:
  ```python
  kb = LocalizationKB(maze)
  ```
- Creates the GUI:
  ```python
  gui = MazeGUI(maze, kb)
  ```
- Starts the application:
  ```python
  gui.run()
  ```

### `gui.py`

Responsible for:

- Drawing the maze grid in a window
- Coloring:
  - **Walls** (black/gray)
  - **Free cells**
  - **Belief cells** (possible positions) in **green**
  - **True agent position** (revealed at the end) in **blue**
- Handling keyboard input (W/A/S/D or arrow keys)
- Requesting percepts from the environment
- Sending `(action, percept)` pairs to the knowledge base
- Displaying history of actions and percepts

### `logic.py`

Contains the **logic and CNF**:

- `LocalizationKB` class:
  - Creates symbolic variables `v_r_c_t` for each free cell `(r, c)` at time `t`
  - Adds:
    - **exactly-one** location constraint for each time
    - **transition** constraints based on actions
    - **sensor** constraints based on wall-percepts
  - Uses `sympy.logic.inference.satisfiable` to compute consistent worlds
  - Stores the **belief state** (set of possible positions) at each time step

### `maze.txt`

A simple 0/1 grid (8 rows × 7 columns):

- `1` = wall
- `0` = free cell

The outer border is walls, and inner 0/1 values define corridors and obstacles.

---

## How It Works

### Maze Representation

- The maze is read from `maze.txt` as a 2D array.
- Only cells with value `0` are valid positions for the agent.
- At each time step `t`, the agent is assumed to be in **exactly one** free cell.

### Knowledge Base & CNF

The knowledge base uses propositional symbols:

```text
v_r_c_t  =  "agent is at row r, column c at time t"
```

For each time step:

1. **Exactly-one position constraint**
   - At least one cell is true:
     \[
     v_{1} \lor v_{2} \lor \dots \lor v_{n}
     \]
   - No two different cells can be true simultaneously:
     \[
     \forall i \neq j : \neg(v_i \land v_j)
     \]

2. **Transition constraints**
   - When the user chooses an action (N, S, E, W, O), the KB encodes how position at time `t-1` can lead to positions at time `t`.
   - Invalid moves (walking into walls or outside the maze) are disallowed by the CNF clauses.

3. **Sensor (percept) constraints**
   - The environment provides a 4-bit pattern indicating walls around the agent (e.g., [North, South, East, West]).
   - For each candidate cell, the KB computes what wall pattern **should** be observed there.
   - If this pattern does **not** match the actual percept, that cell is ruled out by adding `Not(v_r_c_t)` to the KB.

### Belief Update

After each action + percept:

1. The KB adds:
   - new transition clauses
   - new sensor clauses
2. Using `satisfiable(...)`, it enumerates models that satisfy all clauses so far.
3. The set of all positions `(r, c)` that appear as true in any satisfying assignment forms the **belief state** at time `t`.
4. The GUI highlights these cells in green.

Over time, as more evidence is added, the belief usually **shrinks** until ideally only the true position remains.

---

## Installation

Make sure you have **Python 3.8+** installed.

Install required packages:

```bash
pip install pygame sympy
```

The code also uses standard-library modules such as:

- `itertools`
- `random`

(These do not require installation.)

> Note: If you run this project inside a virtual environment, activate it before installing dependencies.

---

## How to Run

Clone or download the repository, then from inside the project directory run:

```bash
python main.py
```

or, depending on your system:

```bash
python3 main.py
```

A pygame window should open, showing:

- The maze grid
- Belief cells in green
- A side panel (or status area) with actions and percept history

---

## Controls

Use the keyboard to move the agent:

- **W** or **↑** : move **North** (up)
- **S** or **↓** : move **South** (down)
- **D** or **→** : move **East** (right)
- **A** or **←** : move **West** (left)

If a move would hit a wall, the true agent usually stays in place (depending on the exact logic), and the KB takes this into account via transitions and sensor readings.

Usually, there is also an option to **stay in place** (action `O`) in the logic, but it may not be mapped to a key in the GUI depending on implementation.

At the end (or on a specific key/condition), the program can reveal the **true position** in blue so you can compare it with the final belief.

---

## Example Scenario

1. Program chooses a random free cell as the **hidden true start**.
2. At time `t = 0`, your belief is spread across many possible cells.
3. You press **D** (East).  
   - The environment tries to move the true agent east, if possible.
   - It computes the new wall-percept in the new position.
   - `LocalizationKB` adds transition + sensor clauses and updates belief.
4. Several cells become logically impossible and are removed from the belief.
5. You continue moving and observing; the belief shrinks.
6. At the end, the program reveals the true position and you can see whether the logical inference localized the agent correctly.

---

## Limitations and Notes

- Maze and logic are kept intentionally simple for educational purposes.
- Inference uses `sympy.logic.inference.satisfiable`, which is fine for small mazes and short time horizons, but **does not scale** to very large grids or long sequences.
- The project does not implement probabilistic reasoning (like HMMs or particle filters); it is purely **logical (CNF)**.
- The report file (`report AI maze project.pdf`) is in Persian and explains:
  - design of the CNF
  - how constraints are constructed
  - how observations refine the belief state step-by-step.

---

## Contributors

Members:

- **Soheil Bateni**
- **Mohammad Alami**

---

## License

This project is for educational and personal use. Feel free to fork and improve it!

(Or replace with GPL/Apache/… as appropriate.)

---
