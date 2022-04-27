from sfinx.fintypes.temporals.base import Temporal
from sfinx.fintypes.period import FinTabPeriod
from sfinx.fintypes.components.cell import FinTabHeader
from sfinx.fintypes.attributes.valtypes import FinTabValTypes


def test_temporal_expr():
    t = Temporal("base")
    header = FinTabHeader(0, 0, "test", FinTabValTypes.DATE, None, [])
    assert t.has_period_expr(header, FinTabPeriod.MONTHS) is True
    header = FinTabHeader(0, 0, "january is here", FinTabValTypes.DEFAULT, None, [])
    assert t.has_period_expr(header, FinTabPeriod.MONTHS) is True
    header = FinTabHeader(0, 0, "2q 1999", FinTabValTypes.TEXT, None, [])
    assert t.has_period_expr(header, FinTabPeriod.MONTHS) is True
    header = FinTabHeader(0, 0, "May-20", FinTabValTypes.TEXT, None, [])
    assert t.has_period_expr(header, FinTabPeriod.MONTHS) is True
    header = FinTabHeader(0, 0, "this is not a date", FinTabValTypes.TEXT, None, [])
    assert t.has_period_expr(header, FinTabPeriod.MONTHS) is False
