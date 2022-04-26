from src.fintypes.attributes.datelike import Datelike
from src.fintypes.components.cell import FinTabCell, FinTabMergedCellGroup


class FinSheet:
    """
    Represents a worksheet with one or more financial tables.
    """
    def __init__(self, sheet_name, sheet):
        # main members
        self.sheet_name = sheet_name
        self.nrows = sheet.max_row
        self.ncols = sheet.max_column
        self.cells = {}  # map of coordinates (i, j) to cell object
        self.empty_rows = set()  # Ordered list of row indices that are empty. This is helpful for identifying table boundaries
        self.empty_cols = set()  # Ordered list of column indices that are empty. This is helpful for identifying table boundaries.
        self.tables = []  # list of tables within the current sheet (note that one worksheet may include more than one table)
        # helper properties
        self.unmerged_cols = set()  # keeps track of column-wise merged cells
        self.unmerged_rows = set()  # keeps track of row-wise merged cells
        self._converted_to_date = set()  # caches integer rows that have been converted to a date
        # processor methods
        self._unmerge_cells(sheet)
        self._populate_cells(sheet)
        self._set_headers()

    def _unmerge_cells(self, sheet):
        """
        Identifies merged cells in a worksheet, unmerges them,
        and stores them in self.unmerged_rows and self.unmerged_cols.
        :param sheet: A worksheet possibly including merged cells.
        """
        for group in sheet.merged_cell_ranges:
            g = FinTabMergedCellGroup(sheet, group)
            sheet.unmerge_cells(str(group))
            row_indices, col_indices = g.get_indices(sheet)
            self.unmerged_rows |= row_indices
            self.unmerged_cols |= col_indices

    def _populate_cells(self, sheet):
        """
        Converts each cell in the sheet into a FinTabCell object
        :param sheet: An MS Excel worksheet
        :return: A map of indices to FinTabCell objects
        """
        non_empty_rows, non_empty_cols = set(), set()
        for i, row in enumerate(sheet.rows):
            for j, cell in enumerate(row):
                # Identify all footnote flags and clean them up.
                cell, footnote_flags = FinTabCell.clean_footnotes(cell)
                # Identify and convert all cells that contain date-like content.
                d = Datelike(sheet, i, j, cell)
                d.convert_datelike_cell(self._converted_to_date)
                # Convert cell objects into FinTabCell objects
                c = FinTabCell(i, j, cell, footnote_flags)
                self.cells[(i, j)] = c
                # Keep track of non-empty rows and columns. If there are multiple tables on the sheet,
                # this helps identify table boundaries
                if not c.is_empty:
                    non_empty_rows.add(i)
                    non_empty_cols.add(j)
        # Using the indices of non-empty rows and columns, identify empty rows and columns
        self.empty_rows = set([-1] + [i for i in range(self.nrows) if i not in non_empty_rows])
        self.empty_cols = set([-1] + [j for j in range(self.ncols) if j not in non_empty_cols])
        return self.cells

    def _set_headers(self):
        """
        Given a map of indices --> cells, identifies cells that are row/column headers
        """
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) in self.cells and self.cells[(i, j)].is_body:
                    # Identify the columns and row headers of each cell
                    self.cells[(i, j)].col_header = self._set_cell_col_header(i, j)
                    self.cells[(i, j)].row_header = self._set_cell_row_header(i, j)
                else:
                    # Sometimes headers are hierarchical. This step helps propagate super-headers to sub-headers.
                    # It first attempts to propagate headers downward.
                    downward_success = self._propagate_headers_downward(i, j)
                    # It downward propagation fails, then it attempts to propagate the headers rightward.
                    rightward_success = False
                    if not downward_success:
                        rightward_success = self._propagate_headers_rightward(i, j)

    def _set_cell_col_header(self, i, j):
        """
        Given the row and column indices of a cell, find its corresponding column header.
        :param i: The row index of the current cell.
        :param j: The column index of the current cell.
        :return: The list of all cells that qualify as the current cell's column header.
        """
        # Find the closest upward cell that is non-empty
        k = i - 1
        while k-1 not in self.empty_rows and (k, j) in self.cells and self.cells[(k, j)].is_empty: k -= 1
        # This top neighbor is either a header, or a cell with the same col header as the current cell.
        if (k, j) in self.cells:
            top_neighbor = self.cells[(k, j)]
            if top_neighbor.is_body and top_neighbor.col_header: return top_neighbor.col_header
            if top_neighbor.is_header:
                output = []
                while top_neighbor is not None and top_neighbor.is_header:
                    output = top_neighbor.inherited_header + output
                    k -= 1
                    top_neighbor = self.cells.get((k, j), None)
                return output
            return top_neighbor.inherited_header
        return []

    def _set_cell_row_header(self, i, j):
        """
        Given the row and column indices of a cell, find its corresponding row header.
        :param i: The row index of the current cell.
        :param j: The column index of the current cell.
        :return: The list of all cells that qualify as the current cell's row header.
        """
        # Find the closest leftward cell that is non-empty
        k = j - 1
        while k-1 not in self.empty_cols and (i, k) in self.cells and self.cells[(i, k)].is_empty: k -= 1
        # This left neighbor is either a header, or a cell with the same row header as the current cell.
        if (i, k) in self.cells:
            left_neighbor = self.cells[(i, k)]
            if left_neighbor.is_body and left_neighbor.row_header: return left_neighbor.row_header
            if left_neighbor.is_header:
                output = []
                while left_neighbor is not None and left_neighbor.is_header:
                    output = left_neighbor.inherited_header + output
                    k -= 1
                    left_neighbor = self.cells.get((i, k), None)
                return output
            return left_neighbor.inherited_header
        return []

    def _propagate_headers_downward(self, i, j):
        """
        Given the row and column index of a cell including a header, propagates that header value downward.
        Propagation is only possible if the subsequent cell is also a header, and its style
        seems equal or subordinate to the current cell's style.
        :param i: The row index of the current cell
        :param j: The column index of the current cell
        :return: A boolean indicating whether the propagation was successful
        """
        curr = self.cells[(i, j)]
        nxt = self.cells.get((i + 1, j), None)
        if not nxt: return False
        if not nxt.is_header: return False
        if nxt.sub(curr):
            nxt.inherited_header = curr.inherited_header + nxt.inherited_header
            return True
        if nxt.equal(curr):
            nxt.inherited_header = curr.inherited_header[:-1] + nxt.inherited_header
            return True
        return False

    def _propagate_headers_rightward(self, i, j):
        """
        Given the row and column index of a cell including a header, propagates that header value rightward.
        Propagation is only possible if the subsequent cell is also a header, and its style
        seems equal or subordinate to the current cell's style.
        :param i: The row index of the current cell
        :param j: The column index of the current cell
        :return: A boolean indicating whether the propagation was successful
        """
        curr = self.cells[(i, j)]
        nxt = self.cells.get((i, j + 1), None)
        if not nxt: return False
        if not nxt.is_header: return False
        if nxt.sub(curr):
            nxt.inherited_header = curr.inherited_header + nxt.inherited_header
            return True
        if nxt.equal(curr):
            nxt.inherited_header = curr.inherited_header[:-1] + nxt.inherited_header
            return True
        return False
