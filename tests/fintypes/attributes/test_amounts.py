from sfinx.fintypes.attributes.amounts import FinTabAmount
from sfinx.fintypes.components.cell import FinTabCell
from tests.globals import sample_table

parent = FinTabCell(1, 3, sample_table["B4"], [])
cell = FinTabCell(3, 6, sample_table["D6"], [])
cell.metrics_hierarchy = [parent]


def test_amount_scale():
    amount = FinTabAmount(cell)
    assert amount.amount_scale == "millions"


def test_amount_delta():
    amount = FinTabAmount(cell)
    assert amount.fit_for_deltas() is True
