from typing import Optional, Dict, Tuple

import pyautogui
import pynput.mouse as mouse


def click_and_drag_to_capture():
    """
    Allow the user to click and drag to select an area on the screen,
    while suppressing mouse events.
    """
    positions: Dict[str, Optional[Tuple[int, int]]] = {"start": None, "end": None}
    dragging = {"is_dragging": False}

    # Define the event filter to capture and suppress mouse events
    def win32_event_filter(msg, data):
        if msg == 0x0201:  # Left mouse button down (WM_LBUTTONDOWN)
            # Start of drag
            positions["start"] = (data.pt.x, data.pt.y)
            dragging["is_dragging"] = True
            print(f"Start position: {positions['start']}")
            listener.suppress_event()  # type: ignore
            return False  # Stop propagation
        elif msg == 0x0202:  # Left mouse button up (WM_LBUTTONUP)
            # End of drag
            if dragging["is_dragging"]:
                positions["end"] = (data.pt.x, data.pt.y)
                dragging["is_dragging"] = False
                print(f"End position: {positions['end']}")
                listener.stop()  # Stop the listener after the drag is complete
                listener.suppress_event()  # type: ignore
                return False  # Stop propagation
        return True  # Allow other events

    # Start the mouse listener for capturing clicks and drag
    with mouse.Listener(win32_event_filter=win32_event_filter) as listener:
        print("Click and drag to select an area.")
        listener.join()

    # Process coordinates once drag is completed
    if positions["start"] and positions["end"]:
        x1, y1 = positions["start"]
        x2, y2 = positions["end"]

        # Calculate the top-left corner and dimensions of the selected area
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        print(f"Selected area: x={x}, y={y}, width={width}, height={height}")
        return x, y, width, height

    print("Selection failed. Please try again.")
    return None


def click_at(coords, duration=0.2):
    """
    Click at specific coordinates.

    Args:
        coords (tuple): (x, y) coordinates to click.
        duration (float): Duration of the mouse movement.
    """
    x, y = coords
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()


def click_and_drag(start_coords, end_coords, duration=0.5):
    """
    Simulates a click-and-drag action from one position to another.

    Args:
        start_coords (tuple): Starting (x, y) coordinates for the drag.
        end_coords (tuple): Ending (x, y) coordinates for the drag.
        duration (float): Duration of the mouse movement between the two positions.
    """
    # Move to the starting position and press the mouse button down
    pyautogui.moveTo(start_coords[0], start_coords[1])
    pyautogui.mouseDown()

    # Drag to the ending position
    pyautogui.moveTo(end_coords[0], end_coords[1], duration=duration)

    # Release the mouse button
    pyautogui.mouseUp()


def click_on_all_cells(board_obj, duration=0.02):
    """
    Clicks on every cell of the game board by calculating the center of each cell
    and using the click_at function.

    Args:
        board_obj (Board): The Board object containing the cells.
        duration (float): Duration of the mouse movement for each click.
    """
    rows, cols = board_obj.get_dimensions()

    # Iterate over every row and column
    for row in range(rows):
        for col in range(cols):
            # Get the cell at (row, col)
            cell = board_obj.get_cell_at(row, col)

            # Calculate the center of the cell
            cell_x = cell.x + board_obj.top_left[0]
            cell_y = cell.y + board_obj.top_left[1]

            # Click at the center of the cell
            click_at((cell_x, cell_y), duration)

    print("Clicked on all cells.")
