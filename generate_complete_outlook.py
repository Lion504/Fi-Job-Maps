"""Generate comprehensive outlook data for all Level 4 and Level 5 occupations.

Fills in missing outlook data by analyzing patterns in existing extras.csv
and applying category-based inference for occupations without data.

Usage:
    uv run python generate_complete_outlook.py
"""

import csv
import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple


def load_existing_extras() -> Dict[str, dict]:
    """Load existing outlook data from extras.csv."""
    if not os.path.exists("extras.csv"):
        return {}
    
    extras = {}
    with open("extras.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("code", "").strip()
            if code:
                extras[code] = {
                    "outlook_pct": row.get("outlook_pct", "").strip(),
                    "outlook_desc": row.get("outlook_desc", "").strip(),
                    "education": row.get("entry_education", "").strip(),
                    "work_experience": row.get("work_experience", "").strip(),
                    "training": row.get("training", "").strip(),
                }
    return extras


def load_occupations() -> List[Tuple[str, str]]:
    """Load all occupations from occupations.json."""
    if not os.path.exists("occupations.json"):
        raise FileNotFoundError("occupations.json not found. Run fetch_statfin.py first.")
    
    with open("occupations.json") as f:
        data = json.load(f)
    
    return [(occ["code"], occ["title"]) for occ in data]


def get_category(code: str) -> str:
    """Extract major category from occupation code."""
    return code[0] if code else ""


def calculate_category_averages(extras: Dict[str, dict]) -> Dict[str, dict]:
    """Calculate average outlook by major category."""
    category_outlooks = defaultdict(list)
    
    for code, data in extras.items():
        outlook_pct = data.get("outlook_pct", "")
        if outlook_pct and outlook_pct.lstrip("-+").isdigit():
            category = get_category(code)
            category_outlooks[category].append(int(outlook_pct))
    
    averages = {}
    for cat, outlooks in category_outlooks.items():
        if outlooks:
            avg = sum(outlooks) / len(outlooks)
            averages[cat] = {
                "outlook_pct": round(avg),
                "outlook_desc": describe_outlook(round(avg)),
            }
    
    return averages


def describe_outlook(pct: int) -> str:
    """Map outlook percentage to descriptive label."""
    if pct >= 10:
        return "Very good prospects"
    elif pct >= 7:
        return "Good prospects"
    elif pct >= 4:
        return "Moderate prospects"
    elif pct >= 1:
        return "Below average"
    elif pct >= -2:
        return "Stable"
    elif pct >= -5:
        return "Labor surplus"
    else:
        return "Declining significantly"


def infer_outlook(code: str, title: str, extras: Dict[str, dict], 
                  category_avg: Dict[str, dict]) -> Tuple[str, str]:
    """Infer outlook for an occupation without data."""
    category = get_category(code)
    
    # Check if Level 5 variant exists
    if not code.endswith("."):
        dotted_code = code + "."
        if dotted_code in extras:
            return (extras[dotted_code].get("outlook_pct", ""),
                    extras[dotted_code].get("outlook_desc", ""))
    
    # Check if Level 4 variant exists (for Level 5)
    if code.endswith("."):
        base_code = code.rstrip(".")
        if base_code in extras:
            return (extras[base_code].get("outlook_pct", ""),
                    extras[base_code].get("outlook_desc", ""))
    
    # Use category average
    if category in category_avg:
        return (str(category_avg[category]["outlook_pct"]),
                category_avg[category]["outlook_desc"])
    
    # Default: stable outlook
    return ("0", "Stable")


def infer_education(code: str, title: str, extras: Dict[str, dict]) -> Dict[str, str]:
    """Infer education requirements based on occupation code patterns."""
    category = get_category(code)
    
    # Check variants first
    if not code.endswith("."):
        dotted_code = code + "."
        if dotted_code in extras and extras[dotted_code].get("education"):
            return {
                "education": extras[dotted_code]["education"],
                "work_experience": extras[dotted_code].get("work_experience", ""),
                "training": extras[dotted_code].get("training", ""),
            }
    
    if code.endswith("."):
        base_code = code.rstrip(".")
        if base_code in extras and extras[base_code].get("education"):
            return {
                "education": extras[base_code]["education"],
                "work_experience": extras[base_code].get("work_experience", ""),
                "training": extras[base_code].get("training", ""),
            }
    
    # Category-based inference
    education_map = {
        "0": ("Upper secondary", "None", "Military training"),  # Armed forces
        "1": ("Bachelor's degree", "3-5 years", "None"),  # Managers
        "2": ("Bachelor's degree", "2-4 years", "None"),  # Professionals
        "3": ("Upper secondary", "None", "Vocational training"),  # Technicians
        "4": ("Upper secondary", "None", "None"),  # Clerical support
        "5": ("Upper secondary", "None", "None"),  # Service workers
        "6": ("Upper secondary", "None", "Vocational training"),  # Skilled agricultural
        "7": ("Upper secondary", "None", "Vocational training"),  # Craft workers
        "8": ("Upper secondary", "None", "Vocational training"),  # Machine operators
        "9": ("None", "None", "None"),  # Elementary occupations
    }
    
    edu_data = education_map.get(category, ("Upper secondary", "None", "None"))
    return {
        "education": edu_data[0],
        "work_experience": edu_data[1],
        "training": edu_data[2],
    }


def main():
    print("Loading existing data...")
    extras = load_existing_extras()
    occupations = load_occupations()
    
    print(f"Loaded {len(extras)} existing outlook entries")
    print(f"Loaded {len(occupations)} total occupations")
    
    print("\nCalculating category averages...")
    category_avg = calculate_category_averages(extras)
    for cat, data in sorted(category_avg.items()):
        print(f"  Category {cat}: {data['outlook_pct']}% ({data['outlook_desc']})")
    
    print("\nGenerating complete outlook data...")
    complete_data = []
    added_count = 0
    
    for code, title in occupations:
        # Skip aggregate categories
        if "Level" not in title:
            continue
        
        # Extract level
        if "(Level 4)" in title or "(Level 5)" in title:
            if code in extras:
                # Use existing data
                complete_data.append({
                    "code": code,
                    "median_pay_annual": "",
                    "entry_education": extras[code].get("education", ""),
                    "work_experience": extras[code].get("work_experience", ""),
                    "training": extras[code].get("training", ""),
                    "outlook_pct": extras[code].get("outlook_pct", ""),
                    "outlook_desc": extras[code].get("outlook_desc", ""),
                })
            else:
                # Infer outlook
                outlook_pct, outlook_desc = infer_outlook(code, title, extras, category_avg)
                edu_data = infer_education(code, title, extras)
                
                complete_data.append({
                    "code": code,
                    "median_pay_annual": "",
                    "entry_education": edu_data["education"],
                    "work_experience": edu_data["work_experience"],
                    "training": edu_data["training"],
                    "outlook_pct": outlook_pct,
                    "outlook_desc": outlook_desc,
                })
                added_count += 1
    
    # Write to new extras file
    fieldnames = [
        "code",
        "median_pay_annual",
        "entry_education",
        "work_experience",
        "training",
        "outlook_pct",
        "outlook_desc",
    ]
    
    output_file = "extras_complete.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(complete_data)
    
    print(f"\n✓ Wrote {len(complete_data)} occupations to {output_file}")
    print(f"  - {len(extras)} from existing extras.csv")
    print(f"  - {added_count} newly inferred")
    print(f"\nBackup existing extras.csv and replace with extras_complete.csv to use.")


if __name__ == "__main__":
    main()
