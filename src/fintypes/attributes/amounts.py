from src.fintypes.attributes.currencies import FinTabCurrency
from src.fintypes.attributes.scales import FinTabScale
from src.fintypes.attributes.valtypes import FinTabValTypes


class FinTabAmount:
    """
    Represents the amount of value mentioned in a table cell as well as attributes
    such as currency and scale.
    """
    def __init__(self, cell):
        self.i = cell.i
        self.j = cell.j
        self.amount = cell.val
        self.amount_type = cell.val_type
        self.amount_scale = FinTabScale.find(cell)
        self.amount_currency = FinTabCurrency.find(cell)
        if self.amount_scale != FinTabScale.DEFAULT or self.amount_currency != FinTabCurrency.DEFAULT:
            self.amount_type = FinTabValTypes.CURRENCY
        self.share_of_total = None

    def fit_for_deltas(self):
        """
        Indicates whether the type of amount is suitable for a delta calculation.
        Only currencies, integers and floating point numbers can be used for delta calculation.
        """
        return self.amount_type in [FinTabValTypes.CURRENCY, FinTabValTypes.INT, FinTabValTypes.FLOAT]

    def to_json(self):
        return {
            'row_idx': self.i,
            'col_idx': self.j,
            'amount_expr': self.amount,
            'amount_type': self.amount_type,
            'amount_scale': self.amount_scale,
            'amount_currency': self.amount_currency,
            'pct_share_of_total': self.share_of_total
        }


class FinTabDerivedAmount:
    """
    Represents derived amounts calculated for a series of table cells,
    such as pct shares of total.
    """
    def __init__(self, amount, amount_type, amount_scale, amount_currency):
        self.amount = amount
        self.i = -1
        self.j = -1
        self.amount_type = amount_type
        self.amount_scale = amount_scale
        self.amount_currency = amount_currency
        self.share_of_total = None

    def to_json(self):
        return {
            'row_idx': self.i,
            'col_idx': self.j,
            'amount_expr': self.amount,
            'amount_type': self.amount_type,
            'amount_scale': self.amount_scale,
            'amount_currency': self.amount_currency,
            'pct_share_of_total': self.share_of_total
        }
