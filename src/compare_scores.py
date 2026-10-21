"""
Compare two AI exposure score files on the occupations they share.

Typical use: score a small fixed sample into a trial file, then compare it with
the published scores before re-scoring everything.

    SCORES_OUTPUT_FILE=data/scores_trial.json uv run python src/score.py --force --sample 40
    uv run python src/compare_scores.py data/scores_trial.json data/scores.json

Differences are A - B (first file minus second).

Usage:
    uv run python src/compare_scores.py A.json [B.json] [--level 4] [--top 15]
"""

import argparse
import json
import re


def load_scores(path: str) -> dict:
    with open(path) as f:
        return {s["slug"]: s for s in json.load(f) if s.get("exposure") is not None}


def score_level(entry: dict) -> int | None:
    """Level from the title ('... (Level 4)') or, failing that, the slug."""
    m = re.search(r"\(Level (\d+)\)", entry.get("title", "")) or re.search(
        r"-level-(\d+)$", entry["slug"]
    )
    return int(m.group(1)) if m else None


def models(scores: dict, slugs) -> str:
    names = sorted({scores[s].get("model") or "unknown" for s in slugs})
    return ", ".join(names)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two AI exposure score files on shared slugs"
    )
    parser.add_argument("a", help="First score file (e.g. a trial run)")
    parser.add_argument(
        "b",
        nargs="?",
        default="data/scores.json",
        help="Second score file (default: data/scores.json)",
    )
    parser.add_argument(
        "--level", type=int, default=None, help="Only compare this level"
    )
    parser.add_argument(
        "--top", type=int, default=15, help="Largest differences to list (default: 15)"
    )
    args = parser.parse_args()

    a = load_scores(args.a)
    b = load_scores(args.b)
    shared = [s for s in a if s in b]
    if args.level is not None:
        shared = [s for s in shared if score_level(a[s]) == args.level]

    print(f"A: {args.a}  ({len(a)} scores; model: {models(a, shared) or '-'})")
    print(f"B: {args.b}  ({len(b)} scores; model: {models(b, shared) or '-'})")
    if args.level is not None:
        print(f"Level: {args.level}")
    if not shared:
        print("No shared occupations to compare.")
        return 1

    diffs = {s: a[s]["exposure"] - b[s]["exposure"] for s in shared}
    n = len(diffs)
    mean_signed = sum(diffs.values()) / n
    mean_abs = sum(abs(d) for d in diffs.values()) / n
    exact = sum(1 for d in diffs.values() if d == 0)
    within1 = sum(1 for d in diffs.values() if abs(d) <= 1)

    print(f"\nShared occupations (N): {n}")
    print(f"Mean signed diff (A - B): {mean_signed:+.2f}")
    print(f"Mean absolute diff:       {mean_abs:.2f}")
    print(f"Exact match:              {100 * exact / n:.1f}%  ({exact})")
    print(f"Within 1 point:           {100 * within1 / n:.1f}%  ({within1})")

    largest = sorted(shared, key=lambda s: (-abs(diffs[s]), s))[: args.top]
    print(f"\nLargest differences (top {len(largest)}):")
    print(f"  {'A':>2} {'B':>2} {'A-B':>4}  Title")
    for s in largest:
        title = re.sub(r"\s*\(Level \d+\)\s*$", "", a[s].get("title") or s)
        print(
            f"  {a[s]['exposure']:>2} {b[s]['exposure']:>2} {diffs[s]:>+4}  {title}"
        )
    return 0


if __name__ == "__main__":
    exit(main())
