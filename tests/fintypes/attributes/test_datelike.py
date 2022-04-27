from tests.globals import sample_cell, sample_cell_i, sample_cell_j, sample_table
from sfinx.fintypes.attributes.datelike import Datelike


def test_datelike():
    d = Datelike(sample_table, sample_cell_i, sample_cell_j, sample_cell)
    f = d.convert_datelike_cell(set())
    assert f is True
