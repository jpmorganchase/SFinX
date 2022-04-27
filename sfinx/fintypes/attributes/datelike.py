from datetime import datetime


class Datelike:
    """
    Represents a cell that has a value resembling a date.
    """
    def __init__(self, sheet, row, col, cell):
        self.sheet = sheet
        self.i = row+1
        self.j = col+1
        self.cell = cell
        self.year = datetime.now().year

    def cell_is_bold_header(self, cached):
        if self.cell.font and \
                self.cell.font.b and \
                (self.j == 1 or self.sheet.cell(self.i, self.j-1).value is None or self.i == 1 or self.sheet.cell(self.i-1, self.j).value is None):
            self.cell.value = str(self.cell.value)
            cached.add((self.i, self.j))
            return True
        return False

    def left_is_bold_header(self, cached):
        if self.cell.font and self.cell.font.b:
            left = self.sheet.cell(self.i, self.j-1)
            if isinstance(left.value, str) and left.font and left.font.b:
                self.cell.value = str(self.cell.value)
                cached.add((self.i, self.j))
                return True
        return False

    def top_is_bold_header(self, cached):
        if self.cell.font and self.cell.font.b:
            top = self.sheet.cell(self.i - 1, self.j)
            if isinstance(top.value, str) and top.font and top.font.b:
                self.cell.value = str(self.cell.value)
                cached.add((self.i, self.j))
                return True
        return False

    def left_is_cached(self, cached):
        if (self.i, self.j-1) in cached:
            self.cell.value = str(self.cell.value)
            cached.add((self.i, self.j))
            return True
        return False

    def top_is_cached(self, cached):
        if (self.i-1, self.j) in cached:
            self.cell.value = str(self.cell.value)
            cached.add((self.i, self.j))
            return True
        return False

    def left_says_year(self, cached):
        left = self.sheet.cell(self.i, self.j-1) if self.j > 0 else None
        if left and left.value and left.font and left.font.b and 'year' in str(left.value).lower():
            self.cell.value = str(self.cell.value)
            cached.add((self.i, self.j))
            return True
        return False

    def top_says_year(self, cached):
        top = self.sheet.cell(self.i-1, self.j) if self.i > 0 else None
        if top and top.value and top.font and top.font.b and 'year' in str(top.value).lower():
            self.cell.value = str(self.cell.value)
            cached.add((self.i, self.j))
            return True
        return False

    def convert_datelike_cell(self, cached):
        """
        Determines if the cell has date-like content.
        If so, converts the value of the cell accordingly,
        and populates the cache with its indices.
        :param cached: A set keeping track of indices of date-like cells.
        :return: A boolean indicating whether the cell has been identified as a date-like cell.
        """
        if not isinstance(self.cell.value, int): return False
        if self.cell.value < 1900: return False
        if self.cell.value - 50 > self.year: return False
        if self.cell_is_bold_header(cached): return True
        if self.left_is_bold_header(cached): return True
        if self.top_is_bold_header(cached): return True
        if self.left_is_cached(cached): return True
        if self.top_is_cached(cached): return True
        if self.left_says_year(cached): return True
        if self.top_says_year(cached): return True
        return False
