from sfinx.fintypes.temporals.months import *


def test_months():
    txt = "Nov 12, 2020".lower()
    assert Sep().get(txt) is None
    assert Nov().get(txt) == 11
