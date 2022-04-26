from src.fintypes.temporals.semis import *


def test_semis():
    text = "2H 2016".lower()
    assert H1().get(text) is None
    assert H2().get(text) is 2


def test_semi_period():
    begin, end = Semi.get_semiannual_period(2016, 2)
    assert begin.year == 2016
    assert begin.month == 7
    assert begin.day == 1
    assert end.year == 2017
    assert end.month == 1
    assert end.day == 1
