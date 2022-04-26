from datetime import datetime
from src.fintypes.temporals.base import Temporal


class Year(Temporal):
    """
    Represents a calendar year.
    """
    def __init__(self, name, offset):
        super().__init__(name)
        self.offset = offset

    def get(self, text):
        """
        Finds the occurrence of a year in a string
        :param text: input string
        :return: integer representation of the year (if found in text)
        """
        for regex in self.regexes:
            hit = regex.search(text)
            if not hit: continue
            i, j = hit.span()
            start, end = j+self.offset, j
            o = int(text[start:end])
            if end-start >= 4: return o
            if o <= int(str(datetime.now().year)[:-2]): o += 2000
            else: o += 1900
            return o
        return None

    @staticmethod
    def find(text, years):
        """
        Finds the occurrence of a year in a string
        :param text: input string
        :param years: a list of Year objects to consider
        :return: integer representation of the year expressed in text (or None)
        """
        for year in years:
            idx = year.get(text)
            if idx: return idx
        return None


class FourDigit(Year):
    """
    Represents a four digit expression of year such as 1946 or 2001.
    """
    def __init__(self):
        super().__init__("FourDigit", -4)
        self.add_regex(r"\b[1-9][0-9]{3}\b")


class QH4(Year):
    """
    Represents a quarter or half-year period expressed as 2Q2019 or 1H'95.
    """
    def __init__(self):
        super().__init__("QH", -4)
        self.add_regex(r"[qh'.\-][1-9][0-9]{3}\b")


class QH2(Year):
    """
    Represents a quarter or half-year period expressed as 2Q2019 or 1H'95.
    """
    def __init__(self):
        super().__init__("QH", -2)
        self.add_regex(r"[qh'.\-][0-9]{2}\b")


class FY4(Year):
    """
    Represents a four digit representation preceded by FY or FYE, e.g. FY2014.
    """
    def __init__(self):
        super().__init__("FY4", -4)
        self.add_regex(r"(fy|fye)['.\-\s]?[1-9][0-9]{3}\b")


class FY2(Year):
    """
    Represents a two digit representation preceded by FY or FYE, e.g. FY'14.
    """
    def __init__(self):
        super().__init__("FY2", -2)
        self.add_regex(r"(fy|fye)['.\-\s]?[0-9]{2}\b")
