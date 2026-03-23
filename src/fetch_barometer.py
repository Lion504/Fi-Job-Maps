"""Normalize Labour Force Barometer outlook data into extras-compatible CSV.

This script prepares occupation-level outlook data from an external CSV and
writes columns compatible with fetch_statfin.py extras merging.

Usage examples:
    uv run python fetch_barometer.py \
      --input barometer.csv \
      --output barometer_outlook.csv \
      --code-column isco_code \
      --outlook-desc-column balance_label

    uv run python fetch_barometer.py \
      --input barometer.csv \
      --output barometer_outlook.csv \
      --code-column ammatti_koodi \
      --outlook-pct-column balance_pct \
      --outlook-desc-column balance_label
"""

import argparse
import csv
import os
from typing import Dict, List


def normalize_code(code: str) -> str:
    return (code or "").strip()


def get_required(row: Dict[str, str], col: str) -> str:
    if col not in row:
        raise KeyError(f"Column not found in input CSV: {col}")
    return (row.get(col) or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to barometer CSV")
    parser.add_argument(
        "--output",
        default="barometer_outlook.csv",
        help="Output extras-compatible CSV",
    )
    parser.add_argument(
        "--code-column",
        required=True,
        help="Input column containing occupation code",
    )
    parser.add_argument(
        "--outlook-desc-column",
        required=True,
        help="Input column containing outlook category/label",
    )
    parser.add_argument(
        "--outlook-pct-column",
        default="",
        help="Optional input column containing numeric outlook percentage",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input CSV not found: {args.input}")

    entries: Dict[str, Dict[str, str]] = {}
    total_rows = 0

    with open(args.input) as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            code = normalize_code(get_required(row, args.code_column))
            if not code:
                continue

            desc = get_required(row, args.outlook_desc_column)
            pct = ""
            if args.outlook_pct_column:
                pct = get_required(row, args.outlook_pct_column)

            entries[code] = {
                "code": code,
                "median_pay_annual": "",
                "entry_education": "",
                "work_experience": "",
                "training": "",
                "outlook_pct": pct,
                "outlook_desc": desc,
            }

    rows: List[Dict[str, str]] = [entries[k] for k in sorted(entries)]

    fieldnames = [
        "code",
        "median_pay_annual",
        "entry_education",
        "work_experience",
        "training",
        "outlook_pct",
        "outlook_desc",
    ]

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Read {total_rows} rows from {args.input}")
    print(f"Wrote {len(rows)} unique occupation codes to {args.output}")


if __name__ == "__main__":
    main()
