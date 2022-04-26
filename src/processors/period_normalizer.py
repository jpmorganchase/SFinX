from src.fintypes.period import FinTabPeriod


class FinTabPeriodNormalizer:
    def __init__(self, workbook):
        self.wb = workbook
        self.header_to_period_map = {}
        self._set_periods_and_hierarchy()

    def _set_periods_and_hierarchy(self):
        for sheet_name, sheet in self.wb.sheets.items():
            for coords, cell in sheet.cells.items():
                if not cell.is_empty:
                    period, hierarchy = \
                        FinTabPeriod.get_period(self.header_to_period_map, sheet_name, cell)
                    cell.period = period
                    cell.metrics_hierarchy = hierarchy
