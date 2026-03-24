"""Generate AI exposure scores for occupations without using API.

Uses rule-based inference based on occupation category, education level,
and occupation characteristics to estimate AI exposure (0-10 scale).

Usage:
    uv run python infer_ai_exposure.py
"""

import json
import os
import re
from typing import Dict, List, Tuple


def get_category(code: str) -> str:
    """Extract major category from occupation code."""
    return code[0] if code else ""


def calculate_ai_exposure(
    title: str, category: str, education: str, outlook: int, jobs: int
) -> Tuple[int, str]:
    """Calculate AI exposure score based on occupation characteristics.

    Returns: (score 0-10, rationale)
    """

    # Category-based base scores
    category_base = {
        "0": 3,  # Armed forces - physical security, command
        "1": 7,  # Managers - high digital/analytical work
        "2": 8,  # Professionals - knowledge work, highly digital
        "3": 6,  # Technicians - mixed digital/physical
        "4": 7,  # Clerical support - administrative, highly automatable
        "5": 4,  # Service workers - customer interaction, physical
        "6": 2,  # Agricultural - physical, outdoor work
        "7": 3,  # Craft workers - manual skills, physical
        "8": 5,  # Machine operators - routine, some automation risk
        "9": 2,  # Elementary - simple physical tasks
    }

    base_score = category_base.get(category, 5)

    # Education adjustment (higher education = more digital/knowledge work)
    edu_adjustment = 0
    if "Doctoral" in education:
        edu_adjustment = 2
    elif "Master's" in education:
        edu_adjustment = 1
    elif "Bachelor's" in education:
        edu_adjustment = 1
    elif "Basic education" in education:
        edu_adjustment = -1

    # Keyword-based adjustments
    title_lower = title.lower()

    # High AI exposure keywords (+2)
    if any(
        kw in title_lower
        for kw in [
            "software",
            "programmer",
            "data",
            "analyst",
            "accountant",
            "clerk",
            "secretary",
            "administrative",
            "bookkeeper",
            "telemarketer",
            "cashier",
            "computer",
            "information",
        ]
    ):
        base_score += 2

    # Medium-high AI exposure (+1)
    elif any(
        kw in title_lower
        for kw in [
            "manager",
            "engineer",
            "designer",
            "writer",
            "editor",
            "marketing",
            "finance",
            "planner",
            "consultant",
            "lawyer",
        ]
    ):
        base_score += 1

    # Low AI exposure (-1)
    elif any(
        kw in title_lower
        for kw in [
            "cleaner",
            "driver",
            "mechanic",
            "repair",
            "construction",
            "agriculture",
            "farmer",
            "fisher",
            "care",
            "nurse",
        ]
    ):
        base_score -= 1

    # Physical/manual work keywords (-2)
    if any(
        kw in title_lower
        for kw in [
            "hand",
            "manual",
            "physical",
            "craft",
            "welder",
            "carpenter",
            "plumber",
            "electrician",
            "mason",
            "painter",
            "hairdresser",
        ]
    ):
        base_score -= 2

    # Apply education adjustment
    base_score += edu_adjustment

    # Clamp to 0-10
    score = max(0, min(10, base_score))

    # Generate rationale
    rationale = generate_rationale(title, category, education, score)

    return score, rationale


def generate_rationale(title: str, category: str, education: str, score: int) -> str:
    """Generate explanation for the AI exposure score."""

    category_names = {
        "0": "armed forces",
        "1": "managerial",
        "2": "professional",
        "3": "technical",
        "4": "clerical",
        "5": "service",
        "6": "agricultural",
        "7": "craft",
        "8": "machine operation",
        "9": "elementary",
    }

    cat_name = category_names.get(category, "occupation")

    if score >= 8:
        return (
            f"This {cat_name} occupation involves extensive digital knowledge work "
            f"and analytical tasks that are highly susceptible to AI automation and "
            f"augmentation. The work is primarily computer-based with limited physical "
            f"requirements, making it highly exposed to AI capabilities."
        )

    elif score >= 6:
        return (
            f"This {cat_name} occupation has significant AI exposure due to substantial "
            f"digital and analytical components. While some aspects involve human judgment "
            f"or physical presence, many core tasks can be automated or augmented by AI "
            f"systems, particularly administrative and routine decision-making functions."
        )

    elif score >= 4:
        return (
            f"This {cat_name} occupation has moderate AI exposure. While some tasks "
            f"(particularly administrative and routine aspects) are susceptible to "
            f"automation, the role requires physical presence, manual skills, or "
            f"interpersonal interaction that provides a buffer against full automation."
        )

    elif score >= 2:
        return (
            f"This {cat_name} occupation has low AI exposure. The work is primarily "
            f"physical and hands-on, requiring manual dexterity, real-time physical "
            f"coordination, or outdoor work in unpredictable environments. AI's impact "
            f"is limited to peripheral support functions."
        )

    else:
        return (
            f"This {cat_name} occupation has minimal AI exposure. The work is almost "
            f"entirely physical, requiring hands-on skills, manual labor, or real-time "
            f"physical interaction with the environment. These tasks cannot be meaningfully "
            f"automated by current or near-term AI technologies."
        )


def load_site_data() -> List[dict]:
    """Load occupation data from site/data.json."""
    if not os.path.exists("site/data.json"):
        raise FileNotFoundError(
            "site/data.json not found. Run build_site_data.py first."
        )

    with open("site/data.json") as f:
        return json.load(f)


def load_existing_scores() -> Dict[str, dict]:
    """Load existing AI exposure scores."""
    # Check data/scores.json first (preferred location)
    scores_path = (
        "data/scores.json" if os.path.exists("data/scores.json") else "scores.json"
    )
    if not os.path.exists(scores_path):
        return {}

    with open(scores_path) as f:
        scores_list = json.load(f)

    # Index by slug
    return {s["slug"]: s for s in scores_list}


def main():
    print("Loading occupation data...")
    occupations = load_site_data()
    existing_scores = load_existing_scores()

    print(f"Loaded {len(occupations)} occupations")
    print(f"Found {len(existing_scores)} existing scores")

    # Count missing
    missing = [occ for occ in occupations if occ.get("exposure") is None]
    print(
        f"\nGenerating AI exposure scores for {len(missing)} occupations without scores..."
    )

    # Process all occupations
    updated_scores = list(existing_scores.values())
    added_count = 0

    for occ in occupations:
        slug = occ["slug"]

        # Skip if already has score from API
        if slug in existing_scores:
            continue

        # Skip if already has exposure in site data (from CSV)
        if occ.get("exposure") is not None:
            continue

        # Extract occupation code from title
        match = re.match(r"^(\d+\.?)[\s\.]", occ["title"])
        code = match.group(1).rstrip(".") if match else ""

        # Calculate exposure
        exposure, rationale = calculate_ai_exposure(
            occ["title"],
            occ["category"],
            occ.get("education", ""),
            occ.get("outlook") or 0,
            occ.get("jobs") or 0,
        )

        # Add to scores
        updated_scores.append(
            {
                "title": occ["title"],
                "slug": slug,
                "exposure": exposure,
                "rationale": rationale,
            }
        )
        added_count += 1

    # Write updated scores to data directory
    os.makedirs("data", exist_ok=True)
    with open("data/scores.json", "w") as f:
        json.dump(updated_scores, f, indent=2)

    print(f"\n✓ Updated data/scores.json")
    print(f"  Total scores: {len(updated_scores)}")
    print(f"  Newly inferred: {added_count}")
    print(f"  Existing (from API): {len(existing_scores)}")

    print("\nNext steps:")
    print("  1. Run: uv run python fetch_statfin.py --config statfin_config.json")
    print("  2. Run: uv run python build_site_data.py")
    print("  3. Refresh your browser")


if __name__ == "__main__":
    main()
