# Othello - DAA Project

A Python implementation of the classic board game **Othello (Reversi)**, featuring interactive algorithm visualization to demonstrate **Minimax (with Alpha-Beta Pruning)** and **Greedy** strategies.

## Features

*   **Game Modes:** 1 Player (vs AI) and 2 Players (PvP).
*   **AI Algorithms:** Minimax (smart) and Greedy (simple).
*   **Visualization:** Real-time AI search tree view, heatmaps, and move hints.
*   **Interfaces:** Modern Graphical UI and classical Terminal UI.

## Requirements

*   Python 3.x
*   `pygame`

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install pygame
    ```

## How to Run

### Graphical Version (Recommended)
Calculates layout dynamically based on window size.

```bash
python main_pygame.py
```

**Controls:**
*   **Click:** Select Game Mode / Grid Size / Make Move
*   **'A' Key:** Toggle Algorithm Visualization (On/Off)
*   **'H' Key:** Toggle Heatmap Overlay (On/Off)
*   **'F' Key:** Toggle Fullscreen

### Terminal Version
Simple text-based interface.

```bash
python main_terminal.py
```

## Project Structure

*   `main_pygame.py`: Entry point for the GUI game.
*   `main_terminal.py`: Entry point for the CLI game.
*   `algorithms/`:
    *   `graph.py`: Search Algorithms (Minimax, Alpha-Beta) and visualization generators.
    *   `greedy.py`: Greedy strategy logic.
    *   `heuristics.py`: Board evaluation weights.
*   `model/`:
    *   `board.py`: Core game logic.
    *   `game_state.py`: State representation.
*   `ui/`:
    *   `pygame_gui.py`: Main GUI logic.
    *   `terminal.py`: Terminal UI logic.
