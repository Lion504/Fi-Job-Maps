# Finland Job Market Visualizer

Explore Finnish occupation data (StatFin PxWeb + Occupational Barometer) and color it by AI exposure. The original US/BLS scrapers remain, but the default pipeline now targets Finland.

## LLM-powered coloring

The repo still lets you score occupations with an LLM (OpenRouter). You can change the rubric in `score.py` to rate anything (AI exposure, offshoring risk, climate impact) and recolor the treemap. Scores are cached in `scores.json`.

**What "AI Exposure" is NOT:**

- It does **not** predict that a job will disappear. Software developers score 9/10 because AI is transforming their work — but demand for software could easily _grow_ as each developer becomes more productive.
- It does **not** account for demand elasticity, latent demand, regulatory barriers, or social preferences for human workers.
- The scores are rough LLM estimates (Gemini Flash via OpenRouter), not rigorous predictions. Many high-exposure jobs will be reshaped, not replaced.

## Data pipeline (Finland)

1. **Fetch StatFin** (`fetch_statfin.py`) — Queries Statistics Finland PxWeb tables (config-driven) to produce `occupations.json` and `occupations.csv` with pay (EUR), employment counts, and optional outlook labels.
2. **Import Barometer outlook (optional)** (`fetch_barometer.py`) — Normalizes Labour Force Barometer CSV into extras-compatible outlook columns (`code`, `outlook_pct`, `outlook_desc`).
3. **Score (optional)** (`score.py`) — Sends each occupation (from CSV or Markdown if present) to an LLM to produce an AI exposure score (0–10) with rationale. Results are cached in `scores.json`.
4. **Build site data** (`build_site_data.py`) — Merges `occupations.csv` and `scores.json` into `site/data.json` for the treemap.
5. **Frontend** (`site/index.html`) — Treemap where area = employment and color = chosen metric (outlook/pay/education/exposure). Copy tweaks may be needed for Finnish labels.

## Key files

| File                          | Description                                                        |
| ----------------------------- | ------------------------------------------------------------------ |
| `statfin_config.example.json` | Template for PxWeb tables/variables (employment, wages, outlook)   |
| `fetch_statfin.py`            | PxWeb fetcher that writes `occupations.json` and `occupations.csv` |
| `fetch_barometer.py`          | Converts Barometer CSV to extras-compatible outlook CSV            |
| `occupations.csv`             | Summary stats: pay (EUR/year), employment count, outlook label     |
| `scores.json`                 | AI exposure scores (0–10) with rationales                          |
| `site/data.json`              | Frontend-ready merged data                                         |
| `site/`                       | Static website (treemap visualization)                             |

## Setup

```
uv sync
```

Requires an OpenRouter API key in `.env` if you plan to run `score.py`:

```
OPENROUTER_API_KEY=your_key_here
```

## Usage (Finland)

1. Copy and edit the StatFin config

```
cp statfin_config.example.json statfin_config.json
# edit statfin_config.json with real PxWeb tables and variable codes
```

2. Fetch data and build the site bundle

```
uv run python fetch_statfin.py --config statfin_config.json
uv run python fetch_barometer.py --input barometer.csv --output barometer_outlook.csv --code-column isco_code --outlook-desc-column balance_label
uv run python score.py        # optional, adds AI exposure layer
uv run python build_site_data.py
cd site && python -m http.server 8000

# Optional: choose hierarchy level for treemap (default: Level 4)
TREE_LEVEL=4 uv run python build_site_data.py
```

## Notes

- The original US/BLS scraping scripts remain in the repo but are no longer the default path.
- `score.py` will use Markdown pages if present, otherwise it constructs a prompt from `occupations.csv` (Finnish stats).
- Outlook: if you use the Occupational Barometer, map its demand labels into the CSV `outlook_desc` field in `fetch_statfin.py`.
- `fetch_statfin.py` now writes `median_pay_source` and `outlook_source` fields for auditability (`wages_statfin`, `outlook_statfin`, `extras_csv`).
- You can enforce outlook completeness in config with `min_outlook_coverage` (0-1) and `strict_outlook_coverage` (true/false).
- `build_site_data.py` uses one hierarchy level only (`TREE_LEVEL`, default `4`) so total jobs are not double-counted across Level 1-5 aggregates.
