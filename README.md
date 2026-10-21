# Finland Job Market Visualizer

Explore Finnish occupation data (StatFin PxWeb + Occupational Barometer) and color it by AI exposure.

## Quick Start

1. **Configure**
   ```bash
   cp data/statfin_config.example.json data/statfin_config.json
   # Edit data/statfin_config.json with your PxWeb table IDs and variable codes
   ```

2. **Build site**
   ```bash
   finlandjobs all --barometer-input barometer.csv  # complete pipeline
   # or
   finlandjobs fetch && finlandjobs build
   ```

3. **Preview**
   ```bash
   cd site && python -m http.server 8000
   ```

## CLI Commands

- `finlandjobs fetch` – download StatFin data
- `finlandjobs infer` – add AI exposure estimates (optional)
- `finlandjobs build` – generate site data files
- `finlandjobs all` – run complete pipeline

Optional: `finlandjobs all --barometer-input barometer.csv` includes Occupational Barometer outlook data.

## Configuration

- `statfin_config.json` – required, defines PxWeb tables and variables
- `TREE_LEVEL` – treemap hierarchy level (default: 4)
- `.env` – copy from `.env.example`; holds the AI-exposure scoring keys (see below)

See `finlandjobs --help` for all options.

## AI exposure scoring

`finlandjobs infer` scores each occupation with an LLM when a key is set in `.env`, and falls back to a rule-based estimate otherwise.

- **Claude API (default):** set `ANTHROPIC_API_KEY` (from <https://platform.claude.com/settings/keys>). The model is `CLAUDE_MODEL`, default `claude-haiku-5-5`, the cheapest and fastest Claude model; scoring all occupations costs roughly $0.10–0.20.
- **Gemini:** set `GOOGLE_API_KEY` (AI Studio) or `VERTEX_PROJECT` + `VERTEX_API_KEY` (Vertex AI); the model is `LLM_MODEL`.
- `LLM_BACKEND` picks the backend: `auto` (Claude, then Vertex, then AI Studio, by which keys are set), `anthropic`, `vertex` or `aistudio`.

Scores are cached in `data/scores.json`, so a run only scores occupations that aren't cached yet. To re-score everything, for example after switching model:

```bash
uv run python src/score.py --force
```

## Notes

- `score.py` will use Markdown pages if present, otherwise it constructs a prompt from `occupations.csv`.
- Outlook: if you use the Occupational Barometer, map its demand labels into the CSV `outlook_desc` field in `fetch_statfin.py`.
- `fetch_statfin.py` writes `median_pay_source` and `outlook_source` fields for auditability (`wages_statfin`, `outlook_statfin`, `extras_csv`).
- You can enforce outlook completeness in config with `min_outlook_coverage` (0-1) and `strict_outlook_coverage` (true/false).
- `build_site_data.py` uses one hierarchy level only (`TREE_LEVEL`, default `4`) so total jobs are not double-counted across Level 1-5 aggregates.
- **Barometer data source**: The Occupational Barometer (Työllisyysbarometri) CSV can be obtained from Statistics Finland (PxWeb API) or the Ministry of Employment and the Economy. Look for columns containing occupation codes (ISCO or ammatti_koodi) and outlook categories (balance_label). This data is optional; the pipeline will use `extras.csv` if barometer data is not provided.
- **Analytics**: the published page loads a self-hosted, cookieless [Umami](https://umami.is) tracker. `data-domains="lion504.github.io"` means local previews are never counted. `site/index.html` and `docs/index.html` (the GitHub Pages copy) carry the same tag; keep them identical.

---

Built by [Wang Yongzhi](https://lion504.github.io/). Notes on the data and design: [A useful map starts with trustworthy totals](https://lion504.github.io/fijobmaps-data.html).

This project is adapted from [karpathy/jobs](https://github.com/karpathy/jobs). Thanks to the original author for the excellent foundation.

## License

The code in this repository is released under the [MIT License](LICENSE). Parts adapted from [karpathy/jobs](https://github.com/karpathy/jobs), which has no license, remain under their original author's copyright. The occupation data is from Statistics Finland, used under its [open data licence (CC BY 4.0)](https://stat.fi/en/services/statistical-data-services/open-data-and-interfaces). Source: Statistics Finland.