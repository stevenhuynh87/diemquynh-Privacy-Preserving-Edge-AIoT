import argparse
import csv
import io
import struct
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path, help="Folder containing UR Fall files")
args = parser.parse_args()

report = []
failures = 0


def log(message=""):
    text = str(message)
    print(text)
    report.append(text)


log("UR Fall initial sample check")
log(f"Source: {args.root}")
log("Scope: two camera-0 depth sequences and four CSV files.")
log("Original files are read only; no extraction or modification.")
log()

for filename in ("fall-01-cam0-d.zip", "adl-01-cam0-d.zip"):
    log(f"Archive: {filename}")

    try:
        path = args.root / filename
        log(f"Archive bytes: {path.stat().st_size}")

        with zipfile.ZipFile(path) as archive:
            bad_file = archive.testzip()
            if bad_file is not None:
                raise ValueError(f"ZIP integrity error: {bad_file}")
            log("ZIP integrity: PASS")

            images = sorted(
                name for name in archive.namelist()
                if name.lower().endswith(".png")
                and not name.startswith("__MACOSX/")
            )
            if not images:
                raise ValueError("No PNG images found")

            log(f"PNG files listed: {len(images)}")
            log(f"Sample: {images[0]}")

            raw = archive.read(images[0])
            if raw[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("Invalid PNG signature")

            width, height, bits, color = struct.unpack(
                ">IIBB", raw[16:26]
            )
            log(f"PNG dimensions: {height} x {width}")
            log(f"PNG bit depth: {bits}")
            log(f"PNG color type: {color} (0 = grayscale)")

            with Image.open(io.BytesIO(raw)) as image:
                pixels = np.array(image)
                log(f"Pillow mode: {image.mode}")

            log(f"Decoded shape: {pixels.shape}")
            log(f"Decoded dtype: {pixels.dtype}")
            log(f"Raw pixel range: {pixels.min()} to {pixels.max()}")
            log(f"Finite pixels: {bool(np.isfinite(pixels).all())}")
            log(f"Nonzero pixels: {np.count_nonzero(pixels)}")

            if bits != 16 or color != 0 or pixels.ndim != 2:
                raise ValueError("Expected a 16-bit grayscale depth PNG")
            if not np.isfinite(pixels).all():
                raise ValueError("Non-finite pixel values")

            log("First depth image read: PASS")

    except Exception as exc:
        failures += 1
        log(f"FAIL: {type(exc).__name__}: {exc}")

    log()

for filename in (
    "fall-01-data.csv",
    "adl-01-data.csv",
    "fall-01-acc.csv",
    "adl-01-acc.csv",
):
    log(f"CSV: {filename}")

    try:
        path = args.root / filename
        text = path.read_text(encoding="utf-8-sig")
        if not text.strip():
            raise ValueError("Empty CSV")

        try:
            dialect = csv.Sniffer().sniff(
                text[:8192], delimiters=",;\t "
            )
            rows = list(csv.reader(io.StringIO(text), dialect))
        except csv.Error:
            rows = list(csv.reader(io.StringIO(text)))

        rows = [row for row in rows if any(cell.strip() for cell in row)]
        if not rows:
            raise ValueError("No nonblank rows")

        log(f"File bytes: {path.stat().st_size}")
        log(f"Nonblank rows, including any header: {len(rows)}")
        log(f"Column counts observed: {sorted(set(map(len, rows)))}")
        log(f"First row: {rows[0]}")
        log("CSV text read: PASS")

    except Exception as exc:
        failures += 1
        log(f"FAIL: {type(exc).__name__}: {exc}")

    log()

log(f"Files with failures: {failures}")
log("Limits: only the first PNG per ZIP was decoded.")
log("CSV timestamps, synchronization and labels are not yet validated.")

output = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "urfall_sample_check.txt"
)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"\nSaved: {output}")

raise SystemExit(1 if failures else 0)
