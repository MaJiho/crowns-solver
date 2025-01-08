import json
from pathlib import Path

# Global settings dictionary
settings = {}

# Base directory for resolving paths
BASE_DIR = Path(__file__).resolve().parent.parent


def check_for_quick_clicker():
    """
    Modify settings in the 'app_settings' section based on the value of 'quick_clicker'.
    """

    def set_setting(section, key, value):
        settings[section][key] = value

    if get_setting("app_settings.quick_clicker"):
        set_setting("app_settings", "click_cross_enabled", False)
        set_setting("app_settings", "click_crown_duration", 0.01)
        set_setting("app_settings", "sleep_time", 0.0)


def resolve_path(relative_path):
    """
    Resolve a path relative to the base directory.
    """
    return BASE_DIR / relative_path


def make_relative(absolute_path):
    """
    Convert an absolute path to a path relative to the base directory.
    """
    return absolute_path.relative_to(BASE_DIR)


def load_settings(file_path="settings/settings.json"):
    """
    Load settings from a JSON file and store them in the global settings variable.
    """
    global settings
    try:
        # Resolve the settings file path
        settings_file_path = resolve_path(file_path)

        with open(settings_file_path, "r") as file:
            raw_settings = json.load(file)

        # Get the base assets path from the settings
        assets_base_path = raw_settings["paths"]["assets"]

        # Create a new dictionary for resolved paths
        resolved_paths = {}

        # Loop through each key-value pair in the 'paths' section
        for key, value in raw_settings["paths"].items():
            if key == "assets":
                # Skip the 'assets' key as it's the base path
                continue
            # Resolve the full path for the current file
            resolved_paths[key] = assets_base_path + value

        # Replace the 'paths' section with the resolved paths
        raw_settings["paths"] = resolved_paths

        settings.update(raw_settings)
        check_for_quick_clicker()
    except FileNotFoundError:
        print(f"Settings file '{file_path}' not found. Using default settings.")
        settings = {}
    except json.JSONDecodeError:
        print(f"Failed to parse '{file_path}'. Ensure it is valid JSON.")
        settings = {}


def get_setting(key, default=None):
    """
    Retrieve a nested setting by a dot-separated key with an optional default value.
    """
    keys = key.split(".")
    value = settings
    try:
        for k in keys:
            value = value[k]
        return value
    except KeyError:
        return default
