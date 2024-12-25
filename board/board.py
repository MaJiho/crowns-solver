import math


def _is_perfect_square(n):
    """
    Checks if a number is a perfect square.

    Args:
        n (int): The number to check.

    Returns:
        bool: True if n is a perfect square, False otherwise.
    """
    return int(math.sqrt(n)) ** 2 == n


def _create_cell_matrix(cells):
    """
    Converts a list of cells into a 2D matrix of cells, assuming the number of cells is a perfect square.

    Args:
        cells (list): A flat list of Cell objects.

    Returns:
        list: A 2D matrix (list of lists) of Cell objects.
    """
    size = int(len(cells) ** 0.5)  # Assuming the grid is a perfect square
    cell_matrix = [cells[i * size:(i + 1) * size] for i in range(size)]
    return cell_matrix


class Board:
    def __init__(self, top_left, cells):
        """
        Initializes the game board with its position on the screen and the grid of cells.

        Args:
            top_left (tuple): The (x, y) coordinates of the top-left corner of the board on the screen.
            cells (list): A list of Cell objects representing the grid's cells.

        Raises:
            ValueError: If the number of cells is not a perfect square.
        """
        if not _is_perfect_square(len(cells)):
            raise ValueError("The number of cells must form a perfect square grid.")

        self.top_left = top_left
        self.cells = _create_cell_matrix(cells)

    def save_state(self):
        """
        Returns a matrix of strings representing the current state of the board.
        Each cell's state is represented as a string.
        """
        return [[cell.state for cell in row] for row in self.cells]

    def load_state(self, state_matrix):
        """
        Sets the states of all cells on the board using a given matrix of states.

        Args:
            state_matrix (list of list of str): A matrix where each element is a string
                                                representing the state of a cell.
        """
        for i, row in enumerate(state_matrix):
            for j, state in enumerate(row):
                self.cells[i][j].state = state

    def get_cell_at(self, row, col):
        """
        Retrieves the cell at the specified (row, col) position.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            Cell: The Cell object at the given position.

        Raises:
            IndexError: If row or col are out of bounds.
        """
        if not (0 <= row < len(self.cells) and 0 <= col < len(self.cells[0])):
            raise IndexError("Row or column index out of bounds.")
        return self.cells[row][col]

    def get_position_coordinates(self, row, col):
        """
        Returns the screen coordinates (center) of the cell at the given row and column.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            tuple: The (x, y) coordinates of the center of the cell.
        """
        if not (0 <= row < len(self.cells) and 0 <= col < len(self.cells[0])):
            raise IndexError("Row or column index out of bounds.")

        # Get the top-left corner of the board
        board_x, board_y = self.top_left

        # Get the cell object at the specified row and column
        cell = self.get_cell_at(row, col)

        # Calculate the center coordinates of the cell in the screen
        cell_x = board_x + cell.x
        cell_y = board_y + cell.y

        return cell_x, cell_y

    def get_cell_coordinates(self, cell):
        """
        Returns the screen coordinates (center) of the given cell.

        Args:
            cell (Cell): The Cell object whose coordinates are to be retrieved.

        Returns:
            tuple: The (x, y) coordinates of the center of the cell.
        """
        # Get the position of the cell in the board (row, col)
        row, col = self.get_cell_position(cell)

        return self.get_position_coordinates(row, col)

    def get_cell_position(self, cell):
        """
        Returns the (row, col) position of the given cell within the board.

        Args:
            cell (Cell): The cell whose position is to be retrieved.

        Returns:
            tuple: The (row, col) position of the given cell within the board.

        Raises:
            ValueError: If the cell is not found on the board.
        """
        for row_index, row in enumerate(self.cells):
            for col_index, board_cell in enumerate(row):
                if board_cell == cell:
                    return row_index, col_index

        raise ValueError("Cell not found on the board.")

    def get_surrounding_cells(self, cell):
        """
        Returns the surrounding cells of the given cell. It checks the 8 surrounding cells in a 3x3 grid
        around the specified cell, excluding the cell itself. If the cell is on the edge or a corner,
        it will return fewer cells.

        Args:
            cell (Cell): The cell whose surrounding cells are to be retrieved.

        Returns:
            list: A list of surrounding Cell objects (up to 8 cells).
        """
        # Get the row and column indices of the provided cell
        row, col = self.get_cell_position(cell)

        surrounding_cells = []

        # Iterate over the range of row-1 to row+1 and col-1 to col+1 to check surrounding cells
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                # Add all cells in the surrounding grid to the list
                if 0 <= i < len(self.cells) and 0 <= j < len(self.cells[0]):
                    surrounding_cells.append(self.cells[i][j])

        # Remove the given cell from the surrounding cells list
        surrounding_cells.remove(cell)

        return surrounding_cells

    def get_position(self):
        """
        Returns the top-left corner position of the board on the screen.

        Returns:
            tuple: The (x, y) coordinates of the board's top-left corner.
        """
        return self.top_left

    def get_dimensions(self):
        """
        Returns the dimensions of the board as (rows, cols).

        Returns:
            tuple: (rows, cols)
        """
        return len(self.cells), len(self.cells[0])
