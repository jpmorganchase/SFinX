from sfinx.fintypes.temporals.years import *


def test_years():
    txt = "in the year 2016".lower()
    assert FourDigit().get(txt) == 2016
    txt = "Q2'16".lower()
    assert QH2().get(txt) == 2016
    txt = "FYE 2020".lower()
    assert FY4().get(txt) == 2020
    txt = "FY19".lower()
    assert FY2().get(txt) == 2019
