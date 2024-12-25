from typing import List

from board.cell import Cell


class Line:
    """
    Represents a generic line of cells (either a row or a column).
    """

    def __init__(self, index, cells):
        """
        Initializes a Line object.

        Args:
            index (int): The index of the line (row or column number).
            cells (list of Cell): The list of Cell objects in the line.
        """
        self.index = index
        self.cells: List[Cell] = cells  # List of Cell objects

        # Update cell references to point to this line
        for cell in self.cells:
            self.assign_cell_reference(cell)

    def contains_cells(self, cells: List[Cell]) -> bool:
        """
        Checks if all the specified cells are contained in this line.

        Args:
            cells (List[Cell]): A list of Cell objects to check.

        Returns:
            bool: True if all the given cells are contained in this line, False otherwise.
        """
        return all(cell in self.cells for cell in cells)

    def get_empty_cells(self):
        """
        Returns a list of all empty cells in this area.

        Returns:
            List[Cell]: A list of cells that are empty.
        """
        return [cell for cell in self.cells if cell.state == "empty"]

    def get_empty_areas(self):
        """
        Returns the areas of the empty spaces in this line without duplicates.

        Returns:
            List[Area]: A list of unique Area objects that contain the empty cells.
        """
        # Gather areas from empty cells
        empty_cells = self.get_empty_cells()
        empty_areas = {cell.area_ref for cell in empty_cells if
                       cell.area_ref is not None}  # Use a set to avoid duplicates

        # Convert the set back to a list
        return list(empty_areas)

    def assign_cell_reference(self, cell):
        """
        Assigns this line as a reference to the cell (implemented in subclasses).

        Args:
            cell (Cell): A Cell object.
        """
        raise NotImplementedError("This method should be implemented in a subclass.")

    def get_line_except_cell(self, cell):
        """
        Returns all cells in the line except the specified cell.

        Args:
            cell (Cell): The cell to exclude.

        Returns:
            List[Cell]: A list of cells in the line except for the given cell.
        """
        cells_except_given = self.cells.copy()  # Make a shallow copy of the cells
        cells_except_given.remove(cell)  # Remove the specified cell
        return cells_except_given

    def intersect_cells(self, cells):
        """
        Returns a list of all cells from the given list that belong to this line.

        Args:
            cells (List[Cell]): A list of Cell objects to check for intersection.

        Returns:
            List[Cell]: A list of cells from the input that belong to this line.
        """
        return [cell for cell in cells if cell in self.cells]

    def check_empty_spot(self):
        """
        Checks if this line meets the conditions to place a crown.

        Returns:
            Cell: The cell to be crowned, or None if conditions are not met.
        """
        # Check if no cell has a crown and only one is empty
        crown_cells = [cell for cell in self.cells if cell.state == "crown"]
        empty_cells = [cell for cell in self.cells if cell.state == "empty"]

        if not crown_cells and len(empty_cells) == 1:
            return empty_cells[0]  # Return the single empty cell

        return None  # Conditions not met

    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index}, cells={len(self.cells)} cells)"


class Row(Line):
    """
    Represents a row of cells.
    """

    def assign_cell_reference(self, cell):
        """
        Assigns this Row as the row reference of the cell.

        Args:
            cell (Cell): A Cell object.
        """
        cell.row_ref = self


class Column(Line):
    """
    Represents a column of cells.
    """

    def assign_cell_reference(self, cell):
        """
        Assigns this Column as the column reference of the cell.

        Args:
            cell (Cell): A Cell object.
        """
        cell.column_ref = self
