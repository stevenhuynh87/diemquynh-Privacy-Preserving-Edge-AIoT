"""Read-only CSV/schema survey. Never edits source data or assigns labels."""
import argparse
import csv
import io
import math
from pathlib import Path


def survey(root, max_files=20, rows=3000, delimiter=','):
    files = sorted(root.rglob('*.csv'))
    if not root.is_dir():
        raise ValueError(f'Folder does not exist: {root}')
    if not files:
        raise ValueError(f'No CSV found under {root}. Check extraction/path.')
    lines = [f'ROOT: {root.resolve()}', f'CSV FILES: {len(files)}', '', 'CSV PATHS:']
    lines.extend(str(f.relative_to(root)) for f in files)
    falls = [f for f in files if f.name.lower() == 'falls.csv']
    selected = falls + [f for f in files if f not in falls][:max_files]
    for f in selected:
        lines += ['', f'FILE: {f.relative_to(root)}', f'BYTES: {f.stat().st_size}']
        widths, times, invalid = set(), [], 0
        try:
            with f.open(encoding='utf-8-sig', newline='') as handle:
                reader = csv.reader(handle, delimiter=delimiter)
                for i, row in enumerate(reader):
                    if i >= rows:
                        break
                    widths.add(len(row))
                    if i < 4:
                        lines.append(f'ROW {i + 1}: fields={len(row)}, first_8={repr(row[:8])[:650]}')
                    if row:
                        try:
                            value = float(row[0])
                            if not math.isfinite(value):
                                raise ValueError()
                            times.append(value)
                        except ValueError:
                            invalid += 1
            lines += [f'SAMPLED_COLUMN_COUNTS: {sorted(widths)}',
                      f'NUMERIC_FIRST_COLUMN_ROWS: {len(times)}; NONNUMERIC: {invalid}']
            if times:
                lines.append(f'FIRST_COLUMN_RANGE: {min(times)} .. {max(times)}')
            if f in falls:
                lines.append('Falls.csv is a subject-column event table, NOT a sensor-frequency file.')
            if 769 in widths:
                lines.append('769 fields is consistent with timestamp + 768 thermal pixels; verify modality.')
        except (OSError, UnicodeError, csv.Error) as error:
            lines.append(f'ERROR: {error}')
    lines += ['', 'No labels, timestamp units, subject mapping or training status inferred automatically.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path, default=Path('reports/sprint1_schema.txt'))
    parser.add_argument('--max-files', type=int, default=20)
    parser.add_argument('--rows', type=int, default=3000)
    parser.add_argument('--delimiter', default=',')
    args = parser.parse_args()
    if len(args.delimiter) != 1 or args.rows < 1 or args.max_files < 1:
        parser.error('Delimiter must be one character; counts must be positive.')
    try:
        result = survey(args.root, args.max_files, args.rows, args.delimiter)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')
    if args.out.resolve() == args.root.resolve() or args.root.resolve() in args.out.resolve().parents:
        parser.error('Write the report outside the raw-data folder.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(result, encoding='utf-8')
    print(result)
    print(f'REPORT SAVED: {args.out.resolve()}')


if __name__ == '__main__':
    main()
