from enum import Enum
from sfinx.fintypes.attributes.valtypes import FinTabValTypes
from sfinx.fintypes.temporals.years import *
from sfinx.fintypes.temporals.semis import *
from sfinx.fintypes.temporals.quarters import *
from sfinx.fintypes.temporals.ending import *
from sfinx.fintypes.temporals.months import *
from sfinx.fintypes.temporals.fulldates import *


class FinTabPeriod:
    class IS(Enum):
        YEAR = 1
        SEMI = 2
        QUARTER = 3
        MONTH = 4
        WEEK = 5
        DAY = 6
        NA = 7

    YEARS = [FourDigit(), QH4(), QH2(), FY4(), FY2()]
    SEMIS = [H1(), H2()]
    QUARTERS = [Q1(), Q2(), Q3(), Q4()]
    ENDING_PERIODS = [MonthsEnding(), DaysEnding()]
    MONTHS = [Jan(), Feb(), Mar(), Apr(), May(), Jun(), Jul(), Aug(), Sep(), Oct(), Nov(), Dec()]

    def __init__(self, expr, start_date, end_date, flags):
        self.expr = expr
        self.start_date = start_date
        self.end_date = end_date
        self.flags = flags
        self.occurrence_range = []

    def __hash__(self):
        return self.expr.__hash__()

    def __eq__(self, other):
        if not isinstance(other, FinTabPeriod): return False
        return self.expr == other.expr and self.start_date == other.start_date and self.end_date == other.end_date

    def __ne__(self, other):
        if not isinstance(other, FinTabPeriod): return True
        return not self.__eq__(other)

    def __ge__(self, other):
        if not isinstance(other, FinTabPeriod): return False
        return self.end_date >= other.end_date

    def __gt__(self, other):
        if not isinstance(other, FinTabPeriod): return False
        return self.end_date > other.end_date

    def __le__(self, other):
        if not isinstance(other, FinTabPeriod): return False
        return self.end_date <= other.end_date

    def __lt__(self, other):
        if not isinstance(other, FinTabPeriod): return False
        return self.end_date < other.end_date

    def __str__(self):
        return self.expr

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return {
            'period_expr': self.expr,
            'period_start': self.start_date.strftime('%Y-%m-%d'),
            'period_end': self.end_date.strftime('%Y-%m-%d'),
            'period_flags': self.flags
        }

    @staticmethod
    def _get_period_from_cached(curr_map, sheet_name, headers):
        """
        Loads cached periods instead of recalculating them.
        :param curr_map: A map that links specific headers in the current worksheet to their corresponding period.
        :param sheet_name: Name of the current worksheet
        :param headers: Set of headers that might include an expression of period in them.
        :return: The headers split into period and non period groups
        """
        cached = {i for i, h in enumerate(headers) if (sheet_name, h.i, h.j) in curr_map}
        header_coords = [(h.i, h.j) for h in headers]
        if len(cached) <= 0: return None, None
        c = next(iter(cached))
        period = curr_map[(sheet_name, headers[c].i, headers[c].j)]
        for coords in period.occurrence_range:
            if coords not in header_coords: return None, None
        non_periods = [headers[i] for i in range(len(headers)) if i not in cached]
        return period, non_periods

    @staticmethod
    def construct_period(sheet_name, curr_map, string, start, end, period_indices, flags, non_periods):
        """
        Constructs the period object for a given header string.
        :param sheet_name: Name of the worksheet.
        :param curr_map: Map of cached periods.
        :param string: Period expression within the header.
        :param start: Start date of the period.
        :param end: End date of the period.
        :param period_indices: Indices of substrings that construct the period expression.
        :param flags: Flags associated with the header.
        :param non_periods: Substrings within the header that do not correspond to the period.
        :return: FinTabPeriod object representing the period expression in the string.
        """
        p = FinTabPeriod(string, start, end, flags)
        p.occurrence_range = period_indices
        for i, j in period_indices:  curr_map[(sheet_name, i, j)] = p
        return p, non_periods

    @staticmethod
    def get_period(curr_map, sheet_name, cell):
        """
        Extracts the period expression from the headers of the given cell.
        :param curr_map: A map that keep track of all headers and their corresponding periods.
        :param sheet_name: The name of the current worksheet.
        :param cell: A cell in the current worksheet.
        :return: A tuple where:
        the first element is a FinTabPeriod object representing the period expressed in the headers of the cell, and
        the second element is the indices of all substrings in the headers that do not express any periods.
        """
        row_headers = cell.row_header if cell.row_header else []
        col_headers = cell.col_header if cell.col_header else []
        headers = col_headers + row_headers

        # If period has already been identified in the headers, return the cached version
        period, non_periods = FinTabPeriod._get_period_from_cached(curr_map, sheet_name, headers)
        if period: return period, non_periods

        # Split headers into segments that include period expressions and segments that don't
        tagged = [(h, (sheet_name, h.i, h.j) in curr_map, Temporal.has_period_expr(h, FinTabPeriod.MONTHS)) for h in headers]
        periods = [h[0] for h in tagged if h[1] or h[2]]
        period_indices = [(h.i, h.j) for h in periods]
        flags = [f for h in periods for f in h.flags]
        non_periods = [h[0] for h in tagged if not h[1] and not h[2]]

        # Extract all relevant temporal expressions from the segments expressing periods
        date, year, quarter, semi, ended, month = None, None, None, None, None, None
        st = ''
        for header in periods:
            if header.val_type == FinTabValTypes.DATE:
                date = header.val
                # FIXME: use s.number_format instead
                st += ' ' + header.val.strftime('%b-%y')
            else:
                s = header.val.lower().replace('mtd', '').replace('ytd', '')
                st += ' ' + header.val
                if not year: year = Year.find(s, FinTabPeriod.YEARS)
                if not quarter: quarter = Quarter.find(s, FinTabPeriod.QUARTERS)
                if not semi: semi = Semi.find(s, FinTabPeriod.SEMIS)
                if not ended: ended = Ending.find(s, FinTabPeriod.ENDING_PERIODS)
                if not month: month = Month.find(s, FinTabPeriod.MONTHS)
                if not date and not quarter and not semi: date = FullDate.find(s)
        if ended and date:  # "3 months/days ending 9/30/2020"
            return FinTabPeriod.construct_period(sheet_name, curr_map, st, date+ended, date+relativedelta(days=1),
                                                 period_indices, flags, non_periods)
        if quarter and year:  # "Q1 2020"
            start, end = Quarter.get_quarterly_period(year, quarter)
            return FinTabPeriod.construct_period(sheet_name, curr_map, st, start, end,
                                                 period_indices, flags, non_periods)
        if semi and year:  # "1H 2020"
            start, end = Semi.get_semiannual_period(year, semi)
            return FinTabPeriod.construct_period(sheet_name, curr_map, st, start, end,
                                                 period_indices, flags, non_periods)
        if month and year:  # "Jan 2020"
            if not date or year != date.year or month != date.month:
                start = datetime(year, month, 1)
                return FinTabPeriod.construct_period(sheet_name, curr_map, st, start, start + relativedelta(months=1),
                                                     period_indices, flags, non_periods)
        if date:  # "1/1/2020"
            return FinTabPeriod.construct_period(sheet_name, curr_map, st, date, date + relativedelta(days=1),
                                                 period_indices, flags, non_periods)
        if year:  # "2020"
            return FinTabPeriod.construct_period(sheet_name, curr_map, st, datetime(year, 1, 1), datetime(year+1, 1, 1),
                                                 period_indices, flags, non_periods)
        return None, headers


class FinTabDerivedPeriod:
    """
    Represents a derived period, e.g. quarter-on-quarter periods calculated based on two adjacent columns.
    """
    def __init__(self, expr, start_date, end_date, flags, occurrence_range):
        self.expr = expr
        self.start_date = start_date
        self.end_date = end_date
        self.flags = flags
        self.occurrence_range = occurrence_range

    def __hash__(self):
        return self.expr.__hash__()

    def __eq__(self, other):
        if not isinstance(other, FinTabDerivedPeriod): return False
        return self.expr == other.expr and self.start_date == other.start_date and self.end_date == other.end_date

    def __ne__(self, other):
        if not isinstance(other, FinTabDerivedPeriod): return True
        return not self.__eq__(other)

    @staticmethod
    def calculate(amount1, period1, amount2, period2):
        """
        Provided with two amounts and corresponding periods, calculates the period-on-period span as a period object.
        If the two amounts don't correspond in type, returns None.
        """
        # If the two periods are the same, no period-on-period deltas can be calculated.
        if period1 == period2: return None
        # If the amount types are not the same, no period-on-period deltas can be calculated.
        if amount1.amount_type != amount2.amount_type: return None
        # Check to ensure type of amount is suitable for delta calculation.
        if not amount1.fit_for_deltas(): return None
        # Determine which period comes first.
        if period1 < period2: a1, p1, a2, p2 = amount1, period1, amount2, period2
        else: a1, p1, a2, p2 = amount2, period2, amount1, period2  # noqa: F841
        # Calculate the period-on-period span and create a new derived period object.
        return FinTabDerivedPeriod(p1.expr + ' to ' + p2.expr + ' delta [derived]',
                                   p1.start_date, p2.end_date,
                                   p1.flags + p2.flags,
                                   p1.occurrence_range + p2.occurrence_range)

    def to_json(self):
        """
        Returns json representation of self.
        """
        return {
            'period_expr': self.expr,
            'period_start': self.start_date.strftime('%Y-%m-%d'),
            'period_end': self.end_date.strftime('%Y-%m-%d'),
            'period_flags': self.flags
        }
