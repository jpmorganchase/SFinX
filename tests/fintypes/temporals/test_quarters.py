from src.fintypes.temporals.quarters import *


def test_quarter():
    txt = "Qtr3 2019".lower()
    assert Q1().get(txt) is None
    assert Q3().get(txt) == 3


def test_quarterly_period():
    begin, end = Quarter.get_quarterly_period(2019, 3)
    assert begin.year == 2019
    assert begin.month == 7
    assert begin.day == 1
    assert end.year == 2019
    assert end.month == 10
    assert end.day == 1
