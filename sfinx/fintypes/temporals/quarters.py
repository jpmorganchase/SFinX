from datetime import datetime
from sfinx.fintypes.temporals.base import Temporal


class Quarter(Temporal):
    """
    Represents one of four quarters in the year.
    """
    def __init__(self, name, index):
        super().__init__(name)
        self.index = index

    def get(self, text):
        """
        Finds the occurrence of a quarter in a string
        :param text: input string
        :return: index of the quarter expressed in text (or None)
        """
        for regex in self.regexes:
            hit = regex.search(text)
            if hit: return self.index
        return None

    @staticmethod
    def find(text, quarters):
        """
        Finds the occurrence of a quarter in a string
        :param text: input string
        :param quarters: a list of quarter objects to consider
        :return: index of the quarter expressed in text (or None)
        """
        # TODO: need to add other variants such as Q1-3 or first two quarters
        for quarter in quarters:
            idx = quarter.get(text)
            if idx: return idx
        return None

    @staticmethod
    def get_quarterly_period(year, qtr):
        """
        Converts a year and quarter pair into calendar dates
        :param year: An integer representation of a year (e.g. 2009 or 1895)
        :param qtr: A quarter index (1 or 2 or 3 or 4).
        :return: A tuple representing the start and end dates on the calendar
        """
        # FIXME: needs to accommodate year end pair
        if qtr == 4: return datetime(year, 10, 1), datetime(year+1, 1, 1)
        if qtr == 3: return datetime(year, 7, 1), datetime(year, 10, 1)
        if qtr == 2: return datetime(year, 4, 1), datetime(year, 7, 1)
        if qtr == 1: return datetime(year, 1, 1), datetime(year, 4, 1)
        return None, None


class Q1(Quarter):
    def __init__(self):
        super().__init__("Q1", 1)
        self.add_regex(r"\b(first q|first quarter|first qtr|1st q|1st quarter|1st qtr|1qtr|1 qtr|qtr1|qtr 1|1q|q1|1 q|q 1|1-q|q-1)")


class Q2(Quarter):
    def __init__(self):
        super().__init__("Q2", 2)
        self.add_regex(r"\b(second q|second quarter|second qtr|2nd q|2nd quarter|2nd qtr|2qtr|2 qtr|qtr2|qtr 2|2q|q2|2 q|q 2|2-q|q-2)")


class Q3(Quarter):
    def __init__(self):
        super().__init__("Q3", 3)
        self.add_regex(r"\b(third q|third quarter|third qtr|3rd q|3rd quarter|3rd qtr|3qtr|3 qtr|qtr3|qtr 3|3q|q3|3 q|q 3|3-q|q-3)")


class Q4(Quarter):
    def __init__(self):
        super().__init__("Q4", 4)
        self.add_regex(r"\b(fourth q|fourth quarter|fourth qtr|last q|last quarter|last qtr|4th q|4th quarter|4th qtr|4qtr|4 qtr|qtr4|qtr 4|4q|q4|4 q|q 4|4-q|q-4)")