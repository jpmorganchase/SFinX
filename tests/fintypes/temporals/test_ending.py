from sfinx.fintypes.temporals.ending import DaysEnding, MonthsEnding


def test_months_ending():
    m = MonthsEnding()
    d = m.get("Three months ended September 30, 2021".lower())
    assert d is not None
    assert d.months == -3


def test_days_ending():
    m = DaysEnding()
    d = m.get("90 days ending September 30, 2021".lower())
    assert d is not None
    assert d.days == -90
