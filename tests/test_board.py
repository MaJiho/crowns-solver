import unittest

from board.board import Board
from board.cell import Cell


class TestBoard(unittest.TestCase):
    def setUp(self):
        # Set up a simple 3x3 board with dummy cells
        self.cells = [Cell(x * 10 + 5, y * 10 + 5, 10) for x in range(3) for y in range(3)]
        self.board = Board((0, 0), self.cells)

    def test_board_initialization(self):
        # Test board initialization and perfect square check
        self.assertEqual(self.board.get_dimensions(), (3, 3))
        self.assertEqual(self.board.get_position(), (0, 0))

    def test_get_cell_at(self):
        # Test getting a specific cell at (1, 1)
        cell = self.board.get_cell_at(1, 1)
        self.assertEqual(cell.get_coordinates(), (15, 15))  # Expected coordinates for center of (1, 1)

        # Test invalid index
        with self.assertRaises(IndexError):
            self.board.get_cell_at(3, 3)  # Out of bounds

    def test_get_cell_coordinates(self):
        # Test the coordinates of a cell at (1, 1)
        coords = self.board.get_position_coordinates(1, 1)
        self.assertEqual(coords, (15, 15))  # Coordinates of the center

        # Test invalid index
        with self.assertRaises(IndexError):
            self.board.get_position_coordinates(3, 3)  # Out of bounds

    def test_get_cell_position(self):
        # Test getting the position of a specific cell
        cell = self.board.get_cell_at(1, 1)
        position = self.board.get_cell_position(cell)
        self.assertEqual(position, (1, 1))

        # Test if a non-existent cell raises an error
        non_existent_cell = Cell(100, 100, 10)  # This cell isn't on the board
        with self.assertRaises(ValueError):
            self.board.get_cell_position(non_existent_cell)

    def test_get_surrounding_cells(self):
        # Test surrounding cells for a middle cell (1, 1)
        cell = self.board.get_cell_at(1, 1)
        surrounding_cells = self.board.get_surrounding_cells(cell)
        self.assertEqual(len(surrounding_cells), 8)  # 8 surrounding cells should be found

        # Test surrounding cells for a corner cell (0, 0)
        corner_cell = self.board.get_cell_at(0, 0)
        corner_surrounding_cells = self.board.get_surrounding_cells(corner_cell)
        self.assertEqual(len(corner_surrounding_cells), 3)  # Should be 3 surrounding cells in the corner

    def test_invalid_cell_count(self):
        # Test the case where the number of cells isn't a perfect square
        invalid_cells = [Cell(x * 10 + 5, y * 10 + 5, 10) for x in range(2) for y in range(3)]  # 6 cells, not a perfect square
        with self.assertRaises(ValueError):
            Board((0, 0), invalid_cells)

    def test_get_dimensions(self):
        # Test that dimensions return the correct number of rows and columns
        self.assertEqual(self.board.get_dimensions(), (3, 3))

    def test_get_position(self):
        # Test that get_position returns the correct top-left corner coordinates
        self.assertEqual(self.board.get_position(), (0, 0))


if __name__ == "__main__":
    unittest.main()
