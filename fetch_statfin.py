"""Fetch Finnish occupation data from Statistics Finland PxWeb.

Loads a config file (statfin_config.json) that specifies PxWeb tables and
variables for employment, wages, and optional outlook. Produces:
- occupations.json : list of occupations with title, code, slug, category
- occupations.csv  : structured stats compatible with the site pipeline

You can also provide an optional CSV with extra attributes (pay, education,
outlook) keyed by occupation code via the config field "extras_csv". This is
useful when StatFin does not publish a given attribute and you need to merge
an external source (e.g., Occupational Barometer labels or manual education
mapping).

Usage:
    uv run python fetch_statfin.py --config statfin_config.json

Notes:
- The example config (statfin_config.example.json) contains placeholder table
  names; update them to real StatFin endpoints and variables.
- Set year="latest" in config to auto-pick the newest year available.
"""

import argparse
import csv
import json
import os
import re
from typing import Dict, List, Optional, Tuple

import httpx

PXWEB_BASE = "https://pxdata.stat.fi/PxWeb/api/v1/en"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    slug = slug.strip("-")
    return slug or "occupation"


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return json.load(f)


def pxweb_request(table: str, payload: dict) -> dict:
    url = f"{PXWEB_BASE}/{table}"
    resp = httpx.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def pxweb_metadata(table: str) -> dict:
    url = f"{PXWEB_BASE}/{table}"
    resp = httpx.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()


def latest_year(meta: dict, year_var: str) -> str:
    for var in meta.get("variables", []):
        if var.get("code") == year_var:
            values = var.get("values", [])
            if values:
                return values[-1]
    raise ValueError(f"Year variable {year_var} not found in metadata")


def extract_categories(meta: dict, code: str) -> List[Tuple[str, str]]:
    for var in meta.get("variables", []):
        if var.get("code") == code:
            values = var.get("values", [])
            out = []
            labels = var.get("valueTexts", [])
            for v, label in zip(values, labels):
                out.append((v, label))
            return out
    raise ValueError(f"Variable {code} not found in metadata")


def query_single_dimension(table: str, query: List[dict]) -> List[dict]:
    payload = {"query": query, "response": {"format": "JSON"}}
    return pxweb_request(table, payload).get("data", [])


def build_query(var: str, values: List[str]) -> dict:
    return {"code": var, "selection": {"filter": "item", "values": values}}


def fetch_employment(cfg: dict) -> Tuple[Dict[str, int], List[Tuple[str, str]]]:
    table = cfg["table"]
    meta = pxweb_metadata(table)
    occ_var = cfg["occupation_var"]
    year_var = cfg["year_var"]
    var_order = [v.get("code") for v in meta.get("variables", [])]
    if occ_var not in var_order:
        raise ValueError(f"Occupation variable {occ_var} not found in metadata")

    year = cfg.get("year", "latest")
    if year == "latest":
        year = latest_year(meta, year_var)

    occupations = extract_categories(meta, occ_var)

    query = [
        build_query(year_var, [year]),
        build_query(occ_var, [v for v, _ in occupations]),
    ]

    if cfg.get("sex_var") and cfg.get("sex_value"):
        query.append(build_query(cfg["sex_var"], [cfg["sex_value"]]))
    if cfg.get("age_var") and cfg.get("age_value"):
        query.append(build_query(cfg["age_var"], [cfg["age_value"]]))
    if cfg.get("measure_var") and cfg.get("measure_value"):
        query.append(build_query(cfg["measure_var"], [cfg["measure_value"]]))

    # PxWeb returns keys in the dataset variable order; use that to locate occupation values.
    occ_idx = var_order.index(occ_var)

    data = query_single_dimension(table, query)
    employment: Dict[str, int] = {}
    for row in data:
        key_parts = row.get("key", [])
        # occupation code expected to be last if we appended after year/filters
        if not key_parts or occ_idx >= len(key_parts):
            continue
        occ_code = key_parts[occ_idx]
        try:
            employment[occ_code] = int(float(row.get("values", ["0"])[0]))
        except ValueError:
            continue

    return employment, occupations


def fetch_wages(cfg: dict, occupation_codes: List[str]) -> Dict[str, float]:
    table = cfg["table"]
    meta = pxweb_metadata(table)
    occ_var = cfg["occupation_var"]
    year_var = cfg["year_var"]

    # Get variable order to find occupation index
    var_order = [v.get("code") for v in meta.get("variables", [])]
    if occ_var not in var_order:
        raise ValueError(f"Occupation variable {occ_var} not found in metadata")

    year = cfg.get("year", "latest")
    if year == "latest":
        year = latest_year(meta, year_var)

    # Get codes available in wage table
    codes_in_table = {v for v, _ in extract_categories(meta, occ_var)}

    # Build mapping: for each original code, find matching code in wage table
    # Employment table may have '1111.' but wage table has '1111'
    selected_codes = []
    code_mapping = {}  # Map code we query -> original code

    for code in occupation_codes:
        if code in codes_in_table:
            selected_codes.append(code)
            code_mapping[code] = code
        else:
            # Try removing trailing dot
            normalized = code.rstrip(".")
            if normalized in codes_in_table:
                selected_codes.append(normalized)
                code_mapping[normalized] = code

    # Remove duplicates while preserving order
    selected_codes = list(dict.fromkeys(selected_codes))

    if not selected_codes:
        return {}

    query = [
        build_query(year_var, [year]),
        build_query(occ_var, selected_codes),
    ]

    if cfg.get("sex_var") and cfg.get("sex_value"):
        query.append(build_query(cfg["sex_var"], [cfg["sex_value"]]))
    if cfg.get("sector_var") and cfg.get("sector_value"):
        query.append(build_query(cfg["sector_var"], [cfg["sector_value"]]))

    if cfg.get("measure_var") and cfg.get("measure_value"):
        query.append(build_query(cfg["measure_var"], [cfg["measure_value"]]))

    occ_idx = var_order.index(occ_var)

    data = query_single_dimension(table, query)
    wages: Dict[str, float] = {}
    for row in data:
        key_parts = row.get("key", [])
        if not key_parts or occ_idx >= len(key_parts):
            continue
        occ_code = key_parts[occ_idx]
        try:
            wages[occ_code] = float(row.get("values", ["0"])[0])
        except ValueError:
            continue

    # Map codes back to original employment table codes
    result = {}
    for queried_code, orig_code in code_mapping.items():
        if queried_code in wages:
            result[orig_code] = wages[queried_code]

    return result


def fetch_outlook(cfg: Optional[dict], occupation_codes: List[str]) -> Dict[str, dict]:
    if not cfg or not cfg.get("table"):
        return {}
    table = cfg["table"]
    meta = pxweb_metadata(table)
    occ_var = cfg["occupation_var"]
    year_var = cfg["year_var"]

    # Get variable order to find occupation index
    var_order = [v.get("code") for v in meta.get("variables", [])]
    if occ_var not in var_order:
        raise ValueError(f"Occupation variable {occ_var} not found in metadata")

    year = cfg.get("year", "latest")
    if year == "latest":
        year = latest_year(meta, year_var)

    codes_in_table = {v for v, _ in extract_categories(meta, occ_var)}
    selected_codes = [c for c in occupation_codes if c in codes_in_table]
    if not selected_codes:
        return {}

    query = [
        build_query(year_var, [year]),
        build_query(occ_var, selected_codes),
    ]
    if cfg.get("category_var") and cfg.get("category_value"):
        query.append(build_query(cfg["category_var"], [cfg["category_value"]]))

    occ_idx = var_order.index(occ_var)

    data = query_single_dimension(table, query)
    outlook: Dict[str, dict] = {}
    for row in data:
        key_parts = row.get("key", [])
        if not key_parts or occ_idx >= len(key_parts):
            continue
        occ_code = key_parts[occ_idx]
        value = row.get("values", [""])[0]
        outlook[occ_code] = {
            "value": value,
            "label": value,
        }
    return outlook


def derive_category(code: str, label: str) -> str:
    # Use the first digit of ISCO/AML code as a rough major group fallback.
    return code[:1] if code else label.split(" ")[0]


def load_extra_attrs(path: Optional[str]) -> Dict[str, dict]:
    """Load optional per-occupation attributes from a CSV.

    Expected columns (any subset):
      code, median_pay_annual, entry_education, outlook_pct, outlook_desc
    Values are used to override/fill missing fields from PxWeb.
    """

    if not path:
        return {}
    if not os.path.exists(path):
        print(f"Warning: extras_csv not found at {path}; ignoring")
        return {}

    extras: Dict[str, dict] = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("code") or "").strip()
            if not code:
                continue
            extras[code] = {
                "median_pay_annual": (row.get("median_pay_annual") or "").strip(),
                "entry_education": (row.get("entry_education") or "").strip(),
                "work_experience": (row.get("work_experience") or "").strip(),
                "training": (row.get("training") or "").strip(),
                "outlook_pct": (row.get("outlook_pct") or "").strip(),
                "outlook_desc": (row.get("outlook_desc") or "").strip(),
            }
    return extras


def load_ai_exposure(path: str = "scores.json") -> Dict[str, dict]:
    """Load AI exposure scores from scores.json.

    Returns a dict keyed by occupation slug with exposure score and rationale.
    Uses fuzzy matching to handle Finnish occupation naming (which includes codes).
    """
    if not os.path.exists(path):
        print(f"Warning: scores.json not found at {path}; skipping AI exposure data")
        return {}

    with open(path) as f:
        data = json.load(f)

    # Build a mapping from normalized English titles to exposure data
    # This helps match Finnish occupation names (which have codes) to English titles
    exposure_by_title: Dict[str, dict] = {}

    for entry in data:
        title = entry.get("title", "")
        slug = entry.get("slug", "")
        if title and slug:
            # Create normalized versions for fuzzy matching
            normalized_title = title.lower().replace(" and ", " ").replace(" & ", " ")
            exposure_by_title[normalized_title] = {
                "slug": slug,
                "exposure": entry.get("exposure"),
                "rationale": entry.get("rationale", ""),
            }
            # Also store by slug
            exposure_by_title[slug] = exposure_by_title[normalized_title]

    print(f"Loaded AI exposure data for {len(exposure_by_title)} occupations/titles")
    return exposure_by_title


def match_ai_exposure(
    finnish_title: str, ai_exposure: Dict[str, dict]
) -> Tuple[Optional[int], str]:
    """Match a Finnish occupation title to AI exposure data.

    Extracts the occupation name from Finnish title and tries to match
    against English occupation titles in the exposure data using substring matching.
    """
    # Remove the occupation code prefix (e.g., "2411 ", "1120 ")
    # Finnish titles look like: "2411 Accountants (Level 4)"
    cleaned = re.sub(r"^\d+\.?\s*", "", finnish_title)  # Remove leading code
    cleaned = re.sub(r"\s*\(Level \d+\)", "", cleaned)  # Remove level suffix
    cleaned = cleaned.lower().strip()

    # Try exact match first
    if cleaned in ai_exposure:
        data = ai_exposure[cleaned]
        return data.get("exposure"), data.get("rationale", "")

    # Try substring matching - check if cleaned title is contained in any exposure key
    for key, data in ai_exposure.items():
        if isinstance(key, str) and key and (cleaned in key or key in cleaned):
            return data.get("exposure"), data.get("rationale", "")

    # Try matching words
    cleaned_words = set(cleaned.replace("-", " ").split())

    best_match = None
    best_score = 0

    for key, data in ai_exposure.items():
        if not key or len(key) < 3:
            continue
        key_words = set(key.replace("-", " ").split())

        # Calculate word overlap
        overlap = len(cleaned_words & key_words)
        if overlap > best_score and overlap >= 2:
            best_score = overlap
            best_match = data

    if best_match:
        return best_match.get("exposure"), best_match.get("rationale", "")

    return None, ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="statfin_config.json", help="Path to StatFin config JSON"
    )
    parser.add_argument(
        "--scores", default="scores.json", help="Path to AI exposure scores JSON"
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    emp_cfg = cfg.get("employment")
    wage_cfg = cfg.get("wages")
    outlook_cfg = cfg.get("outlook")
    extras_path = cfg.get("extras_csv")
    min_outlook_coverage = float(cfg.get("min_outlook_coverage", 0.0))
    strict_outlook_coverage = bool(cfg.get("strict_outlook_coverage", False))

    if not emp_cfg:
        raise SystemExit("employment config is required")

    employment, occupations = fetch_employment(emp_cfg)
    wage_values = fetch_wages(wage_cfg, [c for c, _ in occupations]) if wage_cfg else {}
    outlook_values = (
        fetch_outlook(outlook_cfg, [c for c, _ in occupations]) if outlook_cfg else {}
    )
    extra_attrs = load_extra_attrs(extras_path)
    ai_exposure = load_ai_exposure(args.scores)

    # Build normalized rows
    rows = []
    occ_entries = []
    
    # Build a fallback map for Level 4 codes to inherit from Level 5 (dotted) codes
    fallback_map = {}
    for code, title in occupations:
        if code.endswith("."):
            base_code = code.rstrip(".")
            fallback_map[base_code] = code
    
    for code, title in occupations:
        # Skip Unknown occupations (codes starting with X)
        if code.startswith("X"):
            continue
            
        slug = slugify(title)
        category = derive_category(code, title)
        pay_monthly = wage_values.get(code)
        pay_annual = round(pay_monthly * 12) if pay_monthly else None
        pay_source = "wages_statfin" if pay_monthly else ""
        outlook_entry = outlook_values.get(code, {})

        # Apply overrides from extras CSV when present
        # Try exact match first, then normalized (without trailing dots)
        extra = extra_attrs.get(code, {})
        if not extra:
            normalized_code = code.rstrip(".")
            extra = extra_attrs.get(normalized_code, {})

        # If still no pay data, try to inherit from Level 5 (dotted) variant
        if not pay_annual and code in fallback_map:
            fallback_code = fallback_map[code]
            fallback_pay_monthly = wage_values.get(fallback_code)
            if fallback_pay_monthly:
                pay_annual = round(fallback_pay_monthly * 12)
                pay_source = "wages_statfin"

        if not pay_annual:
            try:
                pay_annual = int(float(extra.get("median_pay_annual", "") or 0)) or None
                if pay_annual:
                    pay_source = "extras_csv"
            except ValueError:
                pay_annual = None
        
        education_val = extra.get("entry_education") or ""
        work_experience_val = extra.get("work_experience") or ""
        training_val = extra.get("training") or ""
        outlook_pct_val = outlook_entry.get("value", "") or extra.get("outlook_pct") or ""
        outlook_desc_val = outlook_entry.get("label", "") or extra.get("outlook_desc", "")
        
        # If still no data (education/outlook/etc), try to inherit from Level 5 variant
        if code in fallback_map:
            fallback_code = fallback_map[code]
            fallback_outlook = outlook_values.get(fallback_code, {})
            fallback_extra = extra_attrs.get(fallback_code, {})
            
            # Inherit outlook if missing
            if not outlook_desc_val and not outlook_pct_val:
                outlook_pct_val = fallback_outlook.get("value", "") or fallback_extra.get("outlook_pct") or ""
                outlook_desc_val = fallback_outlook.get("label", "") or fallback_extra.get("outlook_desc", "")
            
            # Inherit education fields if missing
            if not education_val:
                education_val = fallback_extra.get("entry_education") or ""
            if not work_experience_val:
                work_experience_val = fallback_extra.get("work_experience") or ""
            if not training_val:
                training_val = fallback_extra.get("training") or ""
        
        if outlook_entry.get("label"):
            outlook_source = "outlook_statfin"
        elif extra.get("outlook_desc") or extra.get("outlook_pct"):
            outlook_source = "extras_csv"
        else:
            outlook_source = ""

        # Get AI exposure data by matching Finnish title to English titles
        exposure_val, exposure_rationale = match_ai_exposure(title, ai_exposure)

        rows.append(
            {
                "title": title,
                "category": category,
                "slug": slug,
                "soc_code": code,
                "median_pay_annual": str(pay_annual) if pay_annual else "",
                "median_pay_source": pay_source,
                "median_pay_hourly": "",
                "entry_education": education_val,
                "work_experience": work_experience_val,
                "training": training_val,
                "num_jobs_2024": str(employment.get(code, "")),
                "projected_employment_2034": "",
                "outlook_pct": outlook_pct_val,
                "outlook_desc": outlook_desc_val,
                "outlook_source": outlook_source,
                "employment_change": "",
                "exposure": str(exposure_val) if exposure_val is not None else "",
                "exposure_rationale": exposure_rationale,
                "url": "",
            }
        )
        occ_entries.append(
            {
                "title": title,
                "url": "",
                "slug": slug,
                "category": category,
                "code": code,
            }
        )

    fieldnames = [
        "title",
        "category",
        "slug",
        "soc_code",
        "median_pay_annual",
        "median_pay_source",
        "median_pay_hourly",
        "entry_education",
        "work_experience",
        "training",
        "num_jobs_2024",
        "projected_employment_2034",
        "outlook_pct",
        "outlook_desc",
        "outlook_source",
        "employment_change",
        "exposure",
        "exposure_rationale",
        "url",
    ]

    with open("occupations.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open("occupations.json", "w") as f:
        json.dump(occ_entries, f, indent=2)

    with_outlook = sum(1 for r in rows if r.get("outlook_desc") or r.get("outlook_pct"))
    outlook_coverage = (with_outlook / len(rows)) if rows else 0.0

    print(f"Wrote {len(rows)} rows to occupations.csv and occupations.json")
    print(
        f"Outlook coverage: {with_outlook}/{len(rows)} ({100 * outlook_coverage:.1f}%)"
    )

    if outlook_coverage < min_outlook_coverage:
        msg = (
            f"Outlook coverage {outlook_coverage:.3f} is below min_outlook_coverage "
            f"{min_outlook_coverage:.3f}."
        )
        if strict_outlook_coverage:
            raise SystemExit(msg)
        print(f"Warning: {msg}")


if __name__ == "__main__":
    main()
