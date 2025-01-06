import json

# Global settings dictionary
settings = {}


def check_for_quick_clicker():
    def set_setting(setting, value):
        settings[setting] = value

    if get_setting("quick_clicker"):
        set_setting("click_cross_enabled", False)
        set_setting("click_crown_duration", 0.01)
        set_setting("sleep_time", 0.0)


def load_settings(file_path="settings.json"):
    """
    Load settings from a JSON file and store them in the global settings variable.
    """
    global settings
    try:
        with open(file_path, "r") as file:
            settings = json.load(file)
            check_for_quick_clicker()
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
