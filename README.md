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
- `TREE_LEVEL` – finest classification level (default: 4, unit groups). `build_site_data.py` emits levels 1 to `TREE_LEVEL` and the map opens on `TREE_LEVEL`; `score.py` scores only this level by default
- `.env` – copy from `.env.example`; holds the AI-exposure scoring keys (see below)

See `finlandjobs --help` for all options.

## AI exposure scoring

`finlandjobs infer` scores each occupation with an LLM when a key is set in `.env`, and falls back to a rule-based estimate otherwise.

- **Claude API (default):** set `ANTHROPIC_API_KEY` (from <https://platform.claude.com/settings/keys>). The model is `CLAUDE_MODEL`, default `claude-haiku-5-5`, the cheapest and fastest Claude model.
- **Gemini:** set `GOOGLE_API_KEY` (AI Studio) or `VERTEX_PROJECT` + `VERTEX_API_KEY` (Vertex AI); the model is `LLM_MODEL`.
- `LLM_BACKEND` picks the backend: `auto` (Claude, then Vertex, then AI Studio, by which keys are set), `anthropic`, `vertex` or `aistudio`.

Only the finest level is scored (`--level`, default `TREE_LEVEL`, i.e. the 459 Level 4 unit groups): about 460 calls, roughly $0.10–0.20 with `claude-haiku-5-5`. Group levels get employment-weighted averages at build time instead of their own LLM scores. The model sees just the occupation title and its Classification of Occupations 2010 / ISCO-08 code, not pay, employment, outlook or education. Each score records the `model` that produced it.

Scores are cached in `data/scores.json` by occupation slug (finest level only), so a run only scores occupations that aren't cached yet; when nothing is left to score, `score.py` exits without needing a key. To re-score the level, for example after switching model, and put the new scores on the site:

```bash
uv run python src/score.py --force
finlandjobs build        # or: uv run python src/build_site_data.py
cp site/data.json docs/data.json   # docs/ is the published GitHub Pages copy
```

`--force` re-scores only the selected occupations and merges them into the cache; other entries are kept, so a partial run (`--start/--end`, `--sample`) is safe. The build joins `scores.json` to each occupation by its exact slug and uses no other source of exposure, so new scores always reach the map (an occupation without a score shows none).

To try a model or prompt change cheaply, score a fixed random sample into a separate file and compare it with the current scores before re-scoring everything:

```bash
SCORES_OUTPUT_FILE=data/scores_trial.json uv run python src/score.py --force --sample 40
uv run python src/compare_scores.py data/scores_trial.json data/scores.json --level 4
```

`compare_scores.py` reports, on the occupations both files share, the mean signed and absolute difference, the share of exact and within-one-point matches, and the 15 largest differences.

## Levels on the map

The **Level** switch shows one level of the Classification of Occupations 2010 at a time: major groups (Level 1), sub-major groups (2), minor groups (3) or unit groups (4, the default). Each level covers the whole workforce, so levels are never summed together. Every row in `data.json` has `level` and `code`; group rows also have `members` (the number of unit groups with employment they contain). Group values are built as follows:

- **Employment** and, where Statistics Finland publishes it, **median pay** are the group's own figures. Without a published median, a group whose unit groups' pay is all estimated from the same group takes that estimate (`pay_source: "estimated"`, see below); otherwise its pay is the employment-weighted mean of its unit groups, estimates included (`pay_source: "derived"`).
- **AI exposure** and **outlook** are employment-weighted means of the unit groups' values, rounded to one decimal (`outlook_source: "derived"`). The exposure rationale names the highest- and lowest-scoring unit groups with employment.
- **Outlook label** (`outlook_desc`): the label with the largest share of the group's employment.
- **Education**, **work experience** and **training** are the values held by the largest share of the group's employment.

### Estimated pay

Statistics Finland publishes no median pay for some unit groups (currently 97 of 459). For these, `build_site_data.py` uses the own median of the nearest group that contains them and has one: the Level 3 group, else Level 2, else Level 1 (same code-prefix rule as the group averages). Such rows get `pay_source: "estimated"` and `pay_basis`, the title of that group. A group without its own median whose unit groups all share one estimate gets the same `pay_source` and `pay_basis` (currently 8 Level 3 groups, e.g. 324 Veterinary technicians and assistants, estimated from 32 Health associate professionals). The estimate is made at build time only; `data/occupations.csv` keeps Statistics Finland's figures as published.

On the map the tooltip labels the figure **Median pay (est.)** and names the group it comes from. The Pay layer colours and the statistics panel use the estimates like any other pay, and `prompt.md` marks them "(est.)".

## Weekly refresh

`.github/workflows/refresh-data.yml` refreshes the published data every Monday at 03:17 UTC. To run it by hand, open the **Actions** tab, pick **Weekly data refresh** and click **Run workflow**. It:

1. fetches the latest Statistics Finland tables (`fetch_statfin.py`),
2. scores occupations that have no score yet with `claude-haiku-5-5` (`score.py`),
3. rebuilds `site/data.json`, estimating missing pay as above, and copies it to `docs/data.json`,
4. checks the result with `src/check_site_data.py` (see below),
5. regenerates `prompt.md` (`make_prompt.py`),
6. if anything under `data/`, `site/` or `docs/`, or `prompt.md`, changed, commits it as `github-actions[bot]` ("data: weekly refresh (YYYY-MM-DD)") and pushes it to `master`. If `master` moved during the run, the push is rejected and the run fails without publishing (a rebased commit would carry data computed from older inputs); the next week's run starts again from fresh data,
7. requests a GitHub Pages build when the latest build isn't of the current commit. Pushes made with the workflow's token don't start a Pages build by themselves, so the workflow asks for one through the API (up to 3 tries). Because it compares against the latest build, a run whose request failed is caught up by the next run, even when no data changed.

Any failed step stops the run before anything is committed. Statistics Finland requests that time out, fail to connect or return a server error are retried twice (after 10 s and 30 s) before the run fails.

`check_site_data.py` fails, listing every problem, unless:

- `site/data.json` and `docs/data.json` are identical;
- the rows cover exactly Levels 1 to `TREE_LEVEL`, every level sums to the same employment, and no title still contains "(Level";
- there are at least 400 unit groups (`--min-rows`);
- every unit group has an integer AI exposure from 0 to 10 and a rationale;
- every unit group has pay, with `pay_source` `wages_statfin`, `extras_csv` (pay from `data/extras.csv`) or `estimated`, and at most 150 are estimated (`--max-estimated`);
- every estimated row, unit group or group, names its source group in `pay_basis`;
- every group's AI exposure is the employment-weighted mean of the unit groups under its code (within 0.05).

Scoring needs a repository secret named `ANTHROPIC_API_KEY` (**Settings → Secrets and variables → Actions**), but only in a week when new occupations appear; otherwise `score.py` exits before looking for a key. A week with nothing new costs nothing; each newly scored occupation costs roughly $0.0002 with `claude-haiku-5-5`. If new occupations appear and the secret is missing, the run fails and publishes nothing.

`og.png`, the link-preview image, is not regenerated: it needs headless Chrome, and the default Outlook view it shows rarely changes.

GitHub disables scheduled workflows in public repositories after 60 days without repository activity and emails the owner. To turn the refresh back on, open the **Actions** tab, pick **Weekly data refresh** and click **Enable workflow**, or run `gh workflow enable refresh-data.yml`.

Run the same check locally after a manual rebuild:

```bash
uv run python src/build_site_data.py && cp site/data.json docs/data.json
uv run python src/check_site_data.py
uv run python src/make_prompt.py   # prompt.md, from site/data.json
```

## Notes

- `score.py` will use Markdown pages (`pages/{slug}.md`) if present, otherwise it sends the occupation title and code.
- Outlook: if you use the Occupational Barometer, map its demand labels into the CSV `outlook_desc` field in `fetch_statfin.py`.
- `fetch_statfin.py` writes `median_pay_source` and `outlook_source` fields for auditability (`wages_statfin`, `outlook_statfin`, `extras_csv`).
- You can enforce outlook completeness in config with `min_outlook_coverage` (0-1) and `strict_outlook_coverage` (true/false).
- `build_site_data.py` writes levels 1 to `TREE_LEVEL` (default `4`) as separate rows tagged with `level`; the map shows one level at a time so total jobs are not double-counted across Level 1-5 aggregates.
- **Barometer data source**: The Occupational Barometer (Työllisyysbarometri) CSV can be obtained from Statistics Finland (PxWeb API) or the Ministry of Employment and the Economy. Look for columns containing occupation codes (ISCO or ammatti_koodi) and outlook categories (balance_label). This data is optional; the pipeline will use `extras.csv` if barometer data is not provided.
- **Analytics**: the published page loads a self-hosted, cookieless [Umami](https://umami.is) tracker. `data-domains="lion504.github.io"` means local previews are never counted. `site/index.html` and `docs/index.html` (the GitHub Pages copy) carry the same tag; keep them identical.

---

Built by [Wang Yongzhi](https://lion504.github.io/). Notes on the data and design: [A useful map starts with trustworthy totals](https://lion504.github.io/fijobmaps-data.html).

This project is adapted from [karpathy/jobs](https://github.com/karpathy/jobs). Thanks to the original author for the excellent foundation.

## License

The code in this repository is released under the [MIT License](LICENSE). Parts adapted from [karpathy/jobs](https://github.com/karpathy/jobs), which has no license, remain under their original author's copyright. The occupation data is from Statistics Finland, used under its [open data licence (CC BY 4.0)](https://stat.fi/en/services/statistical-data-services/open-data-and-interfaces). Source: Statistics Finland.