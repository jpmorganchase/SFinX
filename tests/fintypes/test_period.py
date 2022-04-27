from tests.globals import sample_fin_table
from sfinx.fintypes.period import FinTabPeriod
from datetime import datetime


def test_period():
    cell = sample_fin_table.cells[(5, 4)]
    period, non_headers = FinTabPeriod.get_period({}, "sheet", cell)
    assert period is not None
    assert period.expr.strip() == '2019'

    # The date parser will use the current month/day if it only parses a date
    assert period.start_date.day == datetime.now().day
    assert period.end_date.day == datetime.now().day + 1
    assert len(non_headers) == 4
    assert non_headers[0].val == 'FY 20182'
    assert non_headers[1].val == 'Business performance, $MM'
    assert non_headers[2].val == 'Income Statement'
    assert non_headers[3].val == 'External revenue'
