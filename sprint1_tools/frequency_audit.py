"""Timestamp-only audit supporting variable-width radar CSVs. Units are explicit."""
import argparse
import csv
import math
import statistics
from pathlib import Path

SCALE = {'s': 1.0, 'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9}


def audit(path, unit, delimiter=','):
    result = dict(file=str(path), unit=unit, status='ok', rows=0, valid_timestamps=0,
                  first_row_nonnumeric=0, invalid_timestamps=0, blank_rows=0,
                  repeated_timestamps=0, backwards_steps=0, first_timestamp_s='',
                  last_timestamp_s='', median_dt_s='', estimated_hz='', large_gaps=0, error='')
    positive_deltas = []
    previous = None
    try:
        with path.open(encoding='utf-8-sig', newline='') as handle:
            for i, row in enumerate(csv.reader(handle, delimiter=delimiter)):
                result['rows'] += 1
                if not row or not any(cell.strip() for cell in row):
                    result['blank_rows'] += 1
                    continue
                try:
                    timestamp = float(row[0]) * SCALE[unit]
                    if not math.isfinite(timestamp):
                        raise ValueError('non-finite timestamp')
                except ValueError:
                    if i == 0:
                        result['first_row_nonnumeric'] = 1
                    else:
                        result['invalid_timestamps'] += 1
                    continue
                result['valid_timestamps'] += 1
                if result['first_timestamp_s'] == '':
                    result['first_timestamp_s'] = timestamp
                result['last_timestamp_s'] = timestamp
                if previous is not None:
                    delta = timestamp - previous
                    if delta > 0:
                        positive_deltas.append(delta)
                    elif delta == 0:
                        result['repeated_timestamps'] += 1
                    else:
                        result['backwards_steps'] += 1
                previous = timestamp
        if positive_deltas:
            median = statistics.median(positive_deltas)
            result['median_dt_s'] = median
            result['large_gaps'] = sum(d > 1.5 * median for d in positive_deltas)
            if not result['backwards_steps'] and not result['invalid_timestamps']:
                result['estimated_hz'] = 1 / median
        if result['valid_timestamps'] < 3 or not positive_deltas:
            result['status'] = 'insufficient_data'
        elif result['backwards_steps'] or result['invalid_timestamps']:
            result['status'] = 'review_timestamp_errors'
        elif result['repeated_timestamps'] or result['large_gaps'] or result['blank_rows']:
            result['status'] = 'review_irregular_sampling'
    except (OSError, UnicodeError, csv.Error) as error:
        result['status'] = 'error'
        result['error'] = str(error)
        result['estimated_hz'] = ''
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--unit', required=True, choices=SCALE)
    parser.add_argument('--pattern', default='*.csv', help='Restrict to files with the same verified timestamp unit.')
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--out', type=Path, default=Path('reports/frequency_audit_sprint1.csv'))
    args = parser.parse_args()
    if len(args.delimiter) != 1:
        parser.error('Delimiter must be one character.')
    if not args.root.is_dir():
        parser.error('Root folder does not exist.')
    if args.out.resolve() == args.root.resolve() or args.root.resolve() in args.out.resolve().parents:
        parser.error('Write reports outside raw-data folders.')
    files = sorted(f for f in args.root.rglob(args.pattern) if f.is_file() and f.name.lower() != 'falls.csv')
    if not files:
        parser.error('No matching sensor CSV files found.')
    results = [audit(f, args.unit, args.delimiter) for f in files]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    for result in results:
        print(result['file'], 'status=', result['status'], 'Hz=', result['estimated_hz'])
    print('SAVED:', args.out.resolve())
    print('Hz is estimated from the median positive timestamp step, not a hardware rating.')
    print('Large gap = step > 1.5 times the median; inspect flagged recordings before using them.')


if __name__ == '__main__':
    main()
