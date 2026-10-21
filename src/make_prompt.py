"""
Generate prompt.md — a single file containing all project data, designed to be
copy-pasted into an LLM for analysis and conversation about AI exposure of the
Finnish job market.

Covers the finest level (TREE_LEVEL, default 4). Pay comes from the built
site/data.json, so run build_site_data.py first; pay estimated from a group
median is marked "(est.)". The same inputs always give the same file.

Usage:
    uv run python src/make_prompt.py
"""

import csv
import json
import os

# Titles and outlook as the site shows them; importing it also loads .env
# (TREE_LEVEL)
from build_site_data import clean_title, parse_outlook, row_level


def fmt_pay(pay, estimated=False):
    """Annual pay as the site shows it, e.g. 66,408 €."""
    if pay is None:
        return "?"
    return f"{pay:,} €" + (" (est.)" if estimated else "")


def fmt_wages(total):
    """A large euro sum as the site shows it, e.g. 105.6B €."""
    for divisor, unit in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if total >= divisor:
            return f"{total / divisor:.1f}{unit} €"
    return f"{total:.0f} €"


def fmt_jobs(jobs):
    if jobs is None:
        return "?"
    if jobs >= 1_000_000:
        return f"{jobs / 1e6:.1f}M"
    if jobs >= 1_000:
        return f"{jobs / 1e3:.0f}K"
    return str(jobs)


def main():
    # Load all data sources from data directory
    with open("data/occupations.json") as f:
        occupations = json.load(f)

    # Only the finest level is scored; coarser levels are aggregates of it and
    # would count every job several times over.
    tree_level = int(os.getenv("TREE_LEVEL", "4"))
    occupations = [o for o in occupations if row_level(o["title"]) == tree_level]

    with open("data/occupations.csv") as f:
        csv_rows = {row["slug"]: row for row in csv.DictReader(f)}

    with open("data/scores.json") as f:
        scores = {s["slug"]: s for s in json.load(f)}

    # Pay as shown on the site: StatFin's median, or the build's estimate from
    # the occupation's group where StatFin publishes none
    with open("site/data.json") as f:
        site_rows = {}
        for d in json.load(f):
            if d.get("level") == tree_level:
                site_rows.setdefault(d["slug"], d)

    # Merge into unified records
    records = []
    for occ in occupations:
        slug = occ["slug"]
        row = csv_rows.get(slug, {})
        score = scores.get(slug, {})
        site_row = site_rows.get(slug, {})
        pay = site_row.get("pay")
        jobs_value = row.get("num_jobs") or row.get("num_jobs_2024")
        jobs = int(jobs_value) if jobs_value else None
        records.append(
            {
                "title": clean_title(occ["title"]),
                "slug": slug,
                "category": row.get("category", occ.get("category", "")),
                "pay": pay,
                "pay_estimated": site_row.get("pay_source") == "estimated",
                "jobs": jobs,
                "outlook_pct": parse_outlook(row.get("outlook_pct", "")),
                "outlook_desc": row.get("outlook_desc", ""),
                "education": row.get("entry_education", ""),
                "exposure": score.get("exposure"),
                "rationale": score.get("rationale", ""),
                "url": occ.get("url", ""),
            }
        )

    # Sort by exposure desc, then jobs desc
    records.sort(key=lambda r: (-(r["exposure"] or 0), -(r["jobs"] or 0)))

    lines = []

    # ── Header ──
    lines.append("# AI Exposure of the Finnish Job Market")
    lines.append("")
    # The models recorded in scores.json for these occupations
    models = ", ".join(
        sorted({scores[r["slug"]].get("model") or "unknown" for r in records if r["slug"] in scores})
    )
    lines.append(
        f"This document contains structured data on {len(records)} Finnish occupations from Statistics Finland PxWeb and Occupational Barometer, each scored for AI exposure on a 0-10 scale by an LLM ({models or 'none'}). Use this data to analyze, question, and discuss how AI will reshape the Finnish labor market."
    )
    lines.append("")
    lines.append(
        "Pay is the Statistics Finland median. Where it publishes none for an occupation, the median of the occupation's group is used and marked (est.)."
    )
    lines.append("")
    lines.append("Live visualization: https://lion504.github.io/Fi-Job-Maps/")
    lines.append("GitHub: https://github.com/Lion504/Fi-Job-Maps")
    lines.append("Adapted from karpathy/jobs: https://github.com/karpathy/jobs")
    lines.append("")

    # ── Scoring methodology ──
    lines.append("## Scoring methodology")
    lines.append("")
    lines.append(
        "Each occupation was scored on a single AI Exposure axis from 0 to 10, measuring how much AI will reshape that occupation. The score considers both direct automation (AI doing the work) and indirect effects (AI making workers so productive that fewer are needed)."
    )
    lines.append("")
    lines.append(
        "A key heuristic: if the job can be done entirely from a home office on a computer — writing, coding, analyzing, communicating — then AI exposure is inherently high (7+), because AI capabilities in digital domains are advancing rapidly. Conversely, jobs requiring physical presence, manual skill, or real-time human interaction have a natural barrier."
    )
    lines.append("")
    # The anchors of the rubric in score.py
    lines.append("Calibration anchors:")
    lines.append("- 0-1 Minimal: roofers, landscapers, commercial divers")
    lines.append("- 2-3 Low: electricians, plumbers, firefighters, dental hygienists")
    lines.append("- 4-5 Moderate: registered nurses, police officers, veterinarians")
    lines.append("- 6-7 High: teachers, managers, accountants, journalists")
    lines.append(
        "- 8-9 Very high: software developers, graphic designers, translators, data analysts, paralegals, copywriters"
    )
    lines.append("- 10 Maximum: data entry clerks, telemarketers")
    lines.append("")

    # ── Aggregate statistics ──
    lines.append("## Aggregate statistics")
    lines.append("")

    total_jobs = sum(r["jobs"] or 0 for r in records)
    total_wages = sum((r["jobs"] or 0) * (r["pay"] or 0) for r in records)

    # Weighted avg exposure
    w_sum = sum(
        (r["exposure"] or 0) * (r["jobs"] or 0)
        for r in records
        if r["exposure"] is not None and r["jobs"]
    )
    w_count = sum(
        r["jobs"] or 0 for r in records if r["exposure"] is not None and r["jobs"]
    )
    w_avg = w_sum / w_count if w_count else 0

    lines.append(f"- Total occupations: {len(records)}")
    lines.append(f"- Total jobs: {total_jobs:,} ({total_jobs / 1e6:.0f}M)")
    lines.append(f"- Total annual wages: {fmt_wages(total_wages)}")
    lines.append(f"- Job-weighted average AI exposure: {w_avg:.1f}/10")
    lines.append("")

    # Tier breakdown
    tiers = [
        ("Minimal (0-1)", 0, 1),
        ("Low (2-3)", 2, 3),
        ("Moderate (4-5)", 4, 5),
        ("High (6-7)", 6, 7),
        ("Very high (8-10)", 8, 10),
    ]
    lines.append("### Breakdown by exposure tier")
    lines.append("")
    lines.append(
        "| Tier | Occupations | Jobs | % of jobs | Wages | % of wages | Avg pay |"
    )
    lines.append(
        "|------|-------------|------|-----------|-------|------------|---------|"
    )
    for name, lo, hi in tiers:
        group = [
            r
            for r in records
            if r["exposure"] is not None and lo <= r["exposure"] <= hi
        ]
        jobs = sum(r["jobs"] or 0 for r in group)
        wages = sum((r["jobs"] or 0) * (r["pay"] or 0) for r in group)
        avg_pay = wages / jobs if jobs else 0
        lines.append(
            f"| {name} | {len(group)} | {fmt_jobs(jobs)} | {jobs / total_jobs * 100:.1f}% | {fmt_wages(wages)} | {wages / total_wages * 100:.1f}% | {fmt_pay(int(avg_pay))} |"
        )
    lines.append("")

    # By pay band
    lines.append("### Average exposure by pay band (job-weighted)")
    lines.append("")
    # Same bands and labels as the site
    pay_bands = [
        ("<€35K", 0, 35000),
        ("€35–50K", 35000, 50000),
        ("€50–75K", 50000, 75000),
        ("€75–100K", 75000, 100000),
        ("€100K+", 100000, float("inf")),
    ]
    lines.append("| Pay band | Avg exposure | Jobs |")
    lines.append("|----------|-------------|------|")
    for name, lo, hi in pay_bands:
        group = [
            r
            for r in records
            if r["pay"]
            and lo <= r["pay"] < hi
            and r["exposure"] is not None
            and r["jobs"]
        ]
        if group:
            ws = sum(r["exposure"] * r["jobs"] for r in group)
            wc = sum(r["jobs"] for r in group)
            lines.append(f"| {name} | {ws / wc:.1f} | {fmt_jobs(wc)} |")
    lines.append("")

    # By education
    lines.append("### Average exposure by education level (job-weighted)")
    lines.append("")
    edu_groups = [
        (
            "Basic / Upper secondary",
            ["Basic education", "Upper secondary"],
        ),
        (
            "Bachelor's",
            ["Bachelor's degree", "Bachelor's degree + military training"],
        ),
        ("Master's", ["Master's degree"]),
        ("Doctoral", ["Doctoral degree"]),
    ]
    lines.append("| Education | Avg exposure | Jobs |")
    lines.append("|-----------|-------------|------|")
    for name, matches in edu_groups:
        group = [
            r
            for r in records
            if r["education"] in matches and r["exposure"] is not None and r["jobs"]
        ]
        if group:
            ws = sum(r["exposure"] * r["jobs"] for r in group)
            wc = sum(r["jobs"] for r in group)
            lines.append(f"| {name} | {ws / wc:.1f} | {fmt_jobs(wc)} |")
    lines.append("")

    # Outlook vs exposure
    lines.append("### Declining occupations (negative outlook)")
    lines.append("")
    declining = [
        r for r in records if r["outlook_pct"] is not None and r["outlook_pct"] < 0
    ]
    declining.sort(key=lambda r: r["outlook_pct"])
    lines.append("| Occupation | Exposure | Outlook | Jobs |")
    lines.append("|-----------|----------|---------|------|")
    for r in declining:
        lines.append(
            f"| {r['title']} | {r['exposure']}/10 | {r['outlook_pct']:+d}% | {fmt_jobs(r['jobs'])} |"
        )
    lines.append("")

    lines.append("### Best-outlook occupations (outlook +10% or more)")
    lines.append("")
    growing = [
        r for r in records if r["outlook_pct"] is not None and r["outlook_pct"] >= 10
    ]
    growing.sort(key=lambda r: -r["outlook_pct"])
    lines.append("| Occupation | Exposure | Outlook | Jobs |")
    lines.append("|-----------|----------|---------|------|")
    for r in growing:
        lines.append(
            f"| {r['title']} | {r['exposure']}/10 | +{r['outlook_pct']}% | {fmt_jobs(r['jobs'])} |"
        )
    lines.append("")

    # ── Full occupation table ──
    lines.append(f"## All {len(records)} occupations")
    lines.append("")
    lines.append(
        "Sorted by AI exposure (descending), then by number of jobs (descending)."
    )
    lines.append("")

    for score in range(10, -1, -1):
        group = [r for r in records if r["exposure"] == score]
        if not group:
            continue
        group_jobs = sum(r["jobs"] or 0 for r in group)
        lines.append(
            f"### Exposure {score}/10 ({len(group)} occupations, {fmt_jobs(group_jobs)} jobs)"
        )
        lines.append("")
        lines.append(
            "| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |"
        )
        lines.append("|---|-----------|-----|------|---------|-----------|-----------|")
        for i, r in enumerate(group, 1):
            outlook = f"{r['outlook_pct']:+d}%" if r["outlook_pct"] is not None else "?"
            edu = r["education"] if r["education"] else "?"
            # Truncate education for readability
            edu_short = {
                "Basic education": "Basic",
                "Upper secondary": "Upper sec",
                "Bachelor's degree": "Bachelor's",
                "Bachelor's degree + military training": "Bachelor's+",
                "Master's degree": "Master's",
                "Doctoral degree": "Doctoral",
            }.get(edu, edu)
            rationale = r["rationale"].replace("|", "/").replace("\n", " ")
            lines.append(
                f"| {i} | {r['title']} | {fmt_pay(r['pay'], r['pay_estimated'])} | {fmt_jobs(r['jobs'])} | {outlook} | {edu_short} | {rationale} |"
            )
        lines.append("")

    # Write
    text = "\n".join(lines)
    with open("prompt.md", "w") as f:
        f.write(text)

    print(f"Wrote prompt.md ({len(text):,} chars, {len(lines):,} lines)")


if __name__ == "__main__":
    main()
