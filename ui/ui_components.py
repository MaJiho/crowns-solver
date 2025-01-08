import tkinter as tk


def create_button(parent, text, command):
    """
    Create a button with the given text and command, and attach it to the parent widget.
    """
    button = tk.Button(parent, text=text, command=command, padx=10, pady=5)
    return button
