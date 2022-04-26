from tests.globals import sample_table
from src.fintypes.attributes.valtypes import FinTabValTypes


def test_cell_type():
    assert FinTabValTypes.get_cell_type(sample_table["B2"]) == FinTabValTypes.TEXT
    assert FinTabValTypes.get_cell_type(sample_table["J9"]) == FinTabValTypes.CURRENCY
