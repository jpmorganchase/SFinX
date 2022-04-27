from datetime import datetime

from sfinx.fintypes.temporals.base import Temporal


class Semi(Temporal):
    """
    Represents one of semi-annual periods.
    """

    def __init__(self, name, index):
        super().__init__(name)
        self.index = index

    def get(self, text):
        """
        Finds the occurrence of a semi-annual period in a string
        :param text: input string
        :return: index of semi-annual period expressed in text (or None)
        """
        for regex in self.regexes:
            hit = regex.search(text)
            if hit:
                return self.index
        return None

    @staticmethod
    def find(text, semis):
        """
        Finds the occurrence of a semi-annual period in a string
        :param text: input string
        :param semis: a list of Semi objects to consider.
        :return: index of the semi-annual period expressed in text (or None)
        """
        for semi in semis:
            idx = semi.get(text)
            if idx:
                return idx
        return None

    @staticmethod
    def get_semiannual_period(year, half):
        """
        Converts a year and half-year pair into calendar dates
        :param year: An integer representation of a year (e.g. 2009 or 1895)
        :param half: A half-year (1 or 2).
        :return: A tuple representing the start and end dates on the calendar
        """
        # FIXME: needs to accommodate year end pair
        if half == 2:
            return datetime(year, 7, 1), datetime(year + 1, 1, 1)
        if half == 1:
            return datetime(year, 1, 1), datetime(year, 7, 1)
        return None, None


class H1(Semi):
    def __init__(self):
        super().__init__("H1", 1)
        self.add_regex(r"\b(first half|1st half|1h|1-h|h1|h-1)")


class H2(Semi):
    def __init__(self):
        super().__init__("H2", 2)
        self.add_regex(r"\b(second half|2nd half|last half|2h|2-h|h2|h-2)")
