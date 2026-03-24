"""
Build a compact JSON for the website by merging CSV stats with AI exposure scores.

Reads occupations.csv (for stats) and scores.json (for AI exposure).
Writes site/data.json.

Usage:
    uv run python build_site_data.py
"""

import csv
import json
import os
import re


def main():
    # Keep one hierarchy level to avoid summing the same workforce repeatedly.
    target_level = int(os.getenv("TREE_LEVEL", "4"))

    # Load AI exposure scores (optional)
    scores = {}
    if os.path.exists("data/scores.json"):
        with open("data/scores.json") as f:
            scores_list = json.load(f)
        scores = {s["slug"]: s for s in scores_list}

    # Load CSV stats
    with open("data/occupations.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    def row_level(title: str) -> int:
        m = re.search(r"\(Level (\d+)\)", title or "")
        return int(m.group(1)) if m else -1

    rows = [r for r in rows if row_level(r.get("title", "")) == target_level]

    # Merge
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})

        # Use exposure from CSV if available, otherwise from scores.json
        exposure = row.get("exposure")
        if exposure:
            exposure = int(exposure)
        else:
            exposure = score.get("exposure")

        exposure_rationale = row.get("exposure_rationale") or score.get("rationale", "")

        data.append(
            {
                "title": row["title"],
                "slug": slug,
                "category": row["category"],
                "pay": int(row["median_pay_annual"])
                if row["median_pay_annual"]
                else None,
                "pay_source": row.get("median_pay_source", ""),
                "jobs": int(row["num_jobs_2024"]) if row["num_jobs_2024"] else None,  # 2024 data (year pinned in statfin_config.json)
                "outlook": int(row["outlook_pct"])
                if row["outlook_pct"] and row["outlook_pct"].lstrip("-+").isdigit()
                else None,
                "outlook_desc": row["outlook_desc"],
                "outlook_source": row.get("outlook_source", ""),
                "education": row["entry_education"],
                "work_experience": row.get("work_experience", ""),
                "training": row.get("training", ""),
                "exposure": exposure,
                "exposure_rationale": exposure_rationale,
                "url": row.get("url", ""),
            }
        )

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as f:
        json.dump(data, f)

    print(f"Wrote {len(data)} occupations to site/data.json")
    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Total jobs represented: {total_jobs:,}")
    print(f"Hierarchy level used: Level {target_level}")

    # Print coverage stats
    with_pay = sum(1 for d in data if d["pay"])
    with_education = sum(1 for d in data if d["education"])
    with_outlook = sum(1 for d in data if d["outlook"] is not None)
    with_exposure = sum(1 for d in data if d["exposure"] is not None)
    with_work_exp = sum(1 for d in data if d.get("work_experience"))
    with_training = sum(1 for d in data if d.get("training"))

    print(f"\nData coverage:")
    print(f"  With pay: {with_pay}/{len(data)} ({100 * with_pay / len(data):.1f}%)")
    print(
        f"  With education: {with_education}/{len(data)} ({100 * with_education / len(data):.1f}%)"
    )
    print(
        f"  With work_experience: {with_work_exp}/{len(data)} ({100 * with_work_exp / len(data):.1f}%)"
    )
    print(
        f"  With training: {with_training}/{len(data)} ({100 * with_training / len(data):.1f}%)"
    )
    print(
        f"  With outlook: {with_outlook}/{len(data)} ({100 * with_outlook / len(data):.1f}%)"
    )
    print(
        f"  With AI exposure: {with_exposure}/{len(data)} ({100 * with_exposure / len(data):.1f}%)"
    )


if __name__ == "__main__":
    main()
