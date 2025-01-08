import tkinter as tk
from app import process_game_board
from settings.settings import load_settings
from ui_components import create_button


class UIManager:
    def __init__(self):
        """
        Initialize the UIManager and set up the main window.
        """
        self.status_label = None
        self.root = tk.Tk()
        self.root.title("Crown Solver")
        self.root.geometry("300x200")

        # Load settings at startup
        load_settings()

        # Add components to the UI
        self.setup_ui()

    def setup_ui(self):
        """
        Set up UI components in the main window.
        """
        # Title label
        title_label = tk.Label(self.root, text="Crown Solver", font=("Helvetica", 16))
        title_label.pack(pady=20)

        # Solve button
        solve_button = create_button(self.root, "Start Process", self.start_process)
        solve_button.pack(pady=10)

        # Exit button
        exit_button = create_button(self.root, "Exit", self.exit_application)
        exit_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="green", font=("Helvetica", 10))
        self.status_label.pack(pady=10)

    def start_process(self):
        """
        Trigger the solving process and update the status label.
        """
        success = process_game_board()
        if success:
            self.status_label.config(text="Process completed successfully!", fg="green")
        else:
            self.status_label.config(text="Process failed.", fg="red")

    def exit_application(self):
        """
        Exit the application.
        """
        self.root.quit()

    def run(self):
        """
        Start the main UI loop.
        """
        self.root.mainloop()
