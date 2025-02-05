# Gomoku Game

This repository contains an implementation of the Gomoku game, combining Python and C++ components to offer a fast and interactive experience.

## Overview

- **Game Logic & UI:** Implemented in [main.py](main.py) and [render.py](render.py).
- **Core Evaluations & Heuristics:** Implemented in C++ within the [src/](src/) folder:
  - [`bitwise_heuristic`](src/bitwise_heuristic.cpp)
  - [`star_heuristic`](src/star_heuristic.cpp)
  - [`new_bot_play`](src/new_minimax.cpp)
- **Move Generation & Rule Enforcement:** See [moves_generator.cpp](src/moves_generator.cpp) and [is_won.cpp](src/is_won.cpp).

## Build and Run

### Compiling C++ Components
Use the provided [Makefile](Makefile) to compile the performance-critical C++ modules:
```sh
make
```
## Running the Python Game
1. Install dependencies:
```sh
pip install -r requirements.txt
```
2. Run the game:
```sh
python3 main.py
```
## Game Features
- Single-player & Multiplayer Modes: Enjoy different modes using human players or AI.
- Bot Player: The AI uses a minimax algorithm (new_bot_play) with advanced board evaluation.
- Heuristic Evaluations: Leverages bitwise_heuristic and star_heuristic for move scoring.
- Undo & Suggestion: The UI provides undo options (draw_undo_button) and move suggestions (draw_suggestion_button).

## Controls
- Place a Move: Click on the board.
- Undo a Move: Click the "UNDO" button.
- Move Suggestions: Toggle suggestions using the question mark button.

