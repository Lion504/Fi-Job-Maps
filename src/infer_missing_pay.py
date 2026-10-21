"""Infer missing pay data based on occupation characteristics.

Uses statistical inference from existing pay data to estimate missing values
based on occupation category, education level, and similar occupation patterns.

Usage:
    uv run python infer_missing_pay.py
"""

import json
import os
import re
from typing import Dict, List, Optional
from statistics import median


def load_site_data() -> List[dict]:
    """Load the finest-level occupations from site/data.json.

    The file also holds coarser group rows whose values are derived from these
    occupations at build time, so they are left out of statistics and filling.
    """
    if not os.path.exists("site/data.json"):
        raise FileNotFoundError(
            "site/data.json not found. Run build_site_data.py first."
        )

    with open("site/data.json") as f:
        rows = json.load(f)
    levels = [r["level"] for r in rows if r.get("level") is not None]
    if not levels:
        return rows
    return [r for r in rows if r.get("level") == max(levels)]


def occupation_code(occ: dict) -> str:
    """ISCO code without trailing dots, from the code field or the title."""
    code = occ.get("code")
    if not code:
        match = re.match(r"^(\d+\.?)[\s\.]", occ["title"])
        code = match.group(1) if match else ""
    return code.rstrip(".")


def load_occupations_csv() -> Dict[str, dict]:
    """Load occupation data from data/occupations.csv."""
    import csv

    if not os.path.exists("data/occupations.csv"):
        return {}

    occupations = {}
    with open("data/occupations.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("isco_code", "").strip()
            if code:
                occupations[code] = row

    return occupations


def calculate_pay_statistics(occupations: List[dict]) -> Dict:
    """Calculate pay statistics from existing data."""
    stats = {
        "category": {},
        "education": {},
        "category_education": {},
    }

    # Group by category
    for occ in occupations:
        if occ.get("pay") is None:
            continue

        cat = occ["category"]
        edu = occ.get("education", "")
        pay = occ["pay"]

        # By category
        if cat not in stats["category"]:
            stats["category"][cat] = []
        stats["category"][cat].append(pay)

        # By education
        if edu:
            if edu not in stats["education"]:
                stats["education"][edu] = []
            stats["education"][edu].append(pay)

        # By category + education
        key = f"{cat}_{edu}"
        if key not in stats["category_education"]:
            stats["category_education"][key] = []
        stats["category_education"][key].append(pay)

    # Calculate medians
    for key in stats["category"]:
        stats["category"][key] = int(median(stats["category"][key]))
    for key in stats["education"]:
        stats["education"][key] = int(median(stats["education"][key]))
    for key in stats["category_education"]:
        stats["category_education"][key] = int(median(stats["category_education"][key]))

    return stats


def find_similar_occupation_pay(
    code: str, all_occupations: Dict[str, dict]
) -> Optional[int]:
    """Find pay from similar occupation code (3-digit match)."""
    if not code or len(code) < 3:
        return None

    # Try 3-digit code match
    prefix = code[:3].rstrip(".")

    for occ_code, occ_data in all_occupations.items():
        if occ_code.startswith(prefix) and occ_data.get("median_pay_annual"):
            try:
                return int(float(occ_data["median_pay_annual"]))
            except (ValueError, TypeError):
                continue

    return None


def infer_pay(
    occ: dict, stats: Dict, all_occupations: Dict[str, dict]
) -> Optional[int]:
    """Infer pay for an occupation based on available data."""
    category = occ["category"]
    education = occ.get("education", "")
    code = occupation_code(occ)

    # Strategy 1: Find pay from similar occupation code
    similar_pay = find_similar_occupation_pay(code, all_occupations)
    if similar_pay:
        return similar_pay

    # Strategy 2: Use category + education combination
    key = f"{category}_{education}"
    if key in stats["category_education"]:
        return stats["category_education"][key]

    # Strategy 3: Use education median
    if education and education in stats["education"]:
        return stats["education"][education]

    # Strategy 4: Use category median
    if category in stats["category"]:
        return stats["category"][category]

    # Fallback: Statistics Finland 2023 median across all wage earners (~€43,500/yr)
    # Source: Tilastokeskus / Statistics Finland, Structure of Earnings 2023
    # Update this value when a newer reference year is available.
    return 43500  # tagged as inferred_fallback in median_pay_source


def main():
    print("Loading occupation data...")
    site_occupations = load_site_data()
    csv_occupations = load_occupations_csv()

    print(f"Loaded {len(site_occupations)} finest-level occupations from site/data.json")
    print(f"Loaded {len(csv_occupations)} occupations from data/occupations.csv")

    # Calculate statistics
    print("\nCalculating pay statistics...")
    stats = calculate_pay_statistics(site_occupations)

    print("\nPay statistics by category:")
    for cat in sorted(stats["category"].keys()):
        print(f"  Category {cat}: €{stats['category'][cat]:,}/year")

    print("\nPay statistics by education:")
    for edu in sorted(stats["education"].keys()):
        if edu:
            print(f"  {edu}: €{stats['education'][edu]:,}/year")

    # Count missing
    missing = [occ for occ in site_occupations if occ.get("pay") is None]
    print(f"\nFound {len(missing)} occupations without pay data")

    # Infer missing pay
    print("\nInferring missing pay data...")
    updates = []

    for occ in missing:
        code = occupation_code(occ)
        inferred_pay = infer_pay(occ, stats, csv_occupations)

        updates.append(
            {
                "slug": occ["slug"],
                "code": code,
                "title": occ["title"],
                "category": occ["category"],
                "education": occ.get("education", ""),
                "inferred_pay": inferred_pay,
            }
        )

    # Update occupations.csv with inferred pay
    import csv

    if os.path.exists("data/occupations.csv"):
        # Read existing data
        with open("data/occupations.csv") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        # Update rows (matched on slug, so only the finest-level rows change)
        updates_by_slug = {upd["slug"]: upd for upd in updates}
        updated_count = 0
        for row in rows:
            upd = updates_by_slug.get(row.get("slug", ""))
            if upd and not row.get("median_pay_annual"):
                row["median_pay_annual"] = str(upd["inferred_pay"])
                row["median_pay_source"] = "inferred_fallback"
                updated_count += 1

        # Write back
        with open("data/occupations.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✓ Updated {updated_count} pay entries in data/occupations.csv")

    # Show sample updates
    print("\nSample inferred pay values:")
    for upd in updates[:10]:
        print(f"  {upd['code']} - {upd['title'][:50]}...")
        print(f"    Category: {upd['category']}, Education: {upd['education']}")
        print(f"    Inferred pay: €{upd['inferred_pay']:,}/year")

    print(f"\nTotal occupations updated: {len(updates)}")
    print("\nNext steps:")
    print("  1. Run: uv run python src/build_site_data.py")
    print("  2. Refresh your browser")


if __name__ == "__main__":
    main()
