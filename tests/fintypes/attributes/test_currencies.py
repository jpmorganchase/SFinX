from tests.globals import sample_table
from sfinx.fintypes.components.cell import FinTabCell
from sfinx.fintypes.attributes.currencies import FinTabCurrency


def test_scale():
    parent = FinTabCell(1, 3, sample_table["B4"], [])
    cell = FinTabCell(3, 6, sample_table["D6"], [])
    cell.metrics_hierarchy = [parent]
    assert FinTabCurrency.find(cell) == FinTabCurrency.USD
