import dateparser
from src.fintypes.temporals.base import Temporal


class FullDate(Temporal):
    """
    Represents a full date expression.
    """
    def __init__(self):
        super().__init__(self.__name__)

    @staticmethod
    def find(text):
        """
        Finds the occurrence of a date in a string
        :param text: input string
        :return: full expression of date in text, if present (or None)
        """
        t = dateparser.parse(text)
        if t: return t
        return None
