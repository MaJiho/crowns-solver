import json

# Global settings dictionary
settings = {}


def load_settings(file_path="settings.json"):
    """
    Load settings from a JSON file and store them in the global settings variable.
    """
    global settings
    try:
        with open(file_path, "r") as file:
            settings = json.load(file)
    except FileNotFoundError:
        print(f"Settings file '{file_path}' not found. Using default settings.")
        settings = {}
    except json.JSONDecodeError:
        print(f"Failed to parse '{file_path}'. Ensure it is valid JSON.")
        settings = {}


def get_setting(key, default=None):
    """
    Retrieve a setting by key with an optional default value.
    """
    return settings.get(key, default)
