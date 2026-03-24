# Pipeline Evaluation Findings
_Evaluated: 2026-03-24_

## 🔴 Issue 1: `occupations.csv` Schema is Stale

The current `data/occupations.csv` was **generated before the schema fixes** applied to `fetch_statfin.py`.
It still has old/incorrect columns:

| Column | Status | Expected |
|--------|--------|----------|
| `soc_code` | ❌ present | should be `isco_code` |
| `projected_employment_2034` | ❌ present | should be removed (BLS leftover) |
| `employment_change` | ❌ present | should be removed (BLS leftover) |

**Fix:** Re-run `fetch_statfin.py` to regenerate `occupations.csv` with the corrected schema:
```bash
finlandjobs fetch
# or
uv run python src/fetch_statfin.py --config data/statfin_config.json
```

---

## 🔴 Issue 2: `scores.json` is a Mixed US/Finnish Hybrid

- `scores.json` has **1180 entries** — mix of old US slugs (e.g. `athletic-trainers`, `cashiers`) and Finnish slugs (e.g. `2654-film-stage-...-level-4`)
- `occupations.csv` has **1183 Finnish slugs**
- Only **838 slugs match** → 345 Finnish occupations have no AI exposure score

**Root cause:** `score.py --force` was cancelled partway through. The result is a hybrid file.

**Fix options:**
- Option A (recommended): Run `score.py` without `--force` — it will skip existing (cached) entries and only score the 345 unmatched Finnish slugs. Fast (~345 API calls).
- Option B: Run `score.py --force` to completion — re-scores all 1183 occupations. Slow but clean.

```bash
uv run python src/score.py   # no --force → scores only unmatched
uv run python src/score.py --force   # full re-score (1183 calls)
```

---

## 🔴 Issue 3: `site/data.json` Only Has 459 of 1184 Occupations

`build_site_data.py` outputs only 459 entries to the visualization frontend.
This is likely because only Level 4 occupations pass through the `TREE_LEVEL` filter.

**Check:** Review `src/build_site_data.py` for the filter criteria, and check if `TREE_LEVEL=4` in `.env` is intentional.

```bash
python3 -c "import json; d=json.load(open('site/data.json')); print(len(d), 'entries')"
```

---

## 🟡 Issue 4: Two Parallel Orchestrators (`pipeline.py` vs `main.py`)

- `pipeline.py` — simpler step-runner using shell `uv run` commands
- `main.py` — proper `finlandjobs` CLI entrypoint with barometer, two-pass build logic
- `pipeline.py` line 14 docstring still says **"via OpenRouter"** (stale)
- These overlap but `main.py` is the canonical, more complete version

**Fix:** Update `pipeline.py` line 14. Consider whether to keep `pipeline.py` as a quick reference or remove it in favour of `main.py` exclusively.

```diff
- 4. Score AI exposure with LLM (Gemini Flash via OpenRouter)
+ 4. Score AI exposure with LLM (Gemini Flash via Google AI Studio / Vertex AI)
```

---

## Recommended Fix Order

1. `finlandjobs fetch` — regenerates `occupations.csv` with correct column names
2. `uv run python src/score.py` — fills in the 345 missing Finnish scores (cached run)
3. Review `src/build_site_data.py` filtering — understand 459/1184 output
4. Fix `pipeline.py` line 14 docstring (cosmetic)
