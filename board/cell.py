import numpy as np


class Cell:
    def __init__(self, x, y, size):
        """
        Initializes a Cell object.

        Args:
            x (int): The x-coordinate of the cell's center.
            y (int): The y-coordinate of the cell's center.
            size (int): The size of the square cell (both width and height).
        """
        self.x = x
        self.y = y
        self.size = size
        self.color = None  # Optional: Store cell color
        self.state = "empty"  # "empty", "crown", or "cross"

        self.row_ref = None  # Reference to the Row object
        self.column_ref = None  # Reference to the Column object
        self.area_ref = None  # Reference to the Area object

    @classmethod
    def from_corners(cls, top_left, bottom_right):
        """
        Factory method to create a Cell object using corner coordinates.

        Args:
            top_left (tuple): (x, y) coordinates of the top-left corner.
            bottom_right (tuple): (x, y) coordinates of the bottom-right corner.

        Returns:
            Cell: A new Cell object with calculated center and size.
        """
        # Calculate the center and size from corners
        x_center = (top_left[0] + bottom_right[0]) // 2
        y_center = (top_left[1] + bottom_right[1]) // 2
        size = bottom_right[0] - top_left[0]  # Assuming square cells
        return cls(x_center, y_center, size)

    @classmethod
    def from_top_left(cls, top_left, size):
        """
        Factory method to create a Cell object using the top-left corner and size.

        Args:
            top_left (tuple): (x, y) coordinates of the top-left corner.
            size (int): The size of the square cell (both width and height).

        Returns:
            Cell: A new Cell object with calculated center.
        """
        x_center = top_left[0] + size // 2
        y_center = top_left[1] + size // 2
        return cls(x_center, y_center, size)

    def is_empty(self):
        """
        Checks if the cell is in an empty state.

        Returns:
            bool: True if the cell state is "empty", False otherwise.
        """
        return self.state == "empty"

    def is_cross(self):
        """
        Checks if the cell is in a cross state.

        Returns:
            bool: True if the cell state is "cross", False otherwise.
        """
        return self.state == "cross"

    def is_crown(self):
        """
        Checks if the cell is in a crown state.

        Returns:
            bool: True if the cell state is "crown", False otherwise.
        """
        return self.state == "crown"

    def set_color(self, color):
        """
        Sets the color of the cell.

        Args:
            color (numpy.ndarray or tuple): The color in BGR format.

        Converts the color to a tuple to ensure it is hashable.
        """
        if isinstance(color, np.ndarray):
            self.color = tuple(color)  # Convert numpy array to a tuple
        else:
            self.color = color

    def set_state(self, new_state):
        """
        Sets the state of the cell and triggers listeners in its references.

        Args:
            new_state (str): The new state ("empty", "cross", or "crown").
        """
        if new_state not in ["empty", "cross", "crown"]:
            raise ValueError("Invalid state. Allowed values: 'empty', 'cross', 'crown'.")

        self.state = new_state

    def toggle_state(self):
        """
        Toggles the state of the cell in the order: empty -> cross -> crown -> empty.
        """
        if self.is_empty():
            self.set_state("cross")
        elif self.is_cross():
            self.set_state("crown")
        elif self.is_crown():
            self.set_state("empty")

    def get_coordinates(self):
        """
        Returns the coordinates of the cell center.

        Returns:
            tuple: The (x, y) coordinates of the cell center.
        """
        return self.x, self.y

    def get_bounds(self):
        """
        Calculates the bounding box of the cell.

        Returns:
            tuple: The coordinates of the top-left and bottom-right corners.
        """
        half_size = self.size // 2
        top_left = (self.x - half_size, self.y - half_size)
        bottom_right = (self.x + half_size, self.y + half_size)
        return top_left, bottom_right

    def __repr__(self):
        return f"Cell({self.column_ref.get_position(self)},{self.row_ref.get_position(self)})"
