from tests.globals import sample_toc
from src.fintypes.attributes.colors import FinTabColors


def test_cell_font_color_hex():
    cell = sample_toc["B6"]
    assert FinTabColors.get_cell_font_color_hex(cell) == '00FFFFFF'


def test_cell_fill_color_hex():
    cell = sample_toc["B13"]
    assert FinTabColors.get_cell_fill_color_hex(cell) == 'FF644C76'
