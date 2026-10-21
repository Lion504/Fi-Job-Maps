"""
Build a compact JSON for the website by merging CSV stats with AI exposure scores.

Reads occupations.csv (for stats) and scores.json (for AI exposure).
Writes site/data.json with one row per occupation group for levels
1..TREE_LEVEL of the Classification of Occupations 2010 (default 1-4).

Rows at the finest level (TREE_LEVEL) carry their own stats and LLM score.
Group rows (coarser levels) use their own StatFin employment and pay, and
derive outlook, AI exposure and education from the finest-level occupations
they contain (employment-weighted means, or the label with the largest share
of the group's employment).

Usage:
    uv run python src/build_site_data.py
"""

import csv
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()  # TREE_LEVEL may be set in .env, as for score.py

LEVEL_RE = re.compile(r"\s*\(Level (\d+)\)\s*$")


def row_level(title: str) -> int:
    m = LEVEL_RE.search(title or "")
    return int(m.group(1)) if m else -1


def clean_title(title: str) -> str:
    """Drop the " (Level N)" suffix and collapse StatFin's double spaces."""
    return re.sub(r"\s+", " ", LEVEL_RE.sub("", title or "")).strip()


def weighted_mean(pairs):
    """Employment-weighted mean of (value, jobs) pairs; None if no values.

    Falls back to a plain mean when none of the occupations has employment.
    """
    pairs = [(v, j or 0) for v, j in pairs if v is not None]
    if not pairs:
        return None
    total = sum(j for _, j in pairs)
    if total == 0:
        return sum(v for v, _ in pairs) / len(pairs)
    return sum(v * j for v, j in pairs) / total


def dominant_value(members, key):
    """The value of `key` held by the largest share of employment."""
    jobs_by_value, count_by_value = {}, {}
    for d in members:
        value = d.get(key)
        if not value:
            continue
        jobs_by_value[value] = jobs_by_value.get(value, 0) + (d["jobs"] or 0)
        count_by_value[value] = count_by_value.get(value, 0) + 1
    if not jobs_by_value:
        return ""
    return max(jobs_by_value, key=lambda v: (jobs_by_value[v], count_by_value[v]))


def employed_members(members):
    """Members with employment; all of them if none has any.

    Leaves out zero-employment placeholders such as "95.. (Not more
    specifically classified)", which carry no weight in the averages.
    """
    return [d for d in members if d["jobs"]] or members


def exposure_summary(members) -> str:
    """One-line rationale for a group's derived AI exposure."""
    scored = [d for d in members if d["exposure"] is not None]
    if not scored:
        return ""
    if len(scored) == 1:
        d = scored[0]
        text = f"Based on its only scored occupation, {d['title']} ({d['exposure']})."
    else:
        # Ties go to the occupation with more employment
        hi = max(scored, key=lambda d: (d["exposure"], d["jobs"] or 0))
        lo = min(scored, key=lambda d: (d["exposure"], -(d["jobs"] or 0)))
        text = f"Employment-weighted average of {len(scored)} occupations."
        if hi["exposure"] == lo["exposure"]:
            text += f" All score {hi['exposure']}."
        else:
            text += (
                f" Highest: {hi['title']} ({hi['exposure']})."
                f" Lowest: {lo['title']} ({lo['exposure']})."
            )
    unscored = len(members) - len(scored)
    if unscored:
        text += f" {unscored} more have no score."
    return text


def base_row(row: dict, level: int) -> dict:
    """Fields shared by occupation and group rows, straight from the CSV."""
    return {
        "title": clean_title(row["title"]),
        "slug": row["slug"],
        "level": level,
        "code": row["isco_code"],
        "category": row["category"],
        "pay": int(row["median_pay_annual"]) if row["median_pay_annual"] else None,
        "pay_source": row.get("median_pay_source", ""),
        "jobs": int(row.get("num_jobs") or row.get("num_jobs_2024") or 0) or None,
        "jobs_year": int(row["employment_year"])
        if row.get("employment_year", "").isdigit()
        else None,
    }


def occupation_row(row: dict, level: int, scores: dict) -> dict:
    d = base_row(row, level)

    # scores.json (joined by slug) is the only source: the CSV exposure column
    # may hold stale values from older title matching, so it is not used.
    score = scores.get(row["slug"], {})
    if score.get("exposure") is not None:
        exposure = int(score["exposure"])
        exposure_rationale = score.get("rationale", "")
    else:
        exposure, exposure_rationale = None, ""

    d.update(
        {
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
    return d


def group_row(row: dict, level: int, members: list) -> dict:
    d = base_row(row, level)

    # Pay: the group's own StatFin median when published, else derived
    if d["pay"] is None:
        pay = weighted_mean((m["pay"], m["jobs"]) for m in members)
        d["pay"] = round(pay) if pay is not None else None
        d["pay_source"] = "derived" if pay is not None else ""

    outlook = weighted_mean((m["outlook"], m["jobs"]) for m in members)
    exposure = weighted_mean((m["exposure"], m["jobs"]) for m in members)
    outlook = round(outlook, 1) if outlook is not None else None
    # The occupations counted in `members` and named in the rationale
    counted = employed_members(members)

    d.update(
        {
            "outlook": outlook,
            # Source labels don't follow fixed thresholds, so take the label
            # with the largest share of the group's employment, not the mean's
            "outlook_desc": dominant_value(members, "outlook_desc"),
            "outlook_source": "derived" if outlook is not None else "",
            "education": dominant_value(members, "education"),
            "work_experience": dominant_value(members, "work_experience"),
            "training": dominant_value(members, "training"),
            "exposure": round(exposure, 1) if exposure is not None else None,
            "exposure_rationale": exposure_summary(counted),
            "members": len(counted),
            "url": row.get("url", ""),
        }
    )
    return d


def main():
    # The finest level is scored and shown by default; coarser levels are
    # emitted as separate groups (never summed together with it).
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

    rows_by_level = {}
    for r in rows:
        level = row_level(r.get("title", ""))
        if 1 <= level <= target_level:
            rows_by_level.setdefault(level, []).append(r)

    occupations = [
        occupation_row(r, target_level, scores)
        for r in rows_by_level.get(target_level, [])
    ]

    # Groups: descendants are the finest-level occupations under the group code
    data = []
    for level in range(1, target_level):
        for r in rows_by_level.get(level, []):
            code = r["isco_code"]
            members = [d for d in occupations if d["code"].startswith(code)]
            data.append(group_row(r, level, members))
    data.extend(occupations)

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as f:
        json.dump(data, f)

    print(f"Wrote {len(data)} rows to site/data.json (levels 1-{target_level})")
    for level in range(1, target_level + 1):
        level_rows = [d for d in data if d["level"] == level]
        total_jobs = sum(d["jobs"] for d in level_rows if d["jobs"])
        print(f"  Level {level}: {len(level_rows)} rows, {total_jobs:,} jobs")

    # Print coverage stats for the finest (scored) level
    data = occupations
    if not data:
        return
    with_pay = sum(1 for d in data if d["pay"])
    with_education = sum(1 for d in data if d["education"])
    with_outlook = sum(1 for d in data if d["outlook"] is not None)
    with_exposure = sum(1 for d in data if d["exposure"] is not None)
    from_scores = sum(1 for d in data if d["slug"] in scores)
    with_work_exp = sum(1 for d in data if d.get("work_experience"))
    with_training = sum(1 for d in data if d.get("training"))

    print(f"\nData coverage (Level {target_level}):")
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
        f", {from_scores} from scores.json"
    )


if __name__ == "__main__":
    main()
