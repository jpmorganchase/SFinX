from sfinx.fintypes.temporals.base import Temporal


class Month(Temporal):
    """
    Represents one of the  twelve months in the year.
    """
    def __init__(self, name, index):
        super().__init__(name)
        self.index = index

    def get(self, text):
        """
        Finds the occurrence of a month in a string
        :param text: input string
        :return: index of the month expressed in text (or None)
        """
        for regex in self.regexes:
            hit = regex.search(text)
            if hit: return self.index
        return None

    @staticmethod
    def find(text, months):
        """
        Finds the occurrence of a month in a string
        :param text: input string
        :param months: a list of month objects to consider
        :return: index of the month expressed in text (or None)
        """
        for month in months:
            idx = month.get(text)
            if idx: return idx
        return None


class Jan(Month):
    def __init__(self):
        super().__init__("Jan", 1)
        self.add_regex(r"\bjan(uary)?\b")


class Feb(Month):
    def __init__(self):
        super().__init__("Feb", 2)
        self.add_regex(r"\bfeb(uary)?\b")


class Mar(Month):
    def __init__(self):
        super().__init__("Mar", 3)
        self.add_regex(r"\bmar(ch)?\b")


class Apr(Month):
    def __init__(self):
        super().__init__("Apri", 4)
        self.add_regex(r"\bapr(il)?\b")


class May(Month):
    def __init__(self):
        super().__init__("May", 5)
        self.add_regex(r"\bmay\b")


class Jun(Month):
    def __init__(self):
        super().__init__("Jun", 6)
        self.add_regex(r"\bjune?\b")


class Jul(Month):
    def __init__(self):
        super().__init__("Jul", 7)
        self.add_regex(r"\bjuly?\b")


class Aug(Month):
    def __init__(self):
        super().__init__("Aug", 8)
        self.add_regex(r"\baug(ust)?\b")


class Sep(Month):
    def __init__(self):
        super().__init__("Sep", 9)
        self.add_regex(r"\bsept?(ember)?\b")


class Oct(Month):
    def __init__(self):
        super().__init__("Oct", 10)
        self.add_regex(r"\boct(ober)?\b")


class Nov(Month):
    def __init__(self):
        super().__init__("Nov", 11)
        self.add_regex(r"\bnov(ember)?\b")


class Dec(Month):
    def __init__(self):
        super().__init__("Dec", 12)
        self.add_regex(r"\bdec(ember)?\b")
