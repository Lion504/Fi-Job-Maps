"""
Score each occupation's AI exposure using Google AI Studio or Vertex AI (Gemini).

Reads occupation data from data/occupations.csv, sends each to an LLM with a scoring
rubric, and collects structured scores. Results are cached incrementally to
data/scores.json so the script can be resumed if interrupted.

NOTE: If data/scores.json contains old US-sourced scores (English slugs like
'accountants-and-auditors'), re-run this script to replace them with Finnish
occupation data scored from data/occupations.csv.

--- Backend selection (via .env) ---

Option A — Google AI Studio (free tier, simple API key):
    GOOGLE_API_KEY=your_key

Option B — Vertex AI with API key (GCP credits):
    VERTEX_PROJECT=your-gcp-project-id
    VERTEX_API_KEY=your-vertex-api-key     ← from GCP Console → APIs & Services → Credentials

Vertex AI is preferred (auto) when VERTEX_PROJECT is set.

Usage:
    uv run python src/score.py
    uv run python src/score.py --model gemini-3.1-flash-lite-preview
    uv run python src/score.py --workers 10          # more parallel calls
    uv run python src/score.py --start 0 --end 10    # test on first 10
    uv run python src/score.py --backend aistudio    # force AI Studio
    uv run python src/score.py --backend vertex      # force Vertex AI
"""

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite-preview")
OUTPUT_FILE = os.getenv("SCORES_OUTPUT_FILE", "data/scores.json")

# AI Studio
API_KEY = os.getenv("GOOGLE_API_KEY")

# Vertex AI
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
VERTEX_API_KEY = os.getenv("VERTEX_API_KEY")  # API key from GCP Console (no gcloud login needed)

SYSTEM_PROMPT = """\
You are an expert analyst evaluating how exposed different occupations are to \
AI. You will be given structured information about a Finnish occupation \
(titles use ISCO/AML codes, pay is in EUR, and outlook may come from the \
Occupational Barometer demand categories).

Rate the occupation's overall **AI Exposure** on a scale from 0 to 10.

AI Exposure measures: how much will AI reshape this occupation? Consider both \
direct effects (AI automating tasks currently done by humans) and indirect \
effects (AI making each worker so productive that fewer are needed).

A key signal is whether the job's work product is fundamentally digital. If \
the job can be done entirely from a home office on a computer — writing, \
coding, analyzing, communicating — then AI exposure is inherently high (7+), \
because AI capabilities in digital domains are advancing rapidly. Even if \
today's AI can't handle every aspect of such a job, the trajectory is steep \
and the ceiling is very high. Conversely, jobs requiring physical presence, \
manual skill, or real-time human interaction in the physical world have a \
natural barrier to AI exposure.

Use these anchors to calibrate your score:

- **0-1: Minimal exposure.** The work is almost entirely physical, hands-on, \
or requires real-time human presence in unpredictable environments. AI has \
essentially no impact on daily work. \
Examples: roofer, landscaper, commercial diver.

- **2-3: Low exposure.** Mostly physical or interpersonal work. AI might help \
with minor peripheral tasks (scheduling, paperwork) but doesn't touch the \
core job. \
Examples: electrician, plumber, firefighter, dental hygienist.

- **4-5: Moderate exposure.** A mix of physical/interpersonal work and \
knowledge work. AI can meaningfully assist with the information-processing \
parts but a substantial share of the job still requires human presence. \
Examples: registered nurse, police officer, veterinarian.

- **6-7: High exposure.** Predominantly knowledge work with some need for \
human judgment, relationships, or physical presence. AI tools are already \
useful and workers using AI may be substantially more productive. \
Examples: teacher, manager, accountant, journalist.

- **8-9: Very high exposure.** The job is almost entirely done on a computer. \
All core tasks — writing, coding, analyzing, designing, communicating — are \
in domains where AI is rapidly improving. The occupation faces major \
restructuring. \
Examples: software developer, graphic designer, translator, data analyst, \
paralegal, copywriter.

- **10: Maximum exposure.** Routine information processing, fully digital, \
with no physical component. AI can already do most of it today. \
Examples: data entry clerk, telemarketer.

Respond with ONLY a JSON object in this exact format, no other text:
{
  "exposure": <0-10>,
  "rationale": "<2-3 sentences explaining the key factors>"
}"""


# ── Backend implementations ────────────────────────────────────────────────────

def _parse_response_text(text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


def score_aistudio(client: httpx.Client, text: str, model: str) -> dict:
    """Score via Google AI Studio REST API (API key auth)."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={API_KEY}"
    )
    response = client.post(
        url,
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": SYSTEM_PROMPT + "\n\n---\n\n" + text}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_response_text(content)


def score_vertex(client: httpx.Client, text: str, model: str) -> dict:
    """Score via Vertex AI global endpoint (required for preview models).

    Uses the global endpoint (locations/global) so preview and non-preview
    models are all reachable without region-specific restrictions.
    Auth: x-goog-api-key header (VERTEX_API_KEY from .env).
    """
    # Global endpoint: works for all models incl. preview. Regional endpoint
    # (e.g. europe-west4-aiplatform.googleapis.com) 404s on preview models.
    url = (
        f"https://aiplatform.googleapis.com/v1/"
        f"projects/{VERTEX_PROJECT}/locations/global/"
        f"publishers/google/models/{model}:generateContent"
    )
    headers = {"x-goog-api-key": VERTEX_API_KEY}

    response = client.post(
        url,
        headers=headers,
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": SYSTEM_PROMPT + "\n\n---\n\n" + text}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_response_text(content)


# ── Worker (runs in thread pool) ──────────────────────────────────────────────

def _build_text(occ: dict, csv_rows: dict) -> str | None:
    """Build the prompt text for one occupation. Returns None if no data."""
    slug = occ["slug"]
    md_path = f"pages/{slug}.md"
    if os.path.exists(md_path):
        with open(md_path) as f:
            return f.read()
    if slug in csv_rows:
        row = csv_rows[slug]
        # Use isco_code if available, fall back to soc_code for backward compat
        code = row.get("isco_code") or row.get("soc_code", "")
        parts = [
            f"Occupation: {occ['title']}",
            f"Code: {code}",
            f"Category: {row.get('category', '')}",
            f"Pay (annual EUR): {row.get('median_pay_annual', '')}",
            f"Employment (latest): {row.get('num_jobs') or row.get('num_jobs_2024', '')}",
            f"Outlook: {row.get('outlook_desc', '') or row.get('outlook_pct', '')}",
            f"Education: {row.get('entry_education', '')}",
            f"Work Experience: {row.get('work_experience', '')}",
            f"Training: {row.get('training', '')}",
        ]
        return "\n".join(parts)
    return None


def _score_one(occ: dict, csv_rows: dict, score_fn, model: str) -> tuple:
    """
    Worker function: scores one occupation.
    Creates its own httpx.Client for thread safety.
    Returns (slug, title, result_dict) or raises on error.
    """
    text = _build_text(occ, csv_rows)
    if text is None:
        return occ["slug"], occ["title"], None  # None = skip

    with httpx.Client() as client:
        result = score_fn(client, text, model)

    return occ["slug"], occ["title"], result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Score occupations for AI exposure using Gemini (AI Studio or Vertex AI)"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--backend",
        choices=["aistudio", "vertex", "auto"],
        default="auto",
        help=(
            "API backend: 'vertex' uses Vertex AI (VERTEX_PROJECT required), "
            "'aistudio' uses Google AI Studio (GOOGLE_API_KEY required), "
            "'auto' prefers Vertex if VERTEX_PROJECT is set (default: auto)"
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel API calls (default: 5)",
    )
    parser.add_argument(
        "--start", type=int, default=0, help="Start index for batch processing"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="End index for batch processing"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between submitting each job in seconds (default: 0, use to throttle)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-score even if already cached"
    )
    args = parser.parse_args()

    # ── Resolve backend ──────────────────────────────────────────────────────
    use_vertex = False
    if args.backend == "vertex":
        use_vertex = True
    elif args.backend == "aistudio":
        use_vertex = False
    else:  # auto
        use_vertex = bool(VERTEX_PROJECT)

    if use_vertex:
        if not VERTEX_PROJECT:
            print("Error: VERTEX_PROJECT not set. Add it to .env:")
            print("  VERTEX_PROJECT=your-gcp-project-id")
            print("  VERTEX_API_KEY=your-api-key   (from GCP Console → APIs & Services → Credentials)")
            return 1
        if not VERTEX_API_KEY:
            print("Error: VERTEX_API_KEY not set. Add it to .env:")
            print("  VERTEX_API_KEY=your-api-key   (from GCP Console → APIs & Services → Credentials)")
            return 1
        print(f"Backend: Vertex AI (API key)  project={VERTEX_PROJECT}  (global endpoint)")
        def score_fn(client, text, model):
            return score_vertex(client, text, model)
    else:
        if not API_KEY:
            print("Error: GOOGLE_API_KEY not set in environment or .env file")
            print("Get your API key from https://aistudio.google.com/apikey")
            print("Or set VERTEX_PROJECT to use Vertex AI instead.")
            return 1
        print("Backend: Google AI Studio")
        score_fn = score_aistudio

    # ── Load data ────────────────────────────────────────────────────────────
    with open("data/occupations.json") as f:
        occupations = json.load(f)

    csv_rows = {}
    if os.path.exists("data/occupations.csv"):
        import csv
        with open("data/occupations.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_rows[row["slug"]] = row

    subset = occupations[args.start : args.end]

    # Load existing scores
    scores: dict = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                scores[entry["slug"]] = entry

    # Only score occupations not yet cached
    todo = [occ for occ in subset if occ["slug"] not in scores]

    print(f"Model:   {args.model}")
    print(f"Workers: {args.workers} parallel calls")
    print(f"Total:   {len(subset)} occupations  |  cached: {len(scores)}  |  to score: {len(todo)}")

    if not todo:
        print("Nothing to score — all cached.")
        return 0

    # ── Parallel scoring ──────────────────────────────────────────────────────
    errors: list[str] = []
    completed = 0
    save_lock = threading.Lock()

    def save_scores():
        with open(OUTPUT_FILE, "w") as f:
            json.dump(list(scores.values()), f, indent=2)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit all jobs
        future_to_occ = {}
        for i, occ in enumerate(todo):
            future = executor.submit(_score_one, occ, csv_rows, score_fn, args.model)
            future_to_occ[future] = occ
            if args.delay:
                time.sleep(args.delay)

        # Collect results as they complete
        for future in as_completed(future_to_occ):
            occ = future_to_occ[future]
            completed += 1
            try:
                slug, title, result = future.result()
                if result is None:
                    print(f"  [{completed}/{len(todo)}] SKIP {slug} (no data)", flush=True)
                else:
                    scores[slug] = {"slug": slug, "title": title, **result}
                    print(
                        f"  [{completed}/{len(todo)}] {title}  →  exposure={result['exposure']}",
                        flush=True,
                    )
                    # Checkpoint: save after every completion (thread-safe)
                    with save_lock:
                        save_scores()
            except Exception as e:
                print(f"  [{completed}/{len(todo)}] ERROR {occ['title']}: {e}", flush=True)
                errors.append(occ["slug"])

    print(f"\nDone. Scored {len(scores)} total ({len(todo) - len(errors)} new), {len(errors)} errors.")
    if errors:
        print(f"Errors: {errors}")

    # Summary stats
    vals = [s for s in scores.values() if "exposure" in s]
    if vals:
        avg = sum(s["exposure"] for s in vals) / len(vals)
        by_score: dict = {}
        for s in vals:
            bucket = s["exposure"]
            by_score[bucket] = by_score.get(bucket, 0) + 1
        print(f"\nAverage exposure across {len(vals)} occupations: {avg:.1f}")
        print("Distribution:")
        for k in sorted(by_score):
            bar = "█" * min(by_score[k], 60)
            print(f"  {k:2d}: {bar} ({by_score[k]})")

    return 0


if __name__ == "__main__":
    exit(main())
