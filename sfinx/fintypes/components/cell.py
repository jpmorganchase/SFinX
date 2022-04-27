import re
from sfinx.fintypes.attributes.colors import FinTabColors
from sfinx.fintypes.attributes.styles import FinTabStyles
from sfinx.fintypes.attributes.valtypes import FinTabValTypes


class FinTabCell:
    """
    Represents a cell in a financial table.
    """
    FOOTNOTE_FLAG_REGEX = re.compile(r"(\*+|[(\[][a-z1-9]+[])])$")

    def __init__(self, i, j, cell, flags):
        """
        :param i: Row index of the cell
        :param j: Column index of the cell
        :param cell: Value of the cell
        :param flags: Any footnotes attached to the value
        """
        self.i = i
        self.j = j
        self.val = cell.value
        self.flags = flags
        self.val_type = FinTabValTypes.get_cell_type(cell)
        if self.val_type == FinTabValTypes.CURRENCY:
            try:
                self.val = float(self.val)
            except ValueError:
                pass
            except TypeError:
                pass
        if self.val_type in [FinTabValTypes.CURRENCY, FinTabValTypes.FLOAT] and str(self.val).strip() == '-': self.val = 0.0
        if self.val_type in [FinTabValTypes.INT] and str(self.val).strip() == '-': self.val = 0
        self.number_format = cell.number_format
        self.val_str = self._convert_to_str()
        try:
            self.style = cell.style
        except IndexError:
            self.style = FinTabStyles.NORMAL
        self.font_size = cell.font.sz if cell.font.sz else 11.0
        self.font_is_bold = cell.font.b if cell.font.b else False
        self.font_is_italic = cell.font.i if cell.font.i else False
        self.font_color = FinTabColors.get_cell_font_color_hex(cell)[2:]
        self.bg_color = FinTabColors.get_cell_fill_color_hex(cell)
        self.horizontal_alignment = cell.alignment.horizontal if cell.alignment else FinTabStyles.HORIZONTAL_ALIGNMENT_LEFT
        self.col_header = None
        self.row_header = None
        self.inherited_header = [
            FinTabHeader(self.i, self.j, self.val, self.val_type, self.number_format, self.flags)] if \
            self.is_header else []
        self.period = None
        self.metrics_hierarchy = []

    def _convert_to_str(self):
        """
        Returns the string representation of the cell value.
        """
        if self.val is None: return ''
        if self.val_type in [FinTabValTypes.TEXT, FinTabValTypes.PERCENT, FinTabValTypes.CURRENCY]: return self.val
        if self.val_type == FinTabValTypes.DATE: return self.val.strftime('%Y-%m-%d')
        if self.val_type == FinTabValTypes.FLOAT: return "{:,.2f}".format(self.val)
        return str(self.val)

    def sub(self, other):
        """
        Determines whether self is a subordinate cell to other.
        """
        if not isinstance(other, FinTabCell): return False
        if self.style == FinTabStyles.NORMAL and other.style != FinTabStyles.NORMAL: return True
        if self.equal(other) and self.font_color > other.font_color: return True

        return self.font_size < other.font_size or \
               (not self.font_is_bold and other.font_is_bold) or \
               (not self.font_is_italic and other.font_is_italic) or \
               (self.horizontal_alignment == FinTabStyles.HORIZONTAL_ALIGNMENT_LEFT and
                other.horizontal_alignment == FinTabStyles.HORIZONTAL_ALIGNMENT_CENTER)

    def equal(self, other):
        """
        Determines whether self is equal in the hierarchy of cells to other.
        """
        if not isinstance(other, FinTabCell): return False
        return self.font_size == other.font_size and \
               self.font_is_bold == other.font_is_bold and \
               self.font_is_italic == other.font_is_italic

    @property
    def is_empty(self):
        """
        Determines if the content of self is empty.
        """
        return self.val is None or len(str(self.val).strip()) == 0

    @property
    def is_body(self):
        """
        Determines whether self is a body cell (as opposed to a header cell).
        """
        return not self.is_empty and \
               self.val_type not in [FinTabValTypes.TEXT, FinTabValTypes.DATE, FinTabValTypes.DEFAULT]

    @property
    def is_header(self):
        """
        Determines whether self is a header cell (as opposed to a body cell).
        """
        return not self.is_empty and not self.is_body

    @staticmethod
    def clean_footnotes(cell):
        """
        Given a cell, separates its values from possible footnotes flags
        :param cell: A cell in an MS Excel worksheet
        :return: A tuple containing the raw cell value as well as flags indicating possible footnotes
        """
        footnote_flag = []
        if cell.value and cell.data_type in ['s', 'n']:
            s = str(cell.value)
            hit = FinTabCell.FOOTNOTE_FLAG_REGEX.search(s.lower())
            if hit:
                a, b = hit.span()
                footnote_flag.append(s[a:b])
                cell.value = cell.value[0:a]+cell.value[b:]
                if '.' not in s:
                    try:
                        cell.value = int(cell.value)
                    except ValueError:
                        pass
                else:
                    try:
                        cell.value = float(cell.value)
                    except ValueError:
                        pass
        return cell, footnote_flag


class FinTabHeader:
    """
    Represents a header cell.
    """
    def __init__(self, i, j, val, val_type, number_format, flags):
        self.i = i
        self.j = j
        self.val = val
        self.val_type = val_type
        self.number_format = number_format
        self.flags = flags

    @property
    def key(self):
        return self.val + ',' + str(self.i) + ',' + str(self.j)


class FinTabMergedCellGroup:
    """
    Represents a group of merged cells in a financial table.
    """
    def __init__(self, sheet, group):
        self.group = group  # The group of merged cells
        self.top_left_cell_value = sheet.cell(row=group.min_row, column=group.min_col).value  # top-left coords
        self.row_wise = self.group.max_row > self.group.min_row  # Indicates whether cells are merged row-wise
        self.col_wise = self.group.max_col > self.group.min_col  # Indicates whether cells are merged column-wise
        self.row_indices = set()  # Keeps track of row-wise indices
        self.col_indices = set()  # Keeps track of column-wise indices

    def get_indices(self, sheet):
        """
        Returns the full indices of unmerged cells within the current worksheet.
        :param sheet: Current worksheet (within which the merged cell group exists).
        :return: Set of row-wise and column-wise indices of the merge group within the worksheet.
        """
        i = -1
        for row in sheet.iter_rows(min_col=self.group.min_col, min_row=self.group.min_row, max_col=self.group.max_col,
                                   max_row=self.group.max_row):
            i += 1
            j = -1
            for cell in row:
                j += 1
                cell.value = self.top_left_cell_value
                if self.row_wise: self.row_indices.add((i, j))
                if self.col_wise: self.col_indices.add((i, j))
        return self.row_indices, self.col_indices
