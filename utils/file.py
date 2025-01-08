import json
import os
import pickle
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Base directory for resolving paths
BASE_DIR = Path(__file__).resolve().parent.parent
# Executable directory
STARTING_PATH: Path | None = None


def make_relative(absolute_path):
    """
    Convert an absolute path to a path relative to the executable directory (STARTING_PATH).

    Args:
        absolute_path (str or Path): The absolute path to convert.

    Returns:
        Path: The relative path from STARTING_PATH to the given absolute_path.

    Raises:
        ValueError: If STARTING_PATH is not set or the paths cannot be made relative.
    """
    if STARTING_PATH is None:
        raise ValueError("STARTING_PATH is not set. Please set it before calling this function.")

    absolute_path = Path(absolute_path).resolve()
    base_path = STARTING_PATH.resolve()

    # If STARTING_PATH is a file, use its parent directory
    if base_path.is_file():
        base_path = base_path.parent

    try:
        # Attempt to calculate the relative path
        relative_path = absolute_path.relative_to(base_path)
    except ValueError:
        # If paths don't share a common base, calculate manually using os.relpath
        relative_path = Path(os.path.relpath(absolute_path, base_path))

    return relative_path


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


def read_image(image_path: Path):
    """
    Reads an image from the specified path. If the image is not found, it attempts to resolve the
    path by making it relative before trying to load the image again.

    Args:
        image_path (Path): The path to the image file (can be absolute or relative).

    Returns:
        numpy.ndarray: The image as a NumPy array, loaded using OpenCV.

    Raises:
        FileNotFoundError: If the image cannot be found at the specified path, even after attempting
                            to resolve the path.
    """
    # Suppress OpenCV warnings
    cv2.setLogLevel(1)

    # Attempt to read the image using OpenCV (cv2.imread)
    img = cv2.imread(str(image_path))

    # If the image is not found, try to resolve the path by making it relative
    if img is None:
        # Make the path relative and attempt to read the image again
        image_path = make_relative(image_path)
        img = cv2.imread(str(image_path))

    # Raise an exception if the image still cannot be found
    if img is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # Return the loaded image as a NumPy array
    return img
