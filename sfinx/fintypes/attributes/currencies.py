import re

from sfinx.fintypes.attributes.valtypes import FinTabValTypes


class FinTabCurrency:
    """
    Represents the currency (if applicable) of a number mentioned in a table cell.
    """

    USD = "usd"
    DEFAULT = "default"

    def __init__(self):
        self.regex = re.compile(r"\b(usd)\b")

    @staticmethod
    def find(cell):
        """
        Given a table cell, finds the best matching currency for its value (if applicable).
        :param cell: A table cell
        :return: Type of currency implied in the cell value (if applicable).
        """
        if cell.val_type != FinTabValTypes.CURRENCY:
            return FinTabCurrency.DEFAULT
        h = " ".join([m.val for m in cell.metrics_hierarchy]).lower()
        if "$" in h:
            return FinTabCurrency.USD
        regex = re.compile(r"\b(usd)\b")
        if regex.search(h):
            return FinTabCurrency.USD
        return FinTabCurrency.DEFAULT
