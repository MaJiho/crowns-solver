import json
import pickle
from pathlib import Path
from PIL import Image
import numpy as np
import cv2

# Base directory for resolving paths
BASE_DIR = Path(__file__).resolve().parent.parent


def make_relative(absolute_path):
    """
    Convert an absolute path to a path relative to the base directory.
    """
    return absolute_path.relative_to(BASE_DIR)


def resolve_path(relative_path):
    """
    Resolve a path relative to the base directory.
    """
    return BASE_DIR / relative_path


def load_json(file_path):
    """
    Load a JSON file and return its contents as a dictionary.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON format in: {file_path}")
        return None


def save_json(file_path, data):
    """
    Save data to a JSON file.
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")


def load_pickle(file_path):
    """
    Load a pickle file and return the object.
    """
    try:
        with open(file_path, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        print(f"Pickle file not found: {file_path}")
        return None
    except pickle.UnpicklingError:
        print(f"Error unpickling file: {file_path}")
        return None


def save_pickle(file_path, obj):
    """
    Save an object to a pickle file.
    """
    try:
        with open(file_path, "wb") as file:
            pickle.dump(obj, file)
    except Exception as e:
        print(f"Error saving pickle to {file_path}: {e}")


def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, and create it if it doesn't.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def save_png(save_path, image):
    """
    Save the image as a PNG file. If the input is a numpy array, it will be converted.

    Args:
        save_path (str): Path where the PNG file should be saved.
        image: Image data (either numpy.ndarray or PIL.Image).
    """
    # If the image is a numpy ndarray (OpenCV format)
    if isinstance(image, np.ndarray):
        # Convert it to RGB (if it's not already in RGB format)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Convert numpy array to PIL Image
        image = Image.fromarray(image_rgb)

    # If the image is already a PIL Image, no conversion is needed
    if isinstance(image, Image.Image):
        image.save(save_path)
    else:
        raise TypeError("Unsupported image format. Please provide a numpy ndarray or PIL Image.")
