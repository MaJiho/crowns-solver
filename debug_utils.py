import pickle

from settings import get_setting


def load_board_state(filename=None):
    """
    Loads a board state from a file.

    Args:
        filename (str): The name of the file to load the board state from.

    Returns:
        The board object if successfully loaded, or None if an error occurs.
    """
    if filename is None:
        filename = "../" + get_setting("board_obj_path")
    try:
        with open(filename, "rb") as file:
            board_state = pickle.load(file)
            print(f"Board state loaded from {filename}")
            return board_state
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error loading board state: {e}")
    return None
