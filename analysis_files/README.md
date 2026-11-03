# Analysis: Movies vs Crimes and Movies vs Elections

Run everything from the **repo root** (same convention as `data_organizer_files/`):

```bash
pip install -r requirements.txt
python analysis_files/movies_vs_crimes.py
python analysis_files/movies_vs_elections.py
```

| Folder | Contents |
|---|---|
| `analysis_files/charts/` | `*.html` interactive Plotly charts, `*.png` static matplotlib charts for the report |
| `analysis_files/results/` | correlation tables (CSV), merged data, `*_summary.txt` |

## Method
- **Genre share, not counts.** Movie counts grow ~5x (2001-2012) and ~10x (1950-2021), so each genre is converted to a % of that year's movies (Action, Comedy, Crime, Non-fiction, Drama, Horror, Romance). War-themed counts come from a separate dataset and are reported separately.
- **Crimes (2001-2012, n=12):** Pearson/Spearman on levels, then on year-over-year % change to remove the shared upward trend.
- **Elections (n=17):** winning party's vote % is the dissatisfaction proxy (lower = weaker mandate). Tests: correlation in the election year, 3-year-average robustness check, partial correlation with Year held fixed, weak-vs-strong mandate (Mann-Whitney U), decade summary.
- 1985 and 1992 rows in `elections.csv` were excluded (vote totals are 1-4% of a normal election, so they look like by-election records, not general elections). Movie year 2022 is excluded from share analysis (partial year).

## Findings (exploratory; see `results/*_summary.txt`)
- **Crimes:** raw correlations look strong (Comedy r=+0.89, Drama +0.78, Crime -0.81, Action -0.76, Romance -0.79), but crimes correlate 0.96 with Year, so this is mostly a shared trend. On year-over-year changes **no genre is significant** at p<0.05.
- **Elections:** with Year held fixed, Drama share is higher (partial r=+0.51) and Horror (-0.51) and Romance (-0.53) are lower when the winning party has a stronger mandate. Comedy's raw link (r=-0.64) disappears once the time trend is removed.
- Small n and changing cinema over time mean these are patterns, not proof of causation.
