from tests.globals import sample_metric_norm


def test_metric():
    for s, m in sample_metric_norm.sheet_to_metrics.items():
        if s[0] == 'ON segment accounts' and m.name == 'Revenue':
            deltas = [(p.expr.replace('\n', ' ').replace('  ', ' '), a.amount) for p, a in m.period_to_amount.items()]
            deltas = [x for x in deltas if 'FY 2019 to Q3 2020 delta [derived]' in x[0].strip()]
            assert len(deltas) == 1
            assert deltas[0][1] == -407.0
