from collections import OrderedDict
from sfinx.fintypes.attributes.amounts import FinTabAmount, FinTabDerivedAmount
from sfinx.fintypes.attributes.currencies import FinTabCurrency
from sfinx.fintypes.attributes.scales import FinTabScale
from sfinx.fintypes.attributes.valtypes import FinTabValTypes
from sfinx.fintypes.period import FinTabDerivedPeriod


class FinTabMetric:
    """
    Represents a financial metric expressed in one or more cells.
    """

    def __init__(self, name):
        self.name = name
        self.name_to_sub_metric = {}
        self.period_to_amount = OrderedDict()

    def add_sub_metric(self, sub):
        """
        Adds a new sub-metric to the map that keeps track of sub-metrics.
        :param sub: Sub-metric as a cell object.
        :return: Sub-metric as a FinTabMetric object.
        """
        if sub.key not in self.name_to_sub_metric:
            self.name_to_sub_metric[sub.key] = FinTabMetric(sub.val)
        return self.name_to_sub_metric[sub.key]

    def add_period_amount(self, cell):
        self.period_to_amount[cell.period] = FinTabAmount(cell)

    def set_delta(self, amount1, amount2, period):
        """
        Provided with two amounts that correspond to the same period, calculates the raw delta over that period.
        """
        derived_cell = FinTabDerivedAmount(amount2.amount - amount1.amount,
                                           amount1.amount_type,
                                           amount1.amount_scale,
                                           amount1.amount_currency)
        self.period_to_amount[period] = derived_cell

    def set_pct_delta(self, amount1, period1, amount2, period2):
        """
        Provided with two amounts over two periods, calculates the period-on-period change%.
        """
        derived_period = FinTabDerivedPeriod(period1.expr + ' to ' + period2.expr + ' delta% [derived]',
                                             period1.start_date, period2.end_date,
                                             period1.flags + period2.flags,
                                             period1.occurrence_range + period2.occurrence_range)
        derived_cell = FinTabDerivedAmount(((amount2.amount - amount1.amount) * 100.0 / amount1.amount)
                                           if amount1.amount != 0.0 else 0.0,
                                           FinTabValTypes.PERCENT,
                                           FinTabScale.DEFAULT,
                                           FinTabCurrency.DEFAULT)
        self.period_to_amount[derived_period] = derived_cell

    def set_bps_delta(self, amount1, period1, amount2, period2):
        """
        Provided with two amounts over two periods, calculates the period-on-period change in basis-points.
        """
        derived_period = FinTabDerivedPeriod(period1.expr + ' to ' + period2.expr + ' delta(BPS) [derived]',
                                             period1.start_date, period2.end_date,
                                             period1.flags + period2.flags,
                                             period1.occurrence_range + period2.occurrence_range)
        derived_cell = FinTabDerivedAmount(int((amount2.amount - amount1.amount) * 10000 / amount1.amount)
                                           if amount1.amount != 0.0 else 0,
                                           FinTabValTypes.BPS,
                                           FinTabScale.DEFAULT,
                                           FinTabCurrency.DEFAULT)
        self.period_to_amount[derived_period] = derived_cell

    def set_change_rates(self):
        items = [(period, amount) for period, amount in self.period_to_amount.items()]
        item_pairs = [(items[i], items[i+1]) for i in range(0, len(items)-1)]
        for (period1, amount1), (period2, amount2) in item_pairs:
            # For any pair of adjacent cells, calculate period-on-period deltas, if appropriate.
            derived_period = FinTabDerivedPeriod.calculate(amount1, period1, amount2, period2)
            if derived_period is None: continue
            # Set the raw delta
            self.set_delta(amount1, amount2, derived_period)
            # Set the percentage change
            self.set_pct_delta(amount1, period1, amount2, period2)
            # Set the bps change
            self.set_bps_delta(amount1, period1, amount2, period2)
        # recurse over other sub-metrics
        for smn, sm in self.name_to_sub_metric.items():
            sm.set_change_rates()

    def set_shares(self):
        """
        Calculates shares of totals for a series of metrics that add to a total.
        """
        # first, group the sub-metrics by their period and amount type
        period_amount_type_to_amount = {}
        for smn, sm in self.name_to_sub_metric.items():
            # purge any totals from each group
            if 'total' in smn.lower(): continue
            for period, amount in sm.period_to_amount.items():
                # skip over derived periods
                if '[derived]' in period.expr: continue
                # skip over percentages--they already reflect shares
                if amount.amount_type == FinTabValTypes.PERCENT: continue
                # get the proper amount type (integers and floats are treated the same as currencies)
                if amount.fit_for_deltas(): at = FinTabValTypes.CURRENCY
                else: at = amount.amount_type
                # populate the map that tracks periods, amount types and amounts
                l = period_amount_type_to_amount.get((period, at), [])
                l.append(amount)
                period_amount_type_to_amount[(period, amount.amount_type)] = l
        # next, calculate totals
        for key, l in period_amount_type_to_amount.items():
            if len(l) == 0: continue
            total = sum([x.amount for x in l])
            for x in l:
                # then, calculate the share for each metric and add it as derived data
                share = (x.amount * 100.0 / total) if total != 0.0 else 0.0
                x.share_of_total = share
        # lastly, recurse over sub-metrics
        for smn, sm in self.name_to_sub_metric.items():
            sm.set_shares()

    def to_json(self):
        """
        Returns json representation of self.
        """
        j = {'metric_name': self.name}
        if len(self.period_to_amount) > 0:
            j['values'] = []
            for period, amount in self.period_to_amount.items():
                j['values'].append({'period': period.to_json(), 'amount': amount.to_json()})
        if len(self.name_to_sub_metric) > 0:
            j['sub_metrics'] = []
            for smn, sm in self.name_to_sub_metric.items():
                j['sub_metrics'].append(sm.to_json())
        return j
