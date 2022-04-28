from tests.globals import sample_fin_table


def test_headers():
    cell = sample_fin_table.cells[(5, 4)]
    rh = cell.row_header
    ch = cell.col_header
    assert len(rh) == 3
    assert rh[0].val == "Business performance, $MM"
    assert rh[1].val == "Income Statement"
    assert rh[2].val == "External revenue"
    assert len(ch) == 2
    assert ch[0].val == "2019"
    assert ch[1].val == "FY 20182"
