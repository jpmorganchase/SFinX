import re
from sfinx.fintypes.attributes.valtypes import FinTabValTypes


class FinTabScale:
    """
    Represents the scale of a number mentioned in a table cell.
    """
    DEFAULT = 'default'

    def __init__(self, name, regex):
        self.name = name
        self.regex = re.compile(regex)

    def match(self, text):
        if self.regex.search(text): return self.name
        return self.DEFAULT

    @staticmethod
    def find(cell):
        """
        Given a table cell, finds the best matching scale for its value.
        :param cell: A table cell
        :return: The name of an object of the FinTabScale class.
        """
        if cell.val_type == FinTabValTypes.PERCENT: return FinTabScale.DEFAULT
        scales = [Millions(), Billions(), Thousands()]
        h = ' '.join([m.val for m in cell.metrics_hierarchy]).lower()
        for scale in scales:
            if scale.match(h) != FinTabScale.DEFAULT:
                return scale.name
        return FinTabScale.DEFAULT


class Billions(FinTabScale):
    def __init__(self):
        super().__init__("billions", r"\b(billion|bb)s?\b")


class Millions(FinTabScale):
    def __init__(self):
        super().__init__("millions", r"\b(million|mm)s?\b")


class Thousands(FinTabScale):
    def __init__(self):
        super().__init__("thousands", r"\b(thousand|000)s?\b")
