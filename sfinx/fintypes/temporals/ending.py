import re

from dateutil.relativedelta import relativedelta

from sfinx.fintypes.temporals.base import Temporal


class Ending(Temporal):
    """
    Represents a period expression such as "3 months ending Sep 30, 2020".
    """

    MONTHS = "months"
    DAYS = "days"
    NUM_MAP = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }

    def __init__(self, name):
        super().__init__(name)

    def get(self, text):
        """
        Finds the occurrence of a semi-annual period in a string
        :param text: input string
        :return: index of semi-annual period expressed in text (or None)
        """
        for regex in self.regexes:
            hit = regex.search(text)
            if not hit:
                continue
            i, j = hit.span()
            span = text[i:j]
            count = None
            for num, dig in self.NUM_MAP.items():
                if span.startswith(num):
                    count = dig
            if count is None:
                count = int("".join([c for c in span if c.isdigit()]))
            if self.name == self.MONTHS:
                return relativedelta(months=-1 * count)
            if self.name == self.DAYS:
                return relativedelta(days=-1 * count)
        return None

    @staticmethod
    def find(text, ending_periods):
        """
        Finds the occurrence of period in a string in the form of "x months/days ended"
        :param text: input string
        :param ending_periods: a list of ending periods to consider (e.g. months ended or days ended)
        :return: the period expression, normalized as a relativedelta object
        """
        ss = re.split(r"\b(ended|ending)\s?(in|on|at|by)?\b", text)
        if len(ss) <= 1:
            return None
        expr = " ".join([x for x in ss[:-1] if x])
        for period in ending_periods:
            idx = period.get(expr)
            if idx:
                return idx
        return None


class MonthsEnding(Ending):
    def __init__(self):
        super().__init__(Ending.MONTHS)
        self.add_regex(r"[0-9]+\s?(months|mos|mo\.s)")
        self.add_regex("(" + "|".join([num for num in self.NUM_MAP.keys()]) + r")\s?(months|mos|mo\.s)")


class DaysEnding(Ending):
    def __init__(self):
        super().__init__(Ending.DAYS)
        self.add_regex(r"[0-9]+\s?(days)")
