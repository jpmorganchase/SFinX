from tests.globals import sample_fin_table
from src.fintypes.period import FinTabPeriod


def test_period():
    cell = sample_fin_table.cells[(5, 4)]
    period, non_headers = FinTabPeriod.get_period({}, "sheet", cell)
    assert period is not None
    assert period.expr.strip() == '2019'
    assert period.start_date.day == 23
    assert period.end_date.day == 24
    assert len(non_headers) == 4
    assert non_headers[0].val == 'FY 20182'
    assert non_headers[1].val == 'Business performance, $MM'
    assert non_headers[2].val == 'Income Statement'
    assert non_headers[3].val == 'External revenue'
