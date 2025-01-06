from input_utils import click_and_drag_to_capture
from screen_utils import capture_screenshot_of_grid, detect_game_board
from settings import load_settings, get_setting
from solver import Solver


def main():
    # Load settings at the start
    load_settings()

    print("Step 1: Define the grid area using click-and-drag.")

    # Step 1: Click and drag to define the grid area
    grid_area = click_and_drag_to_capture()
    if not grid_area:
        print("Failed to capture the grid area. Exiting.")
        return

    print("\nStep 2: Capture the grid area screenshot.")

    # Step 2: Capture the screenshot of the selected area
    screenshot_path = get_setting("screenshot_img_path")
    capture_screenshot_of_grid(grid_area, save_path=screenshot_path)

    # Step 3: Pass grid_area (x, y, w, h) to the function
    board_obj = detect_game_board(screenshot_path, grid_area, save_intermediate=True)

    # Step 4: Solve the game board
    solver = Solver(board_obj)
    solver.solve()


if __name__ == "__main__":
    main()
