from openpyxl.styles import numbers
from datetime import datetime


class FinTabValTypes:
    """
    Represents the type of values in a financial table cell.
    """
    DEFAULT = 'default'
    TEXT = 'text'
    INT = 'int'
    CURRENCY = 'currency'
    PERCENT = 'percent'
    BPS = 'bps'
    DATE = 'date'
    FLOAT = 'float'

    FORMAT_MAP = {
        numbers.FORMAT_NUMBER: INT,
        numbers.FORMAT_NUMBER_00: FLOAT,
        numbers.FORMAT_NUMBER_COMMA_SEPARATED1: FLOAT,
        numbers.FORMAT_NUMBER_COMMA_SEPARATED2: FLOAT,
        numbers.FORMAT_PERCENTAGE: PERCENT,
        numbers.FORMAT_PERCENTAGE_00: PERCENT,
        numbers.FORMAT_DATE_YYYYMMDD2: DATE,
        numbers.FORMAT_DATE_YYMMDD: DATE,
        numbers.FORMAT_DATE_DDMMYY: DATE,
        numbers.FORMAT_DATE_DMYSLASH: DATE,
        numbers.FORMAT_DATE_DMYMINUS: DATE,
        numbers.FORMAT_DATE_DMMINUS: DATE,
        numbers.FORMAT_DATE_MYMINUS: DATE,
        numbers.FORMAT_DATE_XLSX14: DATE,
        numbers.FORMAT_DATE_XLSX15: DATE,
        numbers.FORMAT_DATE_XLSX16: DATE,
        numbers.FORMAT_DATE_XLSX17: DATE,
        numbers.FORMAT_DATE_XLSX22: DATE,
        numbers.FORMAT_DATE_DATETIME: DATE,
        numbers.FORMAT_DATE_TIME1: DATE,
        numbers.FORMAT_DATE_TIME2: DATE,
        numbers.FORMAT_DATE_TIME3: DATE,
        numbers.FORMAT_DATE_TIME4: DATE,
        numbers.FORMAT_DATE_TIME5: DATE,
        numbers.FORMAT_DATE_TIME6: DATE,
        numbers.FORMAT_DATE_TIME7: DATE,
        numbers.FORMAT_DATE_TIME8: DATE,
        numbers.FORMAT_DATE_TIMEDELTA: DATE,
        numbers.FORMAT_DATE_YYMMDDSLASH: DATE,
        numbers.FORMAT_CURRENCY_USD_SIMPLE: CURRENCY,
        numbers.FORMAT_CURRENCY_USD: CURRENCY,
        numbers.FORMAT_CURRENCY_EUR_SIMPLE: CURRENCY
    }

    @staticmethod
    def get_cell_type(cell):
        """
        Given a cell from a financial table, returns the type of value stored in the cell.
        :param cell: A cell from a financial table.
        :return: Type of value stored in the cell.
        """
        if cell.number_format and cell.number_format in FinTabValTypes.FORMAT_MAP:
            return FinTabValTypes.FORMAT_MAP[cell.number_format]
        if cell.number_format and '%' in cell.number_format: return FinTabValTypes.PERCENT
        if cell.number_format and '$' in cell.number_format: return FinTabValTypes.CURRENCY
        if cell.number_format and '\\(#' in cell.number_format: return FinTabValTypes.CURRENCY
        if isinstance(cell.value, str) and len(cell.value.strip()) > 0: return FinTabValTypes.TEXT
        if isinstance(cell.value, datetime): return FinTabValTypes.DATE
        if isinstance(cell.value, int): return FinTabValTypes.INT
        if isinstance(cell.value, float): return FinTabValTypes.FLOAT
        return FinTabValTypes.DEFAULT
