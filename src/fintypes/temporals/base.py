import re
from src.fintypes.attributes.valtypes import FinTabValTypes


class Temporal:
    """
    Represents any temporal expression such as years, quarters, months, semi-annual periods, or exact dates.
    """
    def __init__(self,  name):
        self.name = name
        self.regexes = []

    def add_regex(self, regex):
        self.regexes.append(re.compile(regex))

    @staticmethod
    def has_period_expr(header, months):
        """
        Determines whether a header string is likely to include an expression of period
        :param header: The header string
        :param months: A list of Month objects
        :return: Boolean indicating whether header is likely to include a period
        """
        if header.val_type == FinTabValTypes.DATE: return True
        l = header.val.lower().strip()
        for month in months:
            if month.get(l):
                return True
        regex = re.compile(r"\b(quarter|qtr|months|mos|days|ended|ending|period|[1-4]q|q[1-4]|q|[12][0-9]{3})\b")
        output = header.val_type == FinTabValTypes.TEXT and regex.search(l)
        if output:
            return True
        regex2 = re.compile(r"\bmay[\-\s.][0-9]+")
        if regex2.search(l):
            return True
        if l == 'may':
            return True
        return False
