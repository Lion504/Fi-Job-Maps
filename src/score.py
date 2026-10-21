"""
Score each occupation's AI exposure using the Claude API, Google AI Studio or
Vertex AI (Gemini).

Reads the occupation list from data/occupations.json, sends each occupation's
title and classification code to an LLM with a scoring rubric, and collects
structured scores. Only the finest level shown on the site is scored
(--level, default TREE_LEVEL or 4); the site derives group scores from it.
Results are cached incrementally to data/scores.json (or SCORES_OUTPUT_FILE)
so the script can be resumed if interrupted.

NOTE: If data/scores.json contains old US-sourced scores (English slugs like
'accountants-and-auditors'), re-run this script to replace them with Finnish
occupation data scored from data/occupations.csv.

--- Backend selection (via .env) ---

Option A — Claude API (Anthropic, default model claude-haiku-5-5):
    ANTHROPIC_API_KEY=your_key             ← from https://platform.claude.com/settings/keys
    CLAUDE_MODEL=claude-haiku-5-5          (optional)

Option B — Google AI Studio (free tier, simple API key):
    GOOGLE_API_KEY=your_key

Option C — Vertex AI with API key (GCP credits):
    VERTEX_PROJECT=your-gcp-project-id
    VERTEX_API_KEY=your-vertex-api-key     ← from GCP Console → APIs & Services → Credentials

With LLM_BACKEND=auto (default), Claude is used when ANTHROPIC_API_KEY is set,
then Vertex AI when VERTEX_PROJECT is set, then AI Studio.

Usage:
    uv run python src/score.py
    uv run python src/score.py --model gemini-3.1-flash-lite-preview
    uv run python src/score.py --workers 10          # more parallel calls
    uv run python src/score.py --start 0 --end 10    # test on first 10 of the level
    uv run python src/score.py --level 3             # score Level 3 groups instead of Level 4
    uv run python src/score.py --force               # re-score the level (e.g. after switching model)
    SCORES_OUTPUT_FILE=data/scores_trial.json uv run python src/score.py --force --sample 40
                                                     # trial run on a fixed random sample of 40;
                                                     # compare with src/compare_scores.py
    uv run python src/score.py --backend anthropic   # force Claude API
    uv run python src/score.py --backend aistudio    # force AI Studio
    uv run python src/score.py --backend vertex      # force Vertex AI
"""

import argparse
import json
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite-preview")
OUTPUT_FILE = os.getenv("SCORES_OUTPUT_FILE", "data/scores.json")
LLM_BACKEND = os.getenv("LLM_BACKEND", "auto")

# Claude API (the SDK reads ANTHROPIC_API_KEY itself)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")

# AI Studio
API_KEY = os.getenv("GOOGLE_API_KEY")

# Vertex AI
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
VERTEX_API_KEY = os.getenv("VERTEX_API_KEY")  # API key from GCP Console (no gcloud login needed)

SYSTEM_PROMPT = """\
You are an expert analyst evaluating how exposed different occupations are to \
AI. You will be given the title of a Finnish occupation and its code in the \
Finnish Classification of Occupations 2010, which follows ISCO-08.

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


class ExposureScore(BaseModel):
    exposure: int
    rationale: str


def score_anthropic(client: anthropic.Anthropic, text: str, model: str) -> dict:
    """Score via the Claude API with a structured JSON output."""
    response = client.messages.parse(
        model=model,
        max_tokens=4096,  # room for adaptive thinking plus the short JSON answer
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        # A short rubric judgement: low effort keeps thinking (and cost) small.
        output_config={"effort": "low"},
        output_format=ExposureScore,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("model declined to score this occupation")
    if response.stop_reason == "max_tokens" or response.parsed_output is None:
        raise RuntimeError(f"no score returned (stop_reason={response.stop_reason})")
    score = response.parsed_output
    if not 0 <= score.exposure <= 10:
        raise ValueError(f"exposure {score.exposure} outside 0-10")
    return {"exposure": score.exposure, "rationale": score.rationale}


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

def title_level(title: str) -> int | None:
    """Classification level from a StatFin title like '2411 Accountants (Level 4)'."""
    m = re.search(r"\(Level (\d+)\)\s*$", title or "")
    return int(m.group(1)) if m else None


def _build_text(occ: dict, csv_rows: dict) -> str | None:
    """Build the prompt text for one occupation. Returns None if no data.

    Only the title and classification code are sent: pay, employment, outlook
    and education say little about the tasks, can anchor the score, and
    outlook/education are partly the project's own category-level guesses.
    """
    slug = occ["slug"]
    md_path = f"pages/{slug}.md"
    if os.path.exists(md_path):
        with open(md_path) as f:
            return f.read()
    row = csv_rows.get(slug, {})
    # Use isco_code if available, fall back to soc_code for backward compat
    code = occ.get("code") or row.get("isco_code") or row.get("soc_code", "")
    # "2411 Accountants (Level 4)" -> "Accountants"; "216." -> "216"
    title = re.sub(r"\s*\(Level \d+\)\s*$", "", occ.get("title", ""))
    title = re.sub(r"^\d+\.*\s+", "", title).strip()
    if not title:
        return None
    parts = [f"Occupation: {title}"]
    if code:
        parts.append(f"Code: {code.rstrip('.')}")
    return "\n".join(parts)


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
        description="Score occupations for AI exposure using Claude or Gemini (AI Studio or Vertex AI)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            f"Model to use (default: {CLAUDE_MODEL} for Claude, "
            f"{DEFAULT_MODEL} for Gemini)"
        ),
    )
    parser.add_argument(
        "--backend",
        choices=["anthropic", "aistudio", "vertex", "auto"],
        default=LLM_BACKEND,
        help=(
            "API backend: 'anthropic' uses the Claude API (ANTHROPIC_API_KEY), "
            "'vertex' uses Vertex AI (VERTEX_PROJECT required), "
            "'aistudio' uses Google AI Studio (GOOGLE_API_KEY required), "
            "'auto' picks Claude, then Vertex, then AI Studio by which keys are set "
            "(default: LLM_BACKEND from .env, else auto)"
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel API calls (default: 5)",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=int(os.getenv("TREE_LEVEL", "4")),
        help=(
            "Classification level to score; only titles marked '(Level N)' are "
            "scored (default: TREE_LEVEL from env, else 4)"
        ),
    )
    parser.add_argument(
        "--start", type=int, default=0, help="Start index within the level"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="End index within the level"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Score a fixed-seed random sample of N occupations (for cheap trial runs)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between submitting each job in seconds (default: 0, use to throttle)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-score the selected occupations even if cached (other cached scores are kept)",
    )
    args = parser.parse_args()
    if args.sample is not None and args.sample < 1:
        parser.error("--sample must be at least 1")

    # ── Resolve backend ──────────────────────────────────────────────────────
    backend = args.backend
    if backend == "auto":
        if ANTHROPIC_API_KEY:
            backend = "anthropic"
        elif VERTEX_PROJECT:
            backend = "vertex"
        else:
            backend = "aistudio"
    model = args.model or (CLAUDE_MODEL if backend == "anthropic" else DEFAULT_MODEL)

    if backend == "anthropic":
        claude = anthropic.Anthropic(max_retries=5)
        if not (claude.api_key or claude.auth_token or claude.credentials):
            print("Error: no Claude API credentials found. Add your key to .env:")
            print("  ANTHROPIC_API_KEY=your-key   (from https://platform.claude.com/settings/keys)")
            return 1
        print("Backend: Claude API")
        def score_fn(client, text, model):
            return score_anthropic(claude, text, model)
    elif backend == "vertex":
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

    # Score only the requested level; --start/--end slice within it
    level_occs = [o for o in occupations if title_level(o["title"]) == args.level]
    if not level_occs:
        print(f"Error: no occupations marked '(Level {args.level})' in data/occupations.json")
        return 1
    subset = level_occs[args.start : args.end]
    if args.sample is not None and args.sample < len(subset):
        # Fixed seed so trial runs are repeatable and comparable
        subset = random.Random(42).sample(subset, args.sample)

    # Load existing scores. Always kept: --force only re-scores the selection
    # and merges it back, so a partial run never drops the rest of the cache.
    scores: dict = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                scores[entry["slug"]] = entry

    # Only score occupations not yet cached, unless forced
    todo = [occ for occ in subset if args.force or occ["slug"] not in scores]
    # Duplicate slugs (StatFin lists a few occupations twice) need one call
    todo = list({occ["slug"]: occ for occ in todo}.values())
    selected = {occ["slug"] for occ in subset}
    cached = len(selected & scores.keys())

    print(f"Model:   {model}")
    print(f"Workers: {args.workers} parallel calls")
    print(f"Level:   {args.level} ({len(level_occs)} occupations)")
    print(f"Total:   {len(selected)} selected  |  cached: {cached}  |  to score: {len(todo)}")

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
            future = executor.submit(_score_one, occ, csv_rows, score_fn, model)
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
                    scores[slug] = {"slug": slug, "title": title, **result, "model": model}
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

    print(f"\nDone. {len(scores)} scores in {OUTPUT_FILE} ({len(todo) - len(errors)} new), {len(errors)} errors.")
    if errors:
        print(f"Failed: {errors}")
        if args.force:
            print("They keep their previous score, if any. Rerun with --force to retry "
                  "(this re-scores the whole selection).")
        else:
            print("Rerun the same command to retry them; cached scores are skipped.")
    if errors and len(errors) == len(todo):
        print("Every request failed; check the API key, model name and network.")
        return 1

    # Summary stats for the selected occupations
    vals = [s for s in scores.values() if s["slug"] in selected and "exposure" in s]
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
