from utils.file import resolve_path, load_json

# Global settings dictionary
settings = {}


def check_for_quick_clicker():
    """
    Modify settings in the 'app_settings' section based on the value of 'quick_clicker'.
    """
    if get_setting("app_settings.quick_clicker"):
        set_setting("app_settings", "click_cross_enabled", False)
        set_setting("app_settings", "click_crown_duration", 0.01)
        set_setting("app_settings", "sleep_time", 0.0)


def set_setting(section, key, value):
    """
    Set a specific setting value in a given section.
    """
    if section in settings:
        settings[section][key] = value


def load_settings(file_path="settings/settings.json"):
    """
    Load settings from a JSON file and store them in the global settings variable.
    """
    global settings
    try:
        # Resolve the settings file path
        settings_file_path = resolve_path(file_path)

        # Load settings using the file utility
        raw_settings = load_json(settings_file_path)
        if raw_settings is None:
            print(f"Failed to load settings from '{file_path}'. Using default settings.")
            settings = {}
            return

        # Resolve all file paths in the 'paths' section
        if "paths" in raw_settings:
            assets_base_path = raw_settings["paths"].get("assets", "")
            resolved_paths = {
                key: assets_base_path + value if key != "assets" else value
                for key, value in raw_settings["paths"].items()
            }
            raw_settings["paths"] = resolved_paths

        # Update global settings
        settings.update(raw_settings)

        # Check for quick clicker settings
        check_for_quick_clicker()
    except Exception as e:
        print(f"Error loading settings: {e}")
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
