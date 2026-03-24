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

See `finlandjobs --help` for all options.

## Notes

- `score.py` will use Markdown pages if present, otherwise it constructs a prompt from `occupations.csv`.
- Outlook: if you use the Occupational Barometer, map its demand labels into the CSV `outlook_desc` field in `fetch_statfin.py`.
- `fetch_statfin.py` writes `median_pay_source` and `outlook_source` fields for auditability (`wages_statfin`, `outlook_statfin`, `extras_csv`).
- You can enforce outlook completeness in config with `min_outlook_coverage` (0-1) and `strict_outlook_coverage` (true/false).
- `build_site_data.py` uses one hierarchy level only (`TREE_LEVEL`, default `4`) so total jobs are not double-counted across Level 1-5 aggregates.
- **Barometer data source**: The Occupational Barometer (Työllisyysbarometri) CSV can be obtained from Statistics Finland (PxWeb API) or the Ministry of Employment and the Economy. Look for columns containing occupation codes (ISCO or ammatti_koodi) and outlook categories (balance_label). This data is optional; the pipeline will use `extras.csv` if barometer data is not provided.

---

This project is adapted from [karpathy/jobs](https://github.com/karpathy/jobs). Thanks to the original author for the excellent foundation.