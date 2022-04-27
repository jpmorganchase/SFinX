import sys
import argparse
import json
import warnings
from pathlib import Path
from sfinx.fintypes.components.workbook import FinWorkbook
from sfinx.processors.period_normalizer import FinTabPeriodNormalizer
from sfinx.processors.metric_normalizer import FinTabMetricNormalizer

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)

INPUT_EXTENSIONS = ['xlsx']
OUTPUT_EXTENSIONS = ['.tsv', '.json']
my_parser = argparse.ArgumentParser(description='Run SFinX normalizer on input data and store in output.')

# Add the arguments
my_parser.add_argument('--input',
                       '-i',
                       dest='input_path',
                       type=str,
                       help='The path to input file.')

my_parser.add_argument('--output',
                       '-o',
                       dest='output_path',
                       type=str,
                       help='The path to output file.')


def recursive_print_per_sheet(sheet_name, metric, map):
    if len(map) == 0: return False
    for key, val in map.items():
        for period, amount in val.period_to_amount.items():
            if sheet_name == 'Dashboard':
                print(sheet_name, '|', amount.i, '|', amount.j, '|', metric, '|', key, '|', period.expr,
                      period.start_date.strftime('%Y-%m-%d'),
                      period.end_date.strftime('%Y-%m-%d'),
                      amount.amount,
                      amount.share_of_total)
        recursive_print_per_sheet(sheet_name, key, val.name_to_sub_metric)
    return True


def recursive_print(path):
    wb = FinWorkbook(path, from_path=True)
    period_norm = FinTabPeriodNormalizer(wb)  # noqa: F841
    metric_norm = FinTabMetricNormalizer(wb)
    for key, metric in metric_norm.sheet_to_metrics.items():
        recursive_print_per_sheet(key[0], metric.name, metric.name_to_sub_metric)
    return True


def generate_output(input, extension, is_path):
    wb = FinWorkbook(input, from_path=is_path)
    period_norm = FinTabPeriodNormalizer(wb)  # noqa: F841
    metric_norm = FinTabMetricNormalizer(wb)
    j = metric_norm.to_json()
    if extension == '.tsv': j = FinTabMetricNormalizer.to_tsv(j)
    if extension == '.json': j = json.dumps(j)
    return j


def run_from_path(input, output_path):
    j = generate_output(input, output_path.suffix, True)
    with open(output_path, 'w') as f:
        f.write(j)
    return j


if __name__ == "__main__":
    args = my_parser.parse_args()
    input_path = Path(args.input_path)

    if not input_path.exists():
        print(f'The given input path does not exist: {input_path}')
        sys.exit(1)

    output_path = Path(args.output_path)
    output_extension = output_path.suffix
    if output_extension not in OUTPUT_EXTENSIONS:
        print(f'The given file extension "{output_extension}" does not match one of {OUTPUT_EXTENSIONS}')
        sys.exit(1)

    run_from_path(input_path, output_path)
