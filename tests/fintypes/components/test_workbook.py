from tests.globals import sample_wb


def test_num_sheets():
    assert len(sample_wb.sheets) == 13
