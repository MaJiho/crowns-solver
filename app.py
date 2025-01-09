from pathlib import Path

from utils import file
from utils.file import resolve_path
from utils.input import click_and_drag_to_capture
from utils.screen import capture_screenshot_of_grid, detect_game_board
from settings.settings import load_settings, get_setting
from solver.solver import Solver

# Base directory for resolving paths
file.STARTING_PATH = Path(__file__).resolve()


def process_game_board():
    """
    Main logic for processing the game board, triggered by the UI or CLI.
    """
    # Step 1: Click and drag to define the grid area
    print("Step 1: Define the grid area using click-and-drag.")
    grid_area = click_and_drag_to_capture()
    if not grid_area:
        return False

    # Step 2: Capture the screenshot of the selected area
    print("\nStep 2: Capture the grid area screenshot.")
    screenshot_path = resolve_path(get_setting("paths.screenshot_img"))
    capture_screenshot_of_grid(grid_area, save_path=screenshot_path)

    # Step 3: Pass grid_area (x, y, w, h) to the function
    board_obj = detect_game_board(screenshot_path, grid_area, save_intermediate=True)

    # Step 4: Solve the game board
    solver = Solver(board_obj)
    solver.solve()

    return True


def main():
    """
    CLI entry point for the application.
    """
    # Load settings at the start
    load_settings()

    # Process the game board through the main logic
    success = process_game_board()
    if success:
        print("\nGame board solved successfully!")
    else:
        print("\nGame board solving failed.")


if __name__ == "__main__":
    main()
