import unittest

from board.board import Board
from board.cell import Cell
from board.line import Row, Column
from utils.debug import load_board_state
from settings.settings import load_settings
from solver.solver import Solver, get_common_cells


class TestSolver(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment with a mock board and cells.
        """
        # Create mock cells
        self.cell1 = Cell(state="empty")
        self.cell2 = Cell(state="empty")
        self.cell3 = Cell(state="crossed")
        self.cell4 = Cell(state="empty")

        # Create rows and columns
        self.row1 = Row(index=1, cells=[self.cell1, self.cell2, self.cell3])
        self.row2 = Row(index=2, cells=[self.cell4])
        self.col1 = Column(index=1, cells=[self.cell1, self.cell4])
        self.col2 = Column(index=2, cells=[self.cell2])
        self.col3 = Column(index=3, cells=[self.cell3])

        # Assign rows and columns to cells
        for cell in self.row1.cells:
            cell.row_ref = self.row1
        for cell in self.row2.cells:
            cell.row_ref = self.row2
        for cell in self.col1.cells:
            cell.column_ref = self.col1
        for cell in self.col2.cells:
            cell.column_ref = self.col2
        for cell in self.col3.cells:
            cell.column_ref = self.col3

        # Solver instance
        self.solver = Solver()

    def test_set_all_cells_crossed(self):
        """
        Test the `set_all_cells_crossed` method with valid input.
        """
        cells = [self.cell1, self.cell2, self.cell3, self.cell4]

        # Call the method (no implementation yet, so expect no exceptions)
        try:
            self.solver.cross_cells_path(cells)
        except Exception as e:
            self.fail(f"set_all_cells_crossed raised an unexpected exception: {e}")

    def test_invalid_cells(self):
        """
        Test that `set_all_cells_crossed` raises a TypeError for invalid input.
        """
        invalid_cells = [self.cell1, "not a cell", 123]

        with self.assertRaises(TypeError):
            self.solver.cross_cells_path(invalid_cells)

    def test_filter_empty_cells(self):
        """
        Test that only empty cells are considered.
        """
        cells = [self.cell1, self.cell2, self.cell3, self.cell4]
        self.solver.cross_cells_path(cells)

        # Verify that crossed cells are ignored (mock functionality for now)
        filtered_cells = [cell for cell in cells if cell.is_empty()]
        self.assertEqual(len(filtered_cells), 3)


class TestGetCommonCells(unittest.TestCase):
    class Cell:
        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            return isinstance(other, self.__class__) and self.value == other.value

        def __hash__(self):
            return hash(self.value)

        def __repr__(self):
            return f"Cell({self.value})"

    def test_common_cells_found(self):
        # Test where there are common cells in all sets
        cell1 = self.Cell(1)
        cell2 = self.Cell(2)
        cell3 = self.Cell(3)

        set1 = {cell1, cell2, cell3}
        set2 = {cell2, cell3}
        set3 = {cell2, cell3, cell1}

        sets_of_cells = [set1, set2, set3]

        common_cells = get_common_cells(sets_of_cells)

        self.assertEqual(common_cells, [cell2, cell3])

    def test_no_common_cells(self):
        # Test where there are no common cells between the sets
        cell1 = self.Cell(1)
        cell2 = self.Cell(2)
        cell3 = self.Cell(3)

        set1 = {cell1}
        set2 = {cell2}
        set3 = {cell3}

        sets_of_cells = [set1, set2, set3]

        common_cells = get_common_cells(sets_of_cells)

        self.assertEqual(common_cells, [])

    def test_empty_input(self):
        # Test for empty input (empty list of sets)
        sets_of_cells = []

        common_cells = get_common_cells(sets_of_cells)

        self.assertEqual(common_cells, [])

    def test_single_set(self):
        # Test when there is only one set
        cell1 = self.Cell(1)
        cell2 = self.Cell(2)

        set1 = {cell1, cell2}

        sets_of_cells = [set1]

        common_cells = get_common_cells(sets_of_cells)

        self.assertEqual(common_cells, [cell1, cell2])

    def test_empty_cells_in_sets(self):
        # Test where some sets contain empty cells
        cell1 = self.Cell(1)
        cell2 = self.Cell(2)

        set1 = {cell1, cell2}
        set2 = {cell2}
        set3 = {cell1, cell2}

        sets_of_cells = [set1, set2, set3]

        common_cells = get_common_cells(sets_of_cells)

        self.assertEqual(common_cells, [cell2])


class TestSolverRules(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by loading the board state.
        This method is executed before each test.
        """
        load_settings("../settings/settings.json")
        self.board: Board = load_board_state()
        if not self.board:
            self.fail("Failed to load board state for testing.")

    def test_rule_five(self):
        """
        Test for rule_five to ensure it behaves as expected.
        """
        solver = Solver(self.board)
        solver.rule_five()


if __name__ == "__main__":
    unittest.main()
