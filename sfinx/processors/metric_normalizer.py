from sfinx.fintypes.metric import FinTabMetric


class FinTabMetricNormalizer:
    """
    Normalizes the metrics in a workbook
    by specifying metric hierarchies and calculating change rates and shares of total.
    """

    def __init__(self, wb):
        self.wb = wb
        self.sheet_to_metrics = {}
        self._populate()
        self._set_change_rates()
        self._set_shares()

    def _populate_sheet_to_metrics(self, sheet_name, metric):
        """
        Keeps track of hierarchy groups in each worksheet.
        :param sheet_name: The name of the worksheet.
        :param metric: A metric represented by a cell.
        :return: Same metric, but abstracted into a FinTabMetric class
        """
        if (sheet_name, metric.key) not in self.sheet_to_metrics:
            self.sheet_to_metrics[(sheet_name, metric.key)] = FinTabMetric(metric.val)
        m = self.sheet_to_metrics[(sheet_name, metric.key)]
        return m

    def _populate(self):
        """
        Merges together groups of metrics that have similar hierarchies.
        Keeps track of different values of the same metric over different periods.
        """
        for sheet_name, sheet in self.wb.sheets.items():
            for coords, cell in sheet.cells.items():
                # Empty cells cannot be part of a hierarchy group.
                if cell.is_empty:
                    continue
                # Cells not attached to a period cannot be part of a hierarchy group.
                if not cell.period:
                    continue
                # Cells that don't have a hierarchy cannot be part of a hierarchy group.
                if not cell.metrics_hierarchy:
                    continue
                # If the cell passes all requirements,
                # ensure that its hierarchy group is recorded in the corresponding worksheet.
                metric = cell.metrics_hierarchy[0]
                m = self._populate_sheet_to_metrics(sheet_name, metric)
                # Also ensure that all sub-metrics in its hierarchy are tracked by super-metrics.
                for metric in cell.metrics_hierarchy[1:]:
                    m = m.add_sub_metric(metric)
                # Finally, ensure that the periods and amounts are aligned for the current metric.
                m.add_period_amount(cell)

    def _set_change_rates(self):
        """
        For all metric groups, calculates period-on-period change rates.
        """
        for sheet_name, metric in self.sheet_to_metrics:
            m = self.sheet_to_metrics[(sheet_name, metric)]
            m.set_change_rates()

    def _set_shares(self):
        """
        For all metric groups, calculates shares of total for each sub-metric.
        """
        for sheet_name, metric in self.sheet_to_metrics:
            m = self.sheet_to_metrics[(sheet_name, metric)]
            m.set_shares()

    def to_json(self):
        """
        Returns json representation of all metrics in the workbook.
        """
        j = []
        for sheet_name, metric in self.sheet_to_metrics:
            ss = [x for x in j if x["sheet_name"] == sheet_name]
            if len(ss) > 0:
                s = ss[0]
            else:
                s = {"sheet_name": sheet_name, "metrics": []}
                j.append(s)
            m = self.sheet_to_metrics[(sheet_name, metric)]
            s["metrics"].append(m.to_json())
        return j

    @staticmethod
    def to_list(j):
        """
        Returns list representation of dictionary object j.
        """
        if "values" in j:
            for val in j["values"]:
                yield [
                    val["period"]["period_expr"],
                    val["period"]["period_start"],
                    val["period"]["period_end"],
                    " ".join(val["period"]["period_flags"]),
                    val["amount"]["row_idx"],
                    val["amount"]["col_idx"],
                    val["amount"]["amount_expr"],
                    val["amount"]["amount_type"],
                    val["amount"]["amount_scale"],
                    val["amount"]["amount_currency"],
                    val["amount"]["pct_share_of_total"] if val["amount"]["pct_share_of_total"] else "",
                ]
        elif "sub_metrics" in j:
            for sub_metric in j["sub_metrics"]:
                vals = list(FinTabMetricNormalizer.to_list(sub_metric))
                for val in vals:
                    yield [j["metric_name"], sub_metric["metric_name"]] + val
        else:
            for metric in j["metrics"]:
                subs = list(FinTabMetricNormalizer.to_list(metric))
                for sub in subs:
                    yield [j["sheet_name"]] + sub

    @staticmethod
    def to_tsv(j):
        """
        Returns tsv representation of dictionary object j.
        """
        l = [list(FinTabMetricNormalizer.to_list(sheet)) for sheet in j]
        max_len = max([len(x) for sheet in l for x in sheet])
        output = (
            "\t".join(
                ["sheet_name", "metric"]
                + ["sub_metric" for x in range(max_len - 13)]
                + [
                    "period_expr",
                    "period_start",
                    "period_end",
                    "period_flags",
                    "row_idx",
                    "col_idx",
                    "amount_expr",
                    "amount_type",
                    "amount_scale",
                    "amount_currency",
                    "pct_share_of_total",
                ]
            )
            + "\n"
        )
        for sheet in l:
            for x in sheet:
                output += (
                    "\t".join(
                        [str(y).replace("\n", " ").replace("\r", " ").replace("\t", " ") for y in x[:-11]]
                        + ["" for x in range(max_len - len(x))]
                        + [str(y).replace("\n", " ").replace("\r", " ").replace("\t", " ") for y in x[-11:]]
                    )
                    + "\n"
                )
        return output
