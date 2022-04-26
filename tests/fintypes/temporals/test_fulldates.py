from src.fintypes.temporals.fulldates import FullDate


def test_full_date():
    d = FullDate.find("Sep 20, 2021")
    assert d is not None
    assert d.year == 2021
    assert d.month == 9
    assert d.day == 20
