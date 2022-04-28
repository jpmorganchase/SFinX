from enum import Enum


class FinTabStyles(Enum):
    """
    Represents the alignment style of a cell in a financial table.
    """

    NORMAL = 1
    HORIZONTAL_ALIGNMENT_LEFT = 2
    HORIZONTAL_ALIGNMENT_CENTER = 3
    HORIZONTAL_ALIGNMENT_RIGHT = 4
