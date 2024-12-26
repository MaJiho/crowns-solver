from typing import Dict, List, Any

import input_utils
from board.area import Area
from board.cell import Cell
from board.line import Row, Column, Line
from collections import defaultdict

from logic_utils import find_matching_entries
from settings import get_setting
import threading
from pynput import keyboard


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

        self.click_cross_enabled = get_setting("click_cross_enabled")
        self.click_crown_enabled = get_setting("click_crown_enabled")
        self.click_enabled = get_setting("click_enabled")

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
        click = get_setting("click_crown_enabled")
        while not cell.is_crown():
            self.toggle_cell(cell, click)

    def set_cell_cross(self, cell, click=get_setting("click_cross_enabled")):
        """
        Toggles the cell's state until it is set to 'cross'.
        """
        while not cell.is_cross():
            self.toggle_cell(cell, click)

    def toggle_cell(self, cell, click=True):
        """
            Toggles the cell's state and clicks it on screen if click is true.
        """
        x, y = self.board.get_cell_coordinates(cell)
        cell.toggle_state()

        # Click the screen
        if click and self.click_enabled:
            duration = get_setting("click_duration")
            input_utils.click_at((x, y), duration)

    def click_and_drag_cells(self, cells: list[Cell]):
        # Change state of cells to crossed without clicking
        for cell in cells:
            self.toggle_cell(cell, click=False)

        start = self.board.get_cell_coordinates(cells[0])
        end = self.board.get_cell_coordinates(cells[-1])
        input_utils.click_and_drag(start, end)

    def set_all_cells_crossed(self, cells_to_cross: List[Cell]):
        """
        Calculate the optimal path for clicking all cells.

        Args:
            cells_to_cross (List[Cell]): List of `Cell` objects with `x` and `y` coordinates.

        Raises:
            TypeError: If any element in `cells` is not a `Cell` object.
        """
        if not all(isinstance(cell, Cell) for cell in cells_to_cross):
            raise TypeError("All elements in the 'cells' list must be instances of the 'Cell' class.")

        # If clicking is not enable, we only change states
        if not get_setting("click_cross_enabled") or not get_setting("click_enabled"):
            for cell in cells_to_cross:
                self.set_cell_cross(cell)

        # Filter any cell that isn't empty
        cells_to_cross = [cell for cell in cells_to_cross if cell.is_empty()]

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
            line_cells = line.intersect_cells(cells_to_cross)
            line_segments = self.make_line_segments(line, line_cells)
            for line_segment in line_segments:
                segments.append(line_segment)

        # Click and drag by segments
        while segments:
            # Order segments
            segments: list[list[Cell]] = sorted(segments, key=len, reverse=True)

            largest_segment = segments.pop(0)
            if len(largest_segment) > 1:  # Click and drag
                self.click_and_drag_cells(largest_segment)
            elif len(largest_segment) == 1:  # Click
                self.set_cell_cross(largest_segment[0])

            # Remove used cells from the other segments
            for cell in largest_segment:
                for segment in segments:
                    if cell in segment:
                        segment.remove(cell)
                    if not segment:
                        segments.remove(segment)

    def make_line_segments(self, line: Line, cells: list[Cell]):

        if not line.contains_cells(cells):
            raise ValueError("The given cells should all be part of the given line.")

        all_segments = []
        segment = []

        for line_cell in line.cells:
            # For segments, we consider empty lines that should be crossed as well as non-empty lines,
            # since they won't be affected
            if line_cell in cells or not line_cell.is_empty():
                segment.append(line_cell)
            else:
                if len(segment) > 0:
                    all_segments.append(segment)
                segment = []

        return all_segments

    def place_crown(self, cell):
        """
        Places a crown on the given cell by interacting with its row, column, and area references.

        Args:
            cell (Cell): The cell where the crown should be placed.
        """
        # Combine the cells from the row, column, and area into a set (to avoid duplicates)
        cells_to_process = set(
            cell.row_ref.cells + cell.column_ref.cells + cell.area_ref.cells + self.board.get_surrounding_cells(
                cell))

        # Remove the given cell from the set
        cells_to_process.discard(cell)

        # Place a crown on the given cell
        self.set_cell_crown(cell)

        # Place a cross on every other cell in the set
        self.set_all_cells_crossed(list(cells_to_process))
        # for other_cell in cells_to_process:
        #     self.set_cell_cross(other_cell)

    def get_empty_spaces(self):
        return [cell for area in self.areas.values() for cell in area.get_empty_cells()]

    def rule_one(self):
        """
        Checks if an area or a line has a single empty spot, which should be considered a crown.

        This method inspects each area and line on the board. If an area or a line contains exactly
        one empty spot, that spot is designated as a crown and a crown is placed there.

        Returns:
            bool: True if a crown was placed according to this rule, False otherwise.
        """
        # Check for crowns in areas
        for area in self.areas.values():
            cell_to_crown = area.check_empty_spot()
            if cell_to_crown:
                self.place_crown(cell_to_crown)
                return True

        # Check for crowns in lines (rows and columns)
        for line in self.rows + self.columns:
            cell_to_crown = line.check_empty_spot()
            if cell_to_crown:
                self.place_crown(cell_to_crown)
                return True

        return False

    def rule_two(self):
        """
        Checks for empty cells of an area that occupy 1 line (row or column).
        If all empty cells of an area are in the same row or column, perform the action (e.g., place a crown).
        """
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
                # Remove the empty cells from the row cells
                remaining_cells = [cell for cell in line_cells if
                                   cell not in area_empty_cells and cell.is_empty()]
                if remaining_cells:
                    # Apply set_cell_cross to the remaining cells in the row
                    self.set_all_cells_crossed(remaining_cells)

                    # for cell in remaining_cells:
                    #   self.set_cell_cross(cell)

                    return True

        return False

    def rule_three(self):
        """
        Checks for rows/columns with only one possible area.
        If all empty cells in a row or column belong to the same area,
        the remaining empty cells of that area (excluding the row/column cells) get crossed.
        """
        progress = False

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
                remaining_cells = [cell for cell in area_empty_cells if
                                   cell not in line_empty_cells and cell.is_empty()]

                # Step 5: Cross the remaining cells
                if remaining_cells:
                    progress = True
                    self.set_all_cells_crossed(remaining_cells)
                # for cell in remaining_cells:
                #     if cell.state == "empty":
                #         self.set_cell_cross(cell)
                #         progress = True

        return progress

    def rule_four(self):
        """
        Checks for impossible spaces in areas.
        For each area, identifies surrounding cells of all empty spaces,
        and if a cell is common to all surrounding spaces, it gets crossed.
        """
        # Step 1: Sort areas by the number of empty spaces (ascending)
        areas_by_empty_cells = sorted(self.areas.values(), key=lambda a: len(a.get_empty_cells()))

        progress = False  # To track if any changes were made

        # Step 2: Iterate through each area
        for area in areas_by_empty_cells:
            empty_cells = area.get_empty_cells()

            # Skip areas with no empty cells or only one empty cell
            if len(empty_cells) < 2:
                continue

            # Step 3: Collect surrounding cells AND lines for all empty cells
            surrounding_cells_list = [
                set(self.board.get_surrounding_cells(cell)) | set(cell.row_ref.get_line_except_cell(cell)) |
                set(cell.column_ref.get_line_except_cell(cell))
                for cell in empty_cells
            ]

            # Step 4: Intersect all surrounding cells
            common_cells = set.intersection(*surrounding_cells_list)

            # Step 5: Cross the common cells that are empty
            common_cells = [cell for cell in common_cells if cell.is_empty()]
            if common_cells:
                progress = True
                self.set_all_cells_crossed(common_cells)
            # for cell in common_cells:
            #     if cell.state == "empty":
            #         self.set_cell_cross(cell)
            #         progress = True

        return progress

    def rule_five(self):
        """
        Rule 5: Pairs areas by rows or columns
        """
        progress = False  # To track if any changes were made

        # Initialize max values for rows and columns
        max_empty_rows = 2
        max_empty_columns = 2

        # Initialize min values for rows and columns
        min_empty_rows = 2
        min_empty_columns = 2

        # Step 1: Iterate through all areas
        area_rows_dict = {}  # Dictionary to store rows for each area
        area_columns_dict = {}  # Dictionary to store rows for each area

        for area_id, area in self.areas.items():
            # Get the empty columns and rows for this area
            empty_columns = area.get_columns_of_empty_cells()
            empty_rows = area.get_rows_of_empty_cells()

            # Step 2: Update max values
            max_empty_rows = max(max_empty_rows, len(empty_rows))
            max_empty_columns = max(max_empty_columns, len(empty_columns))

            # Step 3: Store the rows and columns in the dictionaries
            area_rows_dict[area_id] = empty_rows
            area_columns_dict[area_id] = empty_columns

        def process_line(area_dict, min_value, max_value):
            nonlocal progress
            # Sort the dictionary by the length of the lists (ascending order)
            sorted_dict = dict(sorted(area_dict.items(), key=lambda item: len(item[1])))

            # Iterate from min_value to max_value (inclusive)
            for i in range(min_value, max_value + 1):
                filtered_dict = {a: rows for a, rows in sorted_dict.items() if len(rows) == i}

                # Dictionary to group areas by their rows (values)
                grouped_rows = defaultdict(list)

                # Group areas by their row values
                for c_area, rows in filtered_dict.items():
                    grouped_rows[tuple(rows)].append(c_area)

                # Now filter to only include entries with exactly 'i' areas with the same rows
                matching_entries = {key: value for key, value in grouped_rows.items() if len(value) == i}

                if matching_entries:
                    cols = list(next(iter(matching_entries.keys())))
                    areas = [self.areas[key] for key in next(iter(matching_entries.values()))]

                    # Initialize an empty set to store the final results
                    final_col_cells = set()

                    # For each column, get the empty cells and join them all in one set
                    for column in cols:
                        col_cells = set(column.get_empty_cells())  # Get the empty cells for the column
                        final_col_cells.update(col_cells)  # Add them to the final set

                    # For each area, get its empty cells and remove them from the final column cells
                    for c_area in areas:
                        area_cells = set(c_area.get_empty_cells())  # Get the empty cells for the area
                        final_col_cells.difference_update(area_cells)  # Remove area cells from the column cells

                    final_col_cells = [cell for cell in final_col_cells if cell.is_empty()]
                    if final_col_cells:
                        progress = True
                        self.set_all_cells_crossed(final_col_cells)

                    # for cell in final_col_cells:
                    #     if cell.state == "empty":
                    #         self.set_cell_cross(cell)
                    #         progress = True

        # Step 4: Process Rows
        process_line(area_rows_dict, min_empty_rows, max_empty_rows)
        # Step 5: Process Columns
        process_line(area_columns_dict, min_empty_columns, max_empty_columns)

        return progress

    def rule_six(self):
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
        progress = False
        min_value = 2
        max_value = len(self.areas)

        def process_line(line_areas, get_empty_area_lines):
            nonlocal min_value, max_value, progress
            for i in range(min_value, max_value + 1):
                # Find i lines with the same areas
                matching_lines = find_matching_entries(line_areas, i)
                if matching_lines:
                    # Get the areas from the match
                    matching_areas = list({area for line in list(matching_lines.values()) for area in line})
                    # Guarantee they have i areas
                    if len(matching_areas) == i:
                        # Analyze each areas lines to cross lines not in line_areas
                        total_lines = {line for area in next(iter(matching_lines.values())) for line in
                                       get_empty_area_lines(area)}

                        # Remove the matching lines from the total lines
                        crossed_lines = [line for line in total_lines if line not in list(matching_lines.keys())]
                        crossed_line_cells = [cell for line in crossed_lines for cell in line.get_empty_cells()]

                        # Get cells from the matching areas
                        area_cells = [cell for area in matching_areas for cell in area.get_empty_cells()]

                        # Intersect the cell groups
                        crossed_cells = set(crossed_line_cells) & set(area_cells)

                        crossed_cells = [cell for cell in crossed_cells if cell.is_empty()]
                        if crossed_cells:
                            progress = True
                            self.set_all_cells_crossed(crossed_cells)

                        # for cell in crossed_cells:
                        #     if cell.state == "empty":
                        #         self.set_cell_cross(cell)
                        #         progress = True

                        print()

        rows_areas = {row: row.get_empty_areas() for row in self.rows}
        columns_areas = {column: column.get_empty_areas() for column in self.columns}

        process_line(rows_areas, lambda area: area.get_rows_of_empty_cells())
        process_line(columns_areas, lambda area: area.get_columns_of_empty_cells())

        return progress

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

        # Step 5: Disable clicking on real board
        save_click_enabled = self.click_enabled
        self.click_enabled = False

        # Step 6: Pick a cell in the smallest area
        target_cell = next(iter(filtered_area_empty_cells.values()))[0]
        self.place_crown(target_cell)

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

        return crown_found, target_cell

    def solve(self):
        """
        Solves the game board.
        """
        # self.cross_line()
        self.start_listener()  # Start the listener in a separate thread

        # List of rules to apply
        rules = [self.rule_one, self.rule_two, self.rule_three, self.rule_four,
                 self.rule_five, self.rule_six]

        while not self.stop_flag:  # Check for stop flag
            progress = False
            for index, rule in enumerate(rules, start=1):
                progress = rule()
                if progress:
                    print(f"Rule {index} ({rule.__name__}) found, restarting rules.")
                    break  # If progress is made, restart from the first rule

            if progress:
                continue  # Go back to the start of the rules
            elif len(self.get_empty_spaces()) > 0:  # There are still empty spaces
                crown_found, target_cell = self.guess()  # Try to guess an impossible space
                if crown_found:
                    self.place_crown(target_cell)
                    print("Crown found!")
                else:
                    self.set_cell_cross(target_cell)
                    print("Crossed")
                progress = True

            # It should go in here when board has no more empty spaces
            if not progress:
                print("No progress made, stopping.")
                break  # If no crowns are placed in a full cycle, stop

        # Further steps to be added later...

    def cross_line(self):
        rows, cols = self.board.get_dimensions()
        x1, y1 = self.board.get_position_coordinates(0, 0)
        x2, y2 = self.board.get_position_coordinates(0, cols - 1)
        input_utils.click_and_drag((x1, y1), (x2, y2))
