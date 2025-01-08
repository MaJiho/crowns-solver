import pickle

from settings.settings import get_setting
from utils.file import resolve_path


def load_board_state():
    """
    Loads a board state from a file.

    Args:
        filename (str): The name of the file to load the board state from.

    Returns:
        The board object if successfully loaded, or None if an error occurs.
    """
    filename = get_setting("paths.board_obj")
    file_path = resolve_path(filename)
    try:
        with open(file_path, "rb") as file:
            board_state = pickle.load(file)
            print(f"Board state loaded from {file_path}")
            return board_state
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error loading board state: {e}")
    return None
