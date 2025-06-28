# Elite 1984 City Builder

A retro-themed city building game inspired by the wireframe graphics and minimalist UI of Elite (1984).

## Current Features (Work in Progress)

*   **Core City Building:**
    *   Place buildings on a grid.
    *   Manage resources: Credits, Power, Population, Ore (basic).
    *   Basic power simulation: Buildings generate or consume power. Shortages can affect building operation.
*   **Graphics & UI:**
    *   Pygame window for rendering.
    *   Placeholder wireframe graphics for buildings (simple characters and boxes).
    *   Minimalist UI panel displaying key resources and city status.
    *   Basic build menu.
*   **Game Progression:**
    *   City Ranks: Unlock new buildings by increasing your city's value (initial implementation).
*   **Save/Load System:**
    *   Save and load game progress to/from JSON files.
*   **Sound:**
    *   Basic sound manager implemented. (User needs to provide `.wav` sound files).
*   **Testing:**
    *   Unit tests for core game logic (city state, building placement, save/load).

## Planned Features / Next Steps

*   Refine wireframe graphics for more distinct building appearances.
*   Expand building types and their effects (e.g., dedicated ore mines, factories, advanced power).
*   More detailed economic simulation.
*   Enhanced UI/UX, including better visual feedback.
*   More complex game events (e.g., disasters, economic booms/busts - optional).

## Setup and Running

### Prerequisites

*   Python 3.8+
*   Pygame: `pip install pygame`
*   **Optional for developers:** If you wish to run the `sound.py` script directly *and* have it generate dummy `.wav` files for its own testing, you will also need `scipy` and `numpy`: `pip install scipy numpy`. These are **not** required to play the game itself.

### Running the Game

1.  Clone this repository or download the source code.
2.  Navigate to the root directory of the project.
3.  Run the main game file:
    ```bash
    python -m city_builder.main
    ```
    (Or `python city_builder/main.py` if you are in the directory containing `city_builder/`)

### Running Tests

To run the unit tests:

```bash
python -m unittest discover city_builder/tests
```
(Or navigate to `city_builder` parent directory and run `python -m unittest discover -s city_builder/tests -p "test_*.py"`)

## Project Structure

*   `city_builder/`: Main package for the game.
    *   `main.py`: Main game loop and event handling.
    *   `config.py`: Game settings, constants, building specifications.
    *   `city.py`: `City` class, manages resources, buildings, game state.
    *   `buildings.py`: `Building` class and related logic.
    *   `ui.py`: `UIManager` class for rendering UI elements and game view.
    *   `sound.py`: `SoundManager` for handling sound effects.
    *   `save_load.py`: Functions for saving and loading game state.
    *   `assets/`: Planned directory for game assets (e.g., sounds).
        *   `sounds/`: User should place `.wav` files here (e.g. `ui_click.wav`, `build_place.wav`).
    *   `tests/`: Unit tests for the game.
*   `city_builder_saves/`: Default directory where save games are stored.
*   `README.md`: This file.
*   `AGENTS.md`: Instructions and guidance for AI developers working on this codebase.

## Sound Files

The game includes a sound manager but **does not** provide sound files. To enable sound effects, you need to:

1.  Create a directory `city_builder/assets/sounds/`.
2.  Place your `.wav` sound files in this directory. The game will look for:
    *   `ui_click.wav` (for UI interactions)
    *   `build_place.wav` (when a building is placed)
    *   `error.wav` (for invalid actions)
    *   (More sounds can be added and configured in `main.py`)

If files are missing, the game will print a warning to the console but run without sound for those events.
The `sound.py` script includes an example to generate dummy `.wav` files using `scipy` if you have it installed and run that script directly. This is for testing the `SoundManager` itself, not for general game assets.
