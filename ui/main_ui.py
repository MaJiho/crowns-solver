from pathlib import Path
from ui_manager import UIManager
from utils import file

# Base directory for resolving paths
file.STARTING_PATH = Path(__file__).resolve()

if __name__ == "__main__":
    ui = UIManager()
    ui.run()


