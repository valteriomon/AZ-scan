
import re
import string
from core import utils

class GridSets:
    # Returns specific sets given partial or full grids.
    # @staticmethod
    # def grid_has_no_empty_values(grid):
    #     return all(all(cell not in (None, '', [], {}) for cell in row) for row in grid)

    @staticmethod
    def validate_array_items_pattern(arr):
        pattern = re.compile(r"^[A-Z]\d{1,2}$")
        return all(isinstance(item, str) and pattern.match(item) for item in arr)

    @staticmethod
    def validate_grid_completeness(grid):
        if not grid or not all(isinstance(row, list) for row in grid):
            return False  # must be a list of lists

        num_cols = len(grid[0])
        for i, row in enumerate(grid):
            if len(row) != num_cols:
                raise ValueError("Grid has inconsistent row lengths.")
            expected_row_label = chr(ord('A') + i)
            for j, item in enumerate(row):
                expected_value = f"{expected_row_label}{j + 1}"
                if item != expected_value:
                    raise ValueError("Grid cells don't follow the expected pattern of letters for rows, numbers for columns.")
        return True

    """
    Given an array like ['A1', 'B3', 'C2'], builds a matrix (list of lists)
    with the appropriate size, inserting values at their correct positions
    and filling missing positions with None.
    """
    @staticmethod
    def build_matrix_from_cells(cells):
        # Parse the cells into (row_index, col_index) tuples
        parsed = []
        for cell in cells:
            if len(cell) < 2 or not cell[0].isalpha() or not cell[1:].isdigit():
                raise ValueError(f"Invalid cell format: {cell}")
            row_char = cell[0].upper()
            col_num = int(cell[1:])
            row_index = string.ascii_uppercase.index(row_char)
            col_index = col_num - 1  # zero-based index
            parsed.append((row_index, col_index, cell))

        # Determine matrix size
        max_row = max(r for r, _, _ in parsed)
        max_col = max(c for _, c, _ in parsed)

        # Create matrix filled with None
        matrix = [[None for _ in range(max_col + 1)] for _ in range(max_row + 1)]

        # Fill in known values
        for r, c, val in parsed:
            matrix[r][c] = val

        return matrix

    @staticmethod
    def quadruplets(grid, use_alphabetical_rows=True):
        GridSets.validate_grid_completeness(grid)
        rows = len(grid)
        cols = len(grid[0])

        combinations = []
        for col in range(cols - 1):
            for row in range(rows - 1):
                mat = [
                    [row + 1, col + 1],
                    [row + 1, col + 2],
                    [row + 2, col + 1],
                    [row + 2, col + 2],
                ]
                combinations.append(GridSets._convert_mat_to_str_array(mat, use_alphabetical_rows))
        return combinations

    @staticmethod
    def inverted_diagonal_couples(grid, use_alphabetical_rows=True):
        GridSets.validate_grid_completeness(grid)
        rows = len(grid)
        cols = len(grid[0])

        combinations = []

        for col in range(cols - 1):
            for row in range(rows - 1):
                mat = []
                if not row % 2:
                    mat = [
                        [row + 1, col + 2],
                        [row + 2, col + 1],
                    ]
                else:
                    mat = [
                        [row + 1, col + 1],
                        [row + 2, col + 2],
                    ]
                combinations.append(GridSets._convert_mat_to_str_array(mat, use_alphabetical_rows))
        return combinations

    @staticmethod
    def last_adjacent_neighbours(grid):
        # Empty or single element grid
        if len(grid) == 0 or (len(grid) == 1 and utils.count_valid_elements(grid[0]) <= 1):
            return []

        # First row, with at least two elements
        if len(grid) == 1 and len(grid[0]) > 1:
            (cell, col) = utils.get_last_valid_element(grid[0])
            return [grid[0][col], grid[0][col - 1]]

        # More than one row from now on
        rows = len(grid)

        # Last row contains a single valid element, return only element above
        if utils.count_valid_elements(grid[-1]) == 1:
            cell, col = None, None  # Initialize variables

            if rows % 2: # Odd rows (3, 5, 7...)
                (cell, col) = utils.get_last_valid_element(grid[-1])
            else: # Even rows (2, 4, 6, 8...)
                (cell, col) = utils.get_first_valid_element(grid[-1])

            if cell is not None and col is not None and grid[-2]:
                return [
                    cell,
                    grid[-2][col]
                ]
            else:
                raise ValueError("Invalid column or grid structure.")

        # All other instances will return side and up
        if rows % 2:
            (cell, col) = utils.get_last_valid_element(grid[-1])
            return [
                cell,
                grid[-2][col],
                grid[-1][col - 1]
            ]
        else:
            (cell, col) = utils.get_first_valid_element(grid[-1])
            return [
                cell,
                grid[-2][col],
                grid[-1][col + 1]
            ]

    @staticmethod
    def _convert_mat_to_str_array(mat, use_alphabetical_rows=True):
        if use_alphabetical_rows:
            mat = [f"{utils.alpha_converter(item[0])}{item[1]}" for item in mat]
        else:
            mat = [f"{item[0]}{item[1]}" for item in mat]
        return mat
