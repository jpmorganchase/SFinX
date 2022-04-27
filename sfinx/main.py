import os
import sys
import argparse
import json
from sfinx.fintypes.components.workbook import FinWorkbook
from sfinx.processors.period_normalizer import FinTabPeriodNormalizer
from sfinx.processors.metric_normalizer import FinTabMetricNormalizer

INPUT_EXTENSIONS = ['xlsx', 'csv', 'tsv', 'txt', 'html', 'htm']
OUTPUT_EXTENSIONS = ['tsv', 'json']
my_parser = argparse.ArgumentParser(description='Run SFinX normalizer on input data and store in output.')

# Add the arguments
my_parser.add_argument('-input',
                       '--i',
                       dest='input_path',
                       type=str,
                       help='The path to input file.')

my_parser.add_argument('-input-extension',
                       '--e',
                       dest='input_extension',
                       type=str,
                       default='xlsx',
                       help='The extension of the input file (can be xlsx, csv, tsv, txt, or html).')

my_parser.add_argument('-output-extension',
                       '--t',
                       dest='output_extension',
                       type=str,
                       default='tsv',
                       help='The extension of the output file (can be tsv or json).')

my_parser.add_argument('-output',
                       '--o',
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
    period_norm = FinTabPeriodNormalizer(wb)
    metric_norm = FinTabMetricNormalizer(wb)
    for key, metric in metric_norm.sheet_to_metrics.items():
        recursive_print_per_sheet(key[0], metric.name, metric.name_to_sub_metric)
    return True


def generate_output(input, extension, is_path):
    wb = FinWorkbook(input, from_path=is_path)
    period_norm = FinTabPeriodNormalizer(wb)
    metric_norm = FinTabMetricNormalizer(wb)
    j = metric_norm.to_json()
    if extension == 'tsv': j = FinTabMetricNormalizer.to_tsv(j)
    if extension == 'json': j = json.dumps(j)
    return j


def run_from_path(input, extension, output_path):
    j = generate_output(input, extension, True)
    with open(output_path, 'w') as f:
        f.write(j)
    return j


if __name__ == "__main__":
    args = my_parser.parse_args()
    input_path = args.input_path
    if not os.path.exists(input_path):
        print('The input path specified does not exist:', input_path)
        sys.exit()
    input_extension = args.input_extension.lower()
    if input_extension not in INPUT_EXTENSIONS:
        print('You are only allowed to use one of these file extensions:', INPUT_EXTENSIONS)
        sys.exit()
    output_extension = args.output_extension.lower()
    if output_extension not in OUTPUT_EXTENSIONS:
        print('You are only allowed to save as one of these extensions:', OUTPUT_EXTENSIONS)
        sys.exit()
    output_path = args.output_path
    run_from_path(input_path, output_extension, output_path)
