from typing import List

from board.cell import Cell


class Area:
    def __init__(self, color):
        """
        Initializes an Area object.

        Args:
            color (tuple): The color representing this area.
        """
        self.color = color
        self.cells: List[Cell] = []  # List of Cell objects in this area

    def add_cell(self, cell):
        """
        Adds a cell to this area and sets a reference in the cell.

        Args:
            cell (Cell): The cell to be added.
        """
        self.cells.append(cell)
        cell.area_ref = self

    def on_cell_state_change(self):
        """
        Listener method called when a cell in this area changes state.
        """
        # Example logic: check if only one empty cell remains
        empty_cells = [cell for cell in self.cells if cell.state == "empty"]
        if len(empty_cells) == 1:
            empty_cells[0].set_state("crown")  # Set the last empty cell as the crown

    def check_empty_spot(self):
        """
        Checks if this area has no crowns and only 1 empty spot

        Returns:
            Cell: The cell to be crowned, or None if conditions are not met.
        """
        # Check if no cell has a crown and only one is empty
        crown_cells = [cell for cell in self.cells if cell.state == "crown"]
        empty_cells = self.get_empty_cells()

        if not crown_cells and len(empty_cells) == 1:
            return empty_cells[0]  # Return the single empty cell

        return None  # Conditions not met

    def get_empty_cells(self):
        """
        Returns a list of all empty cells in this area.

        Returns:
            List[Cell]: A list of cells that are empty.
        """
        return [cell for cell in self.cells if cell.state == "empty"]

    def get_columns_of_empty_cells(self):
        """
        Returns a list of column references for all empty cells in this area.

        Returns:
            List[Column]: A list of unique column references.
        """
        empty_cells = self.get_empty_cells()
        columns = {cell.column_ref for cell in empty_cells if cell.column_ref}
        return list(columns)

    def get_rows_of_empty_cells(self):
        """
        Returns a list of row references for all empty cells in this area.

        Returns:
            List[Row]: A list of unique row references.
        """
        empty_cells = self.get_empty_cells()
        rows = {cell.row_ref for cell in empty_cells if cell.row_ref}
        return list(rows)

    def __repr__(self):
        return f"Area(color={self.color}, cells={len(self.cells)} cells)"
