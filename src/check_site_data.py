"""
Sanity-check the built site data before it is published.

Checks that docs/data.json (the GitHub Pages copy) is identical to
site/data.json, and that site/data.json has:
- exactly the levels 1..TREE_LEVEL, each covering the same total employment
- no "(Level N)" suffix left in any title
- an integer AI exposure from 0 to 10 and a rationale on every finest-level row
- pay on every finest-level row: its own median (pay_source "wages_statfin",
  or "extras_csv" when data/extras.csv supplies it) or the build's
  group-median estimate ("estimated"); at most --max-estimated (default 150)
  estimated finest-level rows
- a pay_basis (the group the estimate comes from) on every row, occupation or
  group, whose pay is estimated
- on every group row, the employment-weighted mean exposure of the
  finest-level occupations under its code (as built by build_site_data.py)
- at least --min-rows finest-level rows (default 400; Level 4 has 459)

Lists every problem and exits 1 if any check fails, 0 otherwise.

Usage:
    uv run python src/check_site_data.py
"""

import argparse
import json
import os

# Same averaging as the build; importing it also loads .env (TREE_LEVEL)
from build_site_data import employed_members, weighted_mean

SITE_FILE = "site/data.json"
DOCS_FILE = "docs/data.json"
# A finest-level row's own pay (StatFin, or extras.csv via fetch_statfin.py),
# or the build's group-median estimate
PAY_SOURCES = {"wages_statfin", "extras_csv", "estimated"}
TOLERANCE = 0.051  # group exposures are rounded to one decimal
SHOW = 10  # rows listed per failed check


def is_score(value) -> bool:
    """An integer exposure from 0 to 10 (true/false don't count)."""
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 10


def is_pay(value) -> bool:
    """A positive pay figure."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def check_rows(data: list, tree_level: int, min_rows: int, max_estimated: int) -> list:
    """Problems found in the site rows, as printable lines."""
    problems = []

    def add(message, items=()):
        items = list(items)
        problems.append(f"{message} ({len(items)})" if items else message)
        problems.extend(f"    {item}" for item in items[:SHOW])
        if len(items) > SHOW:
            problems.append(f"    ... and {len(items) - SHOW} more")

    by_level = {}
    for d in data:
        by_level.setdefault(d.get("level"), []).append(d)

    expected_levels = list(range(1, tree_level + 1))
    found_levels = sorted(by_level, key=lambda v: (0, v) if isinstance(v, int) else (1, str(v)))
    if found_levels != expected_levels:
        add(f"levels {found_levels} found, expected {expected_levels} (TREE_LEVEL={tree_level})")

    # Each level covers the whole workforce, so every level sums to the same
    totals = {level: sum(d.get("jobs") or 0 for d in rows) for level, rows in by_level.items()}
    if len(set(totals.values())) > 1:
        add(
            "employment totals differ between levels",
            [f"Level {level}: {totals[level]:,} jobs" for level in found_levels],
        )

    bad_titles = [d.get("title") for d in data if "(Level" in (d.get("title") or "")]
    if bad_titles:
        add('titles still contain "(Level"', bad_titles)

    finest = by_level.get(tree_level, [])
    if len(finest) < min_rows:
        add(f"only {len(finest)} Level {tree_level} rows, expected at least {min_rows}")

    unscored = [
        f"{d.get('title')}: {d.get('exposure')!r}"
        for d in finest
        if not is_score(d.get("exposure"))
    ]
    if unscored:
        add(f"Level {tree_level} rows without an integer exposure from 0 to 10", unscored)
    no_rationale = [
        d.get("title") for d in finest if not str(d.get("exposure_rationale") or "").strip()
    ]
    if no_rationale:
        add(f"Level {tree_level} rows without an exposure rationale", no_rationale)

    # Pay: the row's own median, or the build's group-median estimate
    no_pay = [
        f"{d.get('title')}: pay {d.get('pay')!r}, pay_source {d.get('pay_source')!r}"
        for d in finest
        if not is_pay(d.get("pay")) or d.get("pay_source") not in PAY_SOURCES
    ]
    if no_pay:
        add(f"Level {tree_level} rows without their own or estimated pay", no_pay)
    # Estimates, on occupations and on groups, must name the group they come from
    no_basis = [
        f"{d.get('title')} (Level {d.get('level')})"
        for d in data
        if d.get("pay_source") == "estimated" and not str(d.get("pay_basis") or "").strip()
    ]
    if no_basis:
        add("estimated pay without a pay_basis", no_basis)
    estimated = [d for d in finest if d.get("pay_source") == "estimated"]
    if len(estimated) > max_estimated:
        add(
            f"{len(estimated)} Level {tree_level} rows have estimated pay, "
            f"more than {max_estimated}"
        )

    # Groups: employment-weighted mean of the finest-level rows under the code,
    # counting only those with employment (all of them if none has any)
    wrong = []
    for d in data:
        level = d.get("level")
        if not isinstance(level, int) or not 1 <= level < tree_level:
            continue
        members = [m for m in finest if m["code"].startswith(d["code"])]
        expected = weighted_mean((m["exposure"], m["jobs"]) for m in employed_members(members))
        actual = d.get("exposure")
        if expected is None or actual is None:
            ok = expected is None and actual is None
        else:
            ok = abs(actual - expected) <= TOLERANCE
        if not ok:
            shown = "none" if expected is None else f"{expected:.2f}"
            wrong.append(
                f"{d.get('title')} (Level {level}, members: {len(members)}): "
                f"{actual!r}, expected {shown}"
            )
    if wrong:
        add("group exposures that don't match their occupations", wrong)

    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Sanity-check site/data.json and its docs/ copy before publishing"
    )
    parser.add_argument(
        "--min-rows",
        type=int,
        default=400,
        help="Minimum number of finest-level rows (default: 400)",
    )
    parser.add_argument(
        "--max-estimated",
        type=int,
        default=150,
        help="Maximum number of finest-level rows with estimated pay (default: 150)",
    )
    args = parser.parse_args()
    tree_level = int(os.getenv("TREE_LEVEL", "4"))

    missing = [path for path in (SITE_FILE, DOCS_FILE) if not os.path.exists(path)]
    if missing:
        print(f"FAILED: not found: {', '.join(missing)} (run src/build_site_data.py, "
              f"then cp {SITE_FILE} {DOCS_FILE})")
        return 1

    problems = []
    with open(SITE_FILE, "rb") as f:
        site_bytes = f.read()
    with open(DOCS_FILE, "rb") as f:
        if f.read() != site_bytes:
            problems.append(f"{DOCS_FILE} differs from {SITE_FILE} (cp {SITE_FILE} {DOCS_FILE})")

    try:
        data = json.loads(site_bytes)
        problems += check_rows(data, tree_level, args.min_rows, args.max_estimated)
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        problems.append(f"{SITE_FILE} is malformed: {type(e).__name__}: {e}")

    if problems:
        print(f"FAILED: {SITE_FILE} did not pass its checks (TREE_LEVEL={tree_level}):")
        for line in problems:
            print(line if line.startswith("    ") else f"  - {line}")
        return 1

    finest = [d for d in data if d["level"] == tree_level]
    jobs = sum(d["jobs"] or 0 for d in finest)
    estimated = sum(1 for d in finest if d["pay_source"] == "estimated")
    print(
        f"OK: {SITE_FILE} = {DOCS_FILE}; {len(data)} rows in levels 1-{tree_level}, "
        f"{len(finest)} at Level {tree_level} ({estimated} with estimated pay), "
        f"{jobs:,} jobs per level"
    )
    return 0


if __name__ == "__main__":
    exit(main())
