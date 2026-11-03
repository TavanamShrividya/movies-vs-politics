"""
Movies vs Crimes (2001-2012)
Run from the repo root:  python analysis_files/movies_vs_crimes.py

Inputs : organized_data/movies.csv, organized_data/crimes.csv
Outputs: analysis_files/charts/crimes_*.html (interactive, Plotly)
         analysis_files/charts/crimes_*.png  (static, matplotlib - for the report)
         analysis_files/results/crimes_*.csv / crimes_summary.txt
"""
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

CHART_DIR, RES_DIR = "analysis_files/charts", "analysis_files/results"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

GENRES = ["Action", "Comedy", "Crime", "Non-fiction", "Drama", "Horror", "Romance"]
COLORS = {"Action": "#e4572e", "Comedy": "#f3a712", "Crime": "#4c4c6d", "Non-fiction": "#29a3a3",
          "Drama": "#2e86de", "Horror": "#8e44ad", "Romance": "#e84393", "War": "#6b705c"}

# ---------------------------------------------------------------- load + merge
movies = pd.read_csv("organized_data/movies.csv")
crimes = pd.read_csv("organized_data/crimes.csv")
df = movies.merge(crimes, on="Year", how="inner").sort_values("Year").reset_index(drop=True)

# Movie counts grow ~5x between 2001 and 2012, so raw counts mostly measure "more movies in the dataset".
# We therefore use each genre's SHARE (% of that year's movies) for the main analysis.
df["Total"] = df[GENRES].sum(axis=1)
for g in GENRES:
    df[g + " %"] = df[g] / df["Total"] * 100
df["War per 100"] = df["War"] / df["Total"] * 100      # war-themed count comes from a different source -> keep separate
df["Crimes (lakh)"] = df["Crimes"] / 1e5

share_cols = [g + " %" for g in GENRES] + ["War per 100"]

# ---------------------------------------------------------------- statistics
def corr_table(x_series, frame, cols):
    rows = []
    for c in cols:
        r, p = stats.pearsonr(x_series, frame[c])
        rho, ps = stats.spearmanr(x_series, frame[c])
        rows.append({"Genre": c.replace(" %", "").replace(" per 100", " (war-themed)"),
                     "Pearson r": r, "Pearson p": p, "Spearman rho": rho, "Spearman p": ps})
    return pd.DataFrame(rows)

# (a) levels: crimes vs genre share
levels = corr_table(df["Crimes"], df, share_cols)

# (b) year-over-year change: removes the shared upward trend (both series trend, which causes spurious correlation)
diff = df[["Year", "Crimes"] + share_cols].copy()
diff[["Crimes"] + share_cols] = diff[["Crimes"] + share_cols].pct_change() * 100
diff = diff.dropna().reset_index(drop=True)
changes = corr_table(diff["Crimes"], diff, share_cols)

# (c) trend check: how strongly does each series simply correlate with time?
trend = pd.DataFrame({"Series": ["Crimes"] + share_cols,
                      "r with Year": [stats.pearsonr(df["Year"], df[c])[0] for c in ["Crimes"] + share_cols]})

levels.round(4).to_csv(f"{RES_DIR}/crimes_correlation_levels.csv", index=False)
changes.round(4).to_csv(f"{RES_DIR}/crimes_correlation_yoy_changes.csv", index=False)
df.round(3).to_csv(f"{RES_DIR}/crimes_merged_data.csv", index=False)

# ---------------------------------------------------------------- interactive charts (Plotly)
# 1. crimes (bars) + genre share (lines)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df["Year"], y=df["Crimes (lakh)"], name="IPC crimes (lakh)",
                     marker_color="rgba(120,120,120,0.30)"), secondary_y=False)
for g in GENRES:
    fig.add_trace(go.Scatter(x=df["Year"], y=df[g + " %"], mode="lines+markers", name=g,
                             line=dict(color=COLORS[g], width=2.5)), secondary_y=True)
fig.update_layout(title="IPC crimes vs genre share of Indian movies (2001-2012)", template="plotly_white",
                  hovermode="x unified", legend=dict(orientation="h", y=-0.2))
fig.update_yaxes(title_text="Total IPC crimes (lakh)", secondary_y=False)
fig.update_yaxes(title_text="Genre share of movies (%)", secondary_y=True)
fig.update_xaxes(dtick=1)
fig.write_html(f"{CHART_DIR}/crimes_vs_genre_share.html")

# 2. correlation bars: levels vs year-over-year change
fig = go.Figure()
fig.add_trace(go.Bar(x=levels["Genre"], y=levels["Pearson r"], name="Levels (trend included)", marker_color="#2e86de"))
fig.add_trace(go.Bar(x=changes["Genre"], y=changes["Pearson r"], name="Year-over-year change (trend removed)", marker_color="#e4572e"))
fig.add_hline(y=0, line_color="black")
fig.update_layout(barmode="group", template="plotly_white", yaxis_title="Pearson r with total crimes",
                  title="Correlation of crimes with genre share: raw vs trend-removed")
fig.write_html(f"{CHART_DIR}/crimes_correlation_bars.html")

# 3. scatter grid with regression lines
pick = ["Crime", "Action", "Drama", "Romance"]
fig = make_subplots(rows=2, cols=2, subplot_titles=[f"Crimes vs {g} share" for g in pick])
for i, g in enumerate(pick):
    r_, c_ = i // 2 + 1, i % 2 + 1
    x, y = df["Crimes (lakh)"], df[g + " %"]
    m, b = np.polyfit(x, y, 1)
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers+text", text=df["Year"].astype(str), textposition="top center",
                             marker=dict(color=COLORS[g], size=9), showlegend=False), row=r_, col=c_)
    fig.add_trace(go.Scatter(x=[x.min(), x.max()], y=[m * x.min() + b, m * x.max() + b], mode="lines",
                             line=dict(color="black", dash="dash"), showlegend=False), row=r_, col=c_)
    fig.update_xaxes(title_text="IPC crimes (lakh)", row=r_, col=c_)
    fig.update_yaxes(title_text=f"{g} share (%)", row=r_, col=c_)
fig.update_layout(template="plotly_white", height=750, title="Scatter plots with trend line")
fig.write_html(f"{CHART_DIR}/crimes_scatter_grid.html")

# 4. composition of the movie mix
fig = go.Figure()
for g in GENRES:
    fig.add_trace(go.Bar(x=df["Year"], y=df[g + " %"], name=g, marker_color=COLORS[g]))
fig.update_layout(barmode="stack", template="plotly_white", title="Genre mix of Indian movies, 2001-2012 (% of year)",
                  yaxis_title="% of movies", xaxis=dict(dtick=1))
fig.write_html(f"{CHART_DIR}/crimes_genre_mix.html")

# ---------------------------------------------------------------- static charts (matplotlib, for the report)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(df["Year"], df["Crimes (lakh)"], color="lightgrey", label="IPC crimes (lakh)")
ax.set_ylabel("Total IPC crimes (lakh)"); ax.set_xlabel("Year"); ax.set_xticks(df["Year"])
ax2 = ax.twinx()
for g in GENRES:
    ax2.plot(df["Year"], df[g + " %"], marker="o", color=COLORS[g], label=g)
ax2.set_ylabel("Genre share of movies (%)")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
ax.set_title("IPC crimes vs genre share of Indian movies (2001-2012)")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/crimes_vs_genre_share.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5))
w = 0.38; xs = np.arange(len(levels))
ax.bar(xs - w / 2, levels["Pearson r"], w, label="Levels", color="#2e86de")
ax.bar(xs + w / 2, changes["Pearson r"], w, label="Year-over-year change", color="#e4572e")
ax.axhline(0, color="black", lw=0.8); ax.set_xticks(xs); ax.set_xticklabels(levels["Genre"], rotation=30, ha="right")
ax.set_ylabel("Pearson r with total crimes"); ax.legend(); ax.set_title("Crimes vs genre share: raw vs trend-removed")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/crimes_correlation_bars.png", dpi=150); plt.close(fig)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, g in zip(axes.ravel(), pick):
    x, y = df["Crimes (lakh)"], df[g + " %"]
    m, b = np.polyfit(x, y, 1)
    ax.scatter(x, y, color=COLORS[g])
    for xi, yi, yr in zip(x, y, df["Year"]): ax.annotate(str(yr)[2:], (xi, yi), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.plot([x.min(), x.max()], [m * x.min() + b, m * x.max() + b], "k--")
    r, p = stats.pearsonr(x, y)
    ax.set_title(f"{g}: r = {r:.2f}, p = {p:.3f}"); ax.set_xlabel("IPC crimes (lakh)"); ax.set_ylabel(f"{g} share (%)")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/crimes_scatter_grid.png", dpi=150); plt.close(fig)

# ---------------------------------------------------------------- text summary
def fmt(t):
    return t.round(3).to_string(index=False)

lines = ["MOVIES vs CRIMES (2001-2012, n = 12 years)", "=" * 60,
         "\nA) Crimes vs genre share - LEVELS (n=12)", fmt(levels),
         "\nB) Crimes vs genre share - YEAR-OVER-YEAR % CHANGE (n=11)", fmt(changes),
         "\nC) Correlation of each series with time (trend check)", fmt(trend),
         "\nSignificant at p<0.05 (levels):   " + ", ".join(levels.loc[levels["Pearson p"] < 0.05, "Genre"]),
         "Significant at p<0.05 (changes):  " + (", ".join(changes.loc[changes["Pearson p"] < 0.05, "Genre"]) or "none"),
         "\nCaveat: n is tiny and both series trend over time; treat as exploratory, not causal."]
open(f"{RES_DIR}/crimes_summary.txt", "w").write("\n".join(lines))
print("\n".join(lines))
