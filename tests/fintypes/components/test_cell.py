from tests.globals import sample_table
from sfinx.fintypes.components.cell import FinTabCell


cell1 = FinTabCell(1, 3, sample_table["B4"], [])
cell2 = FinTabCell(3, 3, sample_table["D4"], [])


def test_sub():
    assert cell2.sub(cell1) is True
    assert cell2.equal(cell1) is False


def test_vals():
    assert cell2.is_empty is False
    assert cell2.is_body is True
    assert cell2.is_header is False
