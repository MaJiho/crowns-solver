import math
import pickle
import time
from collections import defaultdict
from typing import Dict, List, Any

from pynput import keyboard

from board.area import Area
from board.cell import Cell
from board.line import Row, Column, Line
from settings.settings import get_setting
from utils.input import click_at, click_and_drag
from utils.logic import find_matching_entries


def get_common_cells(sets_of_cells: list[set[Cell]]) -> list[Cell]:
    """
    Given a list of sets of cells, return a list of cells that are present in every set.

    Args:
        sets_of_cells (list of set): A list where each element is a set of cells.

    Returns:
        list: A list of cells that are present in every set.
    """
    if not sets_of_cells:
        return []  # Return an empty list if there are no sets

    # Start with the first set and intersect with the rest
    common_cells = sets_of_cells[0]

    # Perform intersection with all subsequent sets
    for cell_set in sets_of_cells[1:]:
        common_cells &= cell_set

    return list(common_cells)


def save_board_state(board, filename=None):
    """
    Saves the current state of the board to a file.

    Args:
        board: The board object to save.
        filename (str): The name of the file to save the board to.
    """
    if filename is None:
        filename = get_setting("paths.board_obj")
    try:
        with open(filename, "wb") as file:
            pickle.dump(board, file)
        print(f"Board state saved to {filename}")
    except Exception as e:
        print(f"Error saving board state: {e}")


class Solver:
    def __init__(self, board):
        """
        Initializes the Solver object with the given game board.

        Args:
            board (Board): The Board object representing the game grid.
        """
        self.stop_flag = False  # Flag to stop the solve method
        self.listener = None  # Reference to the listener object

        self.board = board
        self.areas: Dict[Any, Area] = {}  # Dictionary to store areas by color (str -> Area)
        self.rows: List[Row] = []  # List to store Row objects
        self.columns: List[Column] = []  # List to store Column objects
        self.crowns = 0
        self.guess_flag = False

        self.click_cross_enabled = get_setting("app_settings.click_cross_enabled")
        self.click_crown_enabled = get_setting("app_settings.click_crown_enabled")
        self.click_enabled = get_setting("app_settings.click_enabled")
        self.sleep_time = get_setting("app_settings.sleep_time")

        self.create_areas()
        self.create_lines()

    def start_listener(self):
        """
        Starts a listener thread to check for the Esc key press.
        """

        def on_press(key):
            try:
                if key == keyboard.Key.esc:
                    self.stop_flag = True
                    print("Stopping process...")
                    if self.listener:  # Stop the listener explicitly
                        self.listener.stop()
            except Exception as e:
                print(f"Error: {e}")

        if not self.listener:
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.start()

    def create_areas(self):
        """
        Creates areas on the board based on cell colors.

        Each unique color corresponds to an area, and all cells of the same color belong to the same area.
        """
        rows, cols = self.board.get_dimensions()

        for row in range(rows):
            for col in range(cols):
                cell = self.board.get_cell_at(row, col)
                cell_color = cell.color

                # Skip cells with no color
                if cell_color is None:
                    continue

                # Create a new Area object if not already present
                if cell_color not in self.areas:
                    self.areas[cell_color] = Area(color=cell_color)

                # Add the cell to the appropriate area
                self.areas[cell_color].add_cell(cell)

        print(f"Areas created: {len(self.areas)} areas detected.")

    def create_lines(self):
        """
        Creates Row and Column objects for the board and assigns them to cells.
        """
        rows, cols = self.board.get_dimensions()

        # Create Row objects
        for row_index in range(rows):
            cells_in_row = [self.board.get_cell_at(row_index, col) for col in range(cols)]
            row = Row(index=row_index, cells=cells_in_row)
            self.rows.append(row)

        # Create Column objects
        for col_index in range(cols):
            cells_in_column = [self.board.get_cell_at(row, col_index) for row in range(rows)]
            column = Column(index=col_index, cells=cells_in_column)
            self.columns.append(column)

        print(f"Lines created: {len(self.rows)} rows and {len(self.columns)} columns.")

    def set_cell_crown(self, cell):
        """
        Toggles the cell's state until it is set to 'crown'.
        """
        self.crowns = self.crowns + 1
        click = get_setting("app_settings.click_crown_enabled")
        while not cell.is_crown():
            duration = get_setting("app_settings.click_crown_duration")
            self.toggle_cell(cell, click, duration)

    def set_cell_cross(self, cell, click=None):
        """
        Toggles the cell's state until it is set to 'cross'.
        """
        if click is None:
            click = get_setting("app_settings.click_cross_enabled")
        while not cell.is_cross():
            duration = get_setting("app_settings.click_cross_duration")
            self.toggle_cell(cell, click, duration)

    def toggle_cell(self, cell, click=True, duration=None):
        """
            Toggles the cell's state and clicks it on screen if click is true.
        """
        x, y = self.board.get_cell_coordinates(cell)
        cell.toggle_state()

        # Click the screen
        if click and self.click_enabled and not self.stop_flag:
            if duration is None:
                duration = get_setting("app_settings.click_cross_duration")
            click_at((x, y), duration)

    def click_and_drag_cells(self, cells: list[Cell]):
        # Change state of cells to crossed without clicking
        for cell in cells:
            self.toggle_cell(cell, click=False)

        start = self.board.get_cell_coordinates(cells[0])
        end = self.board.get_cell_coordinates(cells[-1])
        click_and_drag(start, end)

    def cross_cells(self, cells: list[Cell]):
        for cell in cells:
            self.set_cell_cross(cell)

    def cross_cells_path(self, cells_to_cross: List[Cell]):
        """
        Calculate the optimal path for clicking all cells.

        Args:
            cells_to_cross (List[Cell]): List of `Cell` objects with `x` and `y` coordinates.

        Raises:
            TypeError: If any element in `cells` is not a `Cell` object.
        """
        if not all(isinstance(cell, Cell) for cell in cells_to_cross):
            raise TypeError("All elements in the 'cells' list must be instances of the 'Cell' class.")

        # Filter any cell that isn't empty
        cells_to_cross = [cell for cell in cells_to_cross if cell.is_empty()]

        # If clicking is not enable, we only change states
        click_cross_enabled = get_setting("app_settings.click_cross_enabled")
        click_enabled = get_setting("app_settings.click_enabled")
        if not (click_enabled and click_cross_enabled):
            for cell in cells_to_cross:
                self.set_cell_cross(cell)
            return

        while cells_to_cross:
            # Organize cells in lines (Rows and Columns)
            lines = defaultdict(int)  # This will store the counts of each line (Row or Column)

            for cell in cells_to_cross:
                lines[cell.row_ref] += 1  # Count the row
                lines[cell.column_ref] += 1  # Count the column

            # Order lines from biggest to smallest
            lines = sorted(lines.items(), key=lambda item: item[1], reverse=True)

            # Split lines into segments
            segments = []

            for line, _ in lines:
                cells_in_line_to_cross = line.intersect_cells(cells_to_cross)
                line_segments = line.make_line_segments(cells_in_line_to_cross)
                segments.extend(line_segments)

            # Order segments
            segments: list[list[Cell]] = sorted(segments, key=len, reverse=True)

            # Cross largest segment
            largest_segment = segments.pop(0)
            if len(largest_segment) > 1:  # Click and drag
                self.click_and_drag_cells(largest_segment)
            elif len(largest_segment) == 1:  # Click
                self.set_cell_cross(largest_segment[0])

            # Remove used cells from original list
            for cell in largest_segment:
                cells_to_cross.remove(cell)

    def crown_cell(self, cell):
        """
        Places a crown on the given cell.

        Args:
            cell (Cell): The cell where the crown should be placed.
        """
        # Place a crown on the given cell
        self.set_cell_crown(cell)

    def get_empty_spaces(self):
        return [cell for area in self.areas.values() for cell in area.get_empty_cells()]

    def get_crosses_from_crown(self, crown):
        col: Column = crown.column_ref
        row: Row = crown.row_ref
        area: Area = crown.area_ref
        return list(set(
            col.get_line_except_cell(crown) +
            row.get_line_except_cell(crown) +
            area.get_area_except_cell(crown) +
            self.board.get_surrounding_cells(crown)
        ))

    def rule_one(self):
        """
        Checks if an area or a line has a single empty spot, which should be considered a crown.

        This method inspects each area and line on the board. If an area or a line contains exactly
        one empty spot, that spot is designated as a crown and a crown is placed there.

        Returns:
            bool: True if a crown was placed according to this rule, False otherwise.
        """
        crown: Cell | None = None
        crosses: list[Cell] = []

        # Check for crowns in areas
        for area in self.areas.values():
            crown = area.check_empty_spot()
            if crown:
                break

        # Check for crowns in lines (rows and columns)
        if not crown:
            for line in self.rows + self.columns:
                crown = line.check_empty_spot()
                if crown:
                    break

        if crown:
            # Gather all cells to be crossed from this crown
            crosses += self.get_crosses_from_crown(crown)

        return crown, crosses

    def rule_two(self):
        """
        Checks for empty cells of an area that occupy 1 line (row or column).
        If all empty cells of an area are in the same row or column, perform the action (e.g., place a crown).
        """
        crown: Cell | None = None
        crosses: list[Cell] = []

        for area in self.areas.values():
            # Get all empty cells in the area
            area_empty_cells = area.get_empty_cells()

            # If there are no empty cells or more than one, skip this area
            if len(area_empty_cells) < 2:
                continue

            # Get rows and columns occupied by the area
            rows = set(cell.row_ref for cell in area_empty_cells)
            columns = set(cell.column_ref for cell in area_empty_cells)

            line = None

            # Check if all empty cells are in the same row
            if len(rows) == 1:
                # All empty cells are in the same row, apply the rule
                line = next(iter(rows))  # Get the row reference

            # Check if all empty cells are in the same column
            elif len(columns) == 1:
                # All empty cells are in the same column, perform the action
                line = next(iter(columns))  # Get the column reference

            if line:
                # Get all cells in the row
                line_cells = line.cells
                # Keep empty cells that don't belong to the area
                crosses = [cell for cell in line_cells if
                           cell not in area_empty_cells and cell.is_empty()]

        return crown, crosses

    def rule_three(self):
        """
        Checks for rows/columns with only one possible area.
        If all empty cells in a row or column belong to the same area,
        the remaining empty cells of that area (excluding the row/column cells) get crossed.
        """
        crown: Cell | None = None
        crosses: list[Cell] = []

        # Step 1: Check all rows and columns
        for line in self.rows + self.columns:  # Combine rows and columns into one iterable
            line_empty_cells = line.get_empty_cells()

            if not line_empty_cells:  # Skip if no empty cells in this line
                continue

            # Step 2: Check if all empty cells belong to the same area
            areas_in_line = set(cell.area_ref for cell in line_empty_cells)

            if len(areas_in_line) == 1:  # Only one area in this line
                area = next(iter(areas_in_line))  # Get the single area reference

                # Step 3: Get all empty cells in the area
                area_empty_cells = area.get_empty_cells()

                # Step 4: Remove the line's empty cells from the area's empty cells
                crosses = [cell for cell in area_empty_cells if
                           cell not in line_empty_cells]
                break

        return crown, crosses

    def rule_four(self):
        """
        Checks for impossible spaces in areas.
        For each area, identifies surrounding cells of all empty spaces,
        and if a cell is common to all surrounding spaces, it gets crossed.
        """
        crown: Cell | None = None
        crosses: list[Cell] = []

        # Step 1: Sort areas by the number of empty spaces (ascending)
        areas_by_empty_cells = sorted(self.areas.values(), key=lambda a: len(a.get_empty_cells()))

        # Step 2: Iterate through each area
        for area in areas_by_empty_cells:
            empty_cells = area.get_empty_cells()

            # Skip areas with no empty cells or only one empty cell
            if len(empty_cells) < 2:
                continue

            # Step 3: Collect surrounding cells AND lines for all empty cells
            surrounding_cells_list = []
            for cell in empty_cells:
                surrounding_cells = set(self.board.get_surrounding_cells(cell))
                row_cells = set(cell.row_ref.get_line_except_cell(cell))
                column_cells = set(cell.column_ref.get_line_except_cell(cell))
                surrounding_cells_list.append(
                    surrounding_cells | row_cells | column_cells)

            # Step 4: Intersect all surrounding cells
            common_cells = get_common_cells(surrounding_cells_list)

            # Step 5: Keep only the empty cells
            common_cells = [cell for cell in common_cells if cell.is_empty()]

            # Step 6: Cross the common cells that are empty
            crosses.extend(common_cells)

        return crown, crosses

    def rule_five(self):
        """
         Implements Rule Six for solving the puzzle. This rule identifies cases where multiple lines (rows or columns)
         share only a few possible areas, ensuring that the crowns within those areas must occupy those lines.
         Consequently, any other lines that overlap with those areas are crossed out to eliminate ambiguity.

         Steps:
         1. For each possible number of matching areas (from `min_value` to `max_value`):
             a. Find groups of lines with exactly `i` matching areas.
             b. Verify that the matched areas are exactly `i` in number.
             c. Determine all lines connected to those areas.
             d. Exclude the matching lines from the total connected lines.
             e. Cross out cells in the excluded lines that overlap with the matched areas.
         2. Repeat the above for both rows and columns.

         Returns:
             bool: Indicates whether any progress was made (i.e., cells were crossed out).
         """
        crown: Cell | None = None
        crosses: list[Cell] = []

        min_value = 2
        max_value = math.ceil(len(self.areas) / 2)

        def process_line(areas_dictionary, get_lines_of_empty_cells):
            nonlocal min_value, max_value
            for i in range(min_value, max_value + 1):
                matching_areas = find_matching_entries(areas_dictionary, i)
                if matching_areas:
                    matching_lines: set[Line] = set(
                        line for area in matching_areas for line in get_lines_of_empty_cells(area))
                    all_cells = set(
                        cell for matching_line in matching_lines for cell in matching_line.get_empty_cells())
                    cells_to_cross = [cell for cell in all_cells if cell.area_ref not in matching_areas]
                    crosses.extend(cells_to_cross)
                    if cells_to_cross:
                        break

        # Apply rule for areas
        areas_rows = {area: rows for area, rows in
                      ((area, area.get_rows_of_empty_cells()) for area in self.areas.values()) if rows}
        areas_columns = {area: columns for area, columns in
                         ((area, area.get_columns_of_empty_cells()) for area in self.areas.values()) if columns}

        process_line(areas_rows, lambda area: area.get_rows_of_empty_cells())
        process_line(areas_columns, lambda area: area.get_columns_of_empty_cells())

        return crown, crosses

    def guess(self):
        """
            Attempts to guess the correct position for a crown on the game board when no other rules can be applied.
            It simulates placing a crown on the smallest area, checks the validity of the board after the guess,
            and then restores the board's state to its original configuration.

            This method follows these steps:
            1. Creates a dictionary of areas and their respective empty cells.
            2. Sorts areas by the number of empty cells and filters out areas with no empty cells.
            3. Saves the current state of the board, crowns, and click status for simulation purposes.
            4. Selects a cell from the area with the fewest empty cells and places a crown there.
            5. Attempts to solve the puzzle with the simulated guess.
            6. Checks if the board has been completed correctly (all areas have crowns).
            7. If the guess is valid, returns the result indicating a crown was placed and the target cell.
            8. Restores the board's original state, including the number of crowns and click status.

            Returns:
                tuple: A tuple containing two values:
                    - `crown_found` (bool): True if a valid crown was placed and the board is complete, False otherwise.
                    - `target_cell` (tuple): The cell where the crown was placed as part of the guess.
            """

        crown_found = False
        print("Guessing Crowns...")

        # Step 1: Create a dictionary with area keys and their empty cells
        area_empty_cells = {key: area.get_empty_cells() for key, area in self.areas.items()}

        # Step 2: Order the dictionary by the number of empty cells (values)
        sorted_area_empty_cells = dict(sorted(area_empty_cells.items(), key=lambda item: len(item[1])))

        # Step 3: Remove entries where the list of empty cells is empty
        filtered_area_empty_cells = {key: cells for key, cells in sorted_area_empty_cells.items() if cells}

        # Step 4: Make a simulated board (save current board to load later)
        save_state_board = self.board.save_state()
        save_crowns = self.crowns
        save_guess_flag = self.guess_flag
        self.guess_flag = True

        # Step 5: Disable clicking on real board
        save_click_enabled = self.click_enabled
        self.click_enabled = False

        # Step 6: Pick a cell in the smallest area
        target_cell = next(iter(filtered_area_empty_cells.values()))[0]
        self.crown_cell(target_cell)

        # Step 7: Attempt to solve with the guess
        self.solve()

        # Step 8: Check if the completed board is correct
        if self.crowns == len(self.areas):
            # Board is correct, we crown the target cell and continue to solve
            crown_found = True

        # Final Step: Undo the simulation
        self.click_enabled = save_click_enabled
        self.board.load_state(save_state_board)
        self.crowns = save_crowns
        self.guess_flag = save_guess_flag

        return crown_found, target_cell

    def apply_rules(self, rules):
        """
        Applies the list of rules sequentially.
        Returns:
            bool: True if progress was made, False otherwise.
        """
        for index, rule in enumerate(rules, start=1):
            crown, crosses = rule()
            if crown or crosses:
                print(f"Rule {index} ({rule.__name__}) found, restarting rules.")
            if crown:
                self.crown_cell(crown)
            if crosses:
                self.cross_cells(crosses)
            if crown or crosses:
                if not self.guess_flag:
                    time.sleep(self.sleep_time)  # Pause between rules
                return True  # Progress was made
        return False  # No progress

    def apply_guess(self):
        """
        Applies a guess when no progress is made.
        """
        crown_found, target_cell = self.guess()
        if self.stop_flag:
            return

        if crown_found:
            self.crown_cell(target_cell)
            print("Crown found!")
            crosses = self.get_crosses_from_crown(target_cell)
            self.cross_cells(crosses)
        else:
            self.set_cell_cross(target_cell)
            print("Crossed")

    def solve(self):
        """
        Solves the game board.
        """
        self.start_listener()  # Start the listener in a separate thread

        rules = [self.rule_one, self.rule_two, self.rule_three, self.rule_four, self.rule_five
                 # , self.rule_six
                 ]

        while not self.stop_flag:
            # Apply rules and check progress
            progress = self.apply_rules(rules)

            # Stop if board is complete
            if len(self.get_empty_spaces()) == 0:
                print("Board complete!")
                save_board_state(self.board)
                break

            # Make a guess if no progress was made
            if not progress:
                self.apply_guess()

        if self.stop_flag and not self.guess_flag:
            save_board_state(self.board)

    def cross_line(self):
        rows, cols = self.board.get_dimensions()
        x1, y1 = self.board.get_position_coordinates(0, 0)
        x2, y2 = self.board.get_position_coordinates(0, cols - 1)
        click_and_drag((x1, y1), (x2, y2))
