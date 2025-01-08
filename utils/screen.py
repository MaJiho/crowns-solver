import cv2
import numpy as np
import pyautogui

from board.board import Board
from board.cell import Cell
from board.gridline import Gridline
from settings.settings import get_setting
from utils.file import resolve_path, save_png


def capture_screenshot_of_grid(grid_area, save_path):
    """
    Capture a screenshot of the selected grid area and save it to a file.

    Args:
        grid_area (tuple): (x, y, width, height) of the grid area.
        save_path (str): Path to save the screenshot.

    Returns:
        None
    """
    x, y, width, height = grid_area
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    save_png(save_path, screenshot)


def load_and_preprocess_image(image_path, save_intermediate=False):
    """
    Loads an image from the specified path, converts it to grayscale,
    and thresholds it to create a binary image.

    Args:
        image_path (str): Path to the image file.
        save_intermediate (bool): Whether to save the grayscale and binary images.

    Returns:
        tuple: Original image (numpy array) and binary image (numpy array).
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use resolve_path to get proper paths for saving intermediate images
    binary_path = resolve_path(get_setting("paths.screenshot_binary_img"))
    grayscale_path = resolve_path(get_setting("paths.screenshot_grayscale_img"))

    if save_intermediate:
        # Save grayscale image using save_png from file.py
        save_png(grayscale_path, gray)

    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    if save_intermediate:
        # Save binary image using save_png from file.py
        save_png(binary_path, binary)

    return img, binary



def find_game_board(binary_image, save_intermediate=False):
    """
    Identifies the largest rectangular contour in the binary image,
    assumed to be the game board, and extracts its bounding rectangle.

    Args:
        binary_image (numpy array): The binary image, where the game board is assumed to be the largest square.
        save_intermediate (bool): If True, saves the extracted board as an intermediate image for debugging purposes.

    Returns:
        tuple: A tuple containing the following:
            - x (int): The x-coordinate of the top-left corner of the board's bounding rectangle.
            - y (int): The y-coordinate of the top-left corner of the board's bounding rectangle.
            - w (int): The width of the board's bounding rectangle.
            - h (int): The height of the board's bounding rectangle.
            - board (numpy array): The cropped binary image of the detected game board.

    Raises:
        ValueError: If no suitable game board is found in the binary image.
    """
    binary_board_path = get_setting("paths.board_binary_img")

    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h

        # Validate square aspect ratio
        if not (0.9 <= aspect_ratio <= 1.1):
            continue

        # Check for nested smaller squares
        nested_contours = sum(1 for i in hierarchy[0] if i[3] != -1)
        if nested_contours < 5:  # Expect at least 5 inner squares
            continue

        # Validate gridlines
        board = binary_image[y:y + h, x:x + w]
        edges = cv2.Canny(board, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
        if lines is None or len(lines) < 5:  # Require at least 5 lines
            continue

        # Save intermediate result
        if save_intermediate:
            cv2.imwrite(binary_board_path, board)

        return x, y, w, h, board

    raise ValueError("Game board not found!")


def square_corners(cropped_binary):
    height, width = cropped_binary.shape

    # Check if any of the corners are rounded (if any corner has a value of 0)
    if cropped_binary[0, 0] == 0 or cropped_binary[0, width - 1] == 0 or cropped_binary[height - 1, 0] == 0 or \
            cropped_binary[height - 1, width - 1] == 0:

        # VERTICAL LEFT AND RIGHT
        v_thickness = 0

        # Find the first row where a black pixel is on the wall (left side)
        for row in range(height):
            if cropped_binary[row, 0] == 255:
                # Count the thickness of the leftmost vertical line
                while v_thickness < width and cropped_binary[row, v_thickness] == 255:
                    v_thickness += 1
                break

        # HORIZONTAL UP AND DOWN
        h_thickness = 0
        # Find the first column where a black pixel is on the wall (top side)
        for col in range(width):
            if cropped_binary[0, col] == 255:
                # Count the thickness of the topmost horizontal line
                while h_thickness < height and cropped_binary[h_thickness, col] == 255:
                    h_thickness += 1
                break

        # Left side
        for row in range(height):
            cropped_binary[row, :v_thickness] = 255
        # Right side
        for row in range(height):
            cropped_binary[row, width - v_thickness:] = 255
        # Top side
        for c in range(width):
            cropped_binary[:h_thickness, c] = 255
        # Bottom side
        for col in range(width):
            cropped_binary[height - h_thickness:, col] = 255

        # Paint inner corners black
        cropped_binary[h_thickness, v_thickness] = 0
        cropped_binary[-h_thickness - 1, v_thickness] = 0
        cropped_binary[h_thickness, -v_thickness - 1] = 0
        cropped_binary[-h_thickness - 1, -v_thickness - 1] = 0

    return cropped_binary


def normalize_grid(cropped_binary):
    # Step 1: Squaring corners
    square_cropped_binary = square_corners(cropped_binary)

    return square_cropped_binary


def detect_gridlines(board):
    """
    Detects vertical and horizontal gridlines in the binary board image.

    Args:
        board (numpy array): The cropped binary image of the game board.

    Returns:
        tuple: Two lists containing Gridline objects for horizontal and vertical gridlines.
    """
    # Initialize lists to store the gridlines
    horizontal_gridlines = []
    vertical_gridlines = []

    # Detect horizontal gridlines (scan rows)
    for row in range(board.shape[0]):  # Loop over rows
        # Check for mixed white and black pixels (not all white)
        if np.any(board[row, :] == 255) and np.any(board[row, :] == 0):  # Mixed white and black
            # Look for groups of white pixels
            start = None
            thickness = 0
            for col in range(board.shape[1]):
                if board[row, col] == 255:  # White pixel
                    if start is None:
                        start = col
                    thickness += 1
                else:
                    if start is not None:
                        # We have a group of white pixels, save the gridline in the middle
                        mid_position = (start + col - 1) // 2  # Middle pixel
                        horizontal_gridlines.append(Gridline(mid_position, thickness, 'horizontal'))
                        start = None
                        thickness = 0
            if start is not None:  # Last group of white pixels in the row
                mid_position = (start + board.shape[1] - 1) // 2
                horizontal_gridlines.append(Gridline(mid_position, thickness, 'horizontal'))
                break

    # Detect vertical gridlines (scan columns)
    for col in range(board.shape[1]):  # Loop over columns
        # Check for mixed white and black pixels (not all white)
        if np.any(board[col, :] == 255) and np.any(board[col, :] == 0):  # Mixed white and black
            # Look for groups of white pixels
            start = None
            thickness = 0
            for row in range(board.shape[0]):
                if board[row, col] == 255:  # White pixel
                    if start is None:
                        start = row
                    thickness += 1
                else:
                    if start is not None:
                        # We have a group of white pixels, save the gridline in the middle
                        mid_position = (start + row - 1) // 2  # Middle pixel
                        vertical_gridlines.append(Gridline(mid_position, thickness, 'vertical'))
                        start = None
                        thickness = 0
            if start is not None:  # Last group of white pixels in the column
                mid_position = (start + board.shape[0] - 1) // 2
                vertical_gridlines.append(Gridline(mid_position, thickness, 'vertical'))
                break

    return horizontal_gridlines, vertical_gridlines


def compute_cell_coordinates(rows, cols, x, y):
    """
    Computes the coordinates of each square cell on the game board.

    Args:
        rows (list): A list of Gridline objects for horizontal gridlines.
        cols (list): A list of Gridline objects for vertical gridlines.
        x (int): The x-coordinate of the top-left corner of the board.
        y (int): The y-coordinate of the top-left corner of the board.

    Returns:
        list: A list of Cell objects representing each cell's position and size.
    """
    cells = []

    # Assuming cells are square-shaped, so width = height
    for i in range(len(rows) - 1):
        for j in range(len(cols) - 1):
            # Top-left corner (x, y) for each cell
            cell_x = cols[j].position
            cell_y = rows[i].position

            # The size of the cell is determined by the distance between consecutive gridlines
            cell_size = min(cols[j + 1].position - cols[j].position, rows[i + 1].position - rows[i].position)

            # Create a Cell object with the position and size
            cell = Cell.from_top_left((cell_x, cell_y), cell_size)
            cells.append(cell)

    return cells


def color_cells(original_image, cells, x, y):
    """
    Colors the cells by extracting the color from the original image at the cell positions.

    Args:
        original_image (numpy array): The original (color) image.
        cells (list): List of Cell objects representing the cells.
        x (int): The x-coordinate of the top-left corner of the cropped board in the original image.
        y (int): The y-coordinate of the top-left corner of the cropped board in the original image.

    Returns:
        list: List of Cell objects with updated color information.
    """
    for cell in cells:
        # Adjust the cell position from the cropped image to the original image
        cell_x = cell.x + x
        cell_y = cell.y + y

        # Get the color of the pixel at (cell_x, cell_y) from the original image
        bgr_color = original_image[cell_y, cell_x]  # Color is in BGR format

        # Convert BGR to RGB
        rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])

        # Set the color of the cell
        cell.set_color(rgb_color)

    return cells


def detect_game_board(image_path, grid_area, save_intermediate=False):
    """
    Detects the game board grid from a screenshot image and optionally saves intermediate images.

    Args:
        image_path (str): Path to the image file.
        grid_area (tuple): The (x, y, w, h) coordinates of the grid area on the screen.
        save_intermediate (bool): Whether to save intermediate images.

    Returns:
        dict: A dictionary containing grid coordinates and cell details, including:
              - "grid_top_left": Coordinates of the top-left corner of the board.
              - "grid_bottom_right": Coordinates of the bottom-right corner of the board.
              - "cells": List of dictionaries with cell coordinates.
              - "rows": Number of rows in the grid.
              - "columns": Number of columns in the grid.
    """
    # Step 1: Load and preprocess the image
    img, binary = load_and_preprocess_image(image_path, save_intermediate)

    # Step 2: Find the game board
    x, y, w, h, cropped_binary = find_game_board(binary, save_intermediate)

    # Combine grid_area (screen position) with board position within the image
    grid_top_left_screen = (grid_area[0] + x, grid_area[1] + y)
    grid_bottom_right_screen = (grid_area[0] + x + w, grid_area[1] + y + h)

    # Step 3: Normalize lines in board
    board = normalize_grid(cropped_binary)

    # Step 3: Detect gridlines
    rows, cols = detect_gridlines(board)

    # Step 4: Compute cell coordinates
    cells = compute_cell_coordinates(rows, cols, x, y)

    # Step 5: Color the cells by extracting color information from the original image
    colored_cells = color_cells(img, cells, x, y)

    board_obj = Board(grid_top_left_screen, colored_cells)

    # Return the details
    return board_obj
