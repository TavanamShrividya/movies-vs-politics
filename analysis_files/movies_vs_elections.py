"""
Movies vs Elections (1951-2019)
Run from the repo root:  python analysis_files/movies_vs_elections.py

Inputs : organized_data/movies.csv, organized_data/elections.csv
Outputs: analysis_files/charts/elections_*.html (Plotly) and *.png (matplotlib)
         analysis_files/results/elections_*.csv / elections_summary.txt

Political dissatisfaction proxy = vote share of the winning party (lower share = weaker mandate).
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
          "Drama": "#2e86de", "Horror": "#8e44ad", "Romance": "#e84393"}
PARTY_COLORS = {"INC": "#2e86de", "INC(I)": "#2e86de", "BLD": "#27ae60", "BJP": "#f39c12"}

# ---------------------------------------------------------------- load
movies = pd.read_csv("organized_data/movies.csv")
elections = pd.read_csv("organized_data/elections.csv").rename(columns={"YEAR": "Year"})

# 1985 (IND, 4.8M votes) and 1992 (INC, 1.5M votes) are not Lok Sabha general elections
# (general elections: 1984, 1989, 1991...). Their vote totals are ~1-4% of a normal election, so they are
# by-election / partial records. They are excluded so they don't distort the analysis.
suspect = elections[elections["Year"].isin([1985, 1992])]
elections = elections[~elections["Year"].isin([1985, 1992])].copy()
elections["Winner"] = elections["PARTY"].replace({"INC(I)": "INC"})   # INC(I) = Congress (I), same party family
elections["Mandate"] = np.where(elections["PERCENTAGE"] >= elections["PERCENTAGE"].median(), "Strong (>= median)", "Weak (< median)")

# genre SHARE (% of year's movies) because raw counts grow ~10x over 70 years
movies["Total"] = movies[GENRES].sum(axis=1)
for g in GENRES:
    movies[g + " %"] = movies[g] / movies["Total"] * 100
movies = movies[movies["Year"] <= 2021]          # 2022 is a partial year in the movie dataset
share_cols = [g + " %" for g in GENRES]

# robustness: 3-year average (year-1, year, year+1) around each election
roll = movies.set_index("Year")[share_cols].rolling(3, center=True, min_periods=2).mean().reset_index()

df = elections.merge(movies[["Year"] + share_cols], on="Year", how="inner")
df3 = elections.merge(roll, on="Year", how="inner")
df["Decade"] = (df["Year"] // 10 * 10).astype(str) + "s"

# ---------------------------------------------------------------- statistics
def corr(frame):
    rows = []
    for c in share_cols:
        r, p = stats.pearsonr(frame["PERCENTAGE"], frame[c])
        rho, ps = stats.spearmanr(frame["PERCENTAGE"], frame[c])
        rows.append({"Genre": c.replace(" %", ""), "Pearson r": r, "Pearson p": p, "Spearman rho": rho, "Spearman p": ps})
    return pd.DataFrame(rows)

corr_year = corr(df)
corr_3yr = corr(df3)
mandate = df.groupby("Mandate")[share_cols].mean().T.round(2)
party = df.groupby("Winner")[share_cols].mean().T.round(2)
party["n elections"] = None
decade = df.groupby("Decade").agg(avg_win_pct=("PERCENTAGE", "mean"), elections=("Year", "count"),
                                  **{c: (c, "mean") for c in share_cols}).round(2)

# Weak vs Strong mandate: Mann-Whitney U test per genre (small groups -> non-parametric)
weak = df[df["Mandate"].str.startswith("Weak")]; strong = df[df["Mandate"].str.startswith("Strong")]
mw = pd.DataFrame([{"Genre": c.replace(" %", ""), "Mean (weak)": weak[c].mean(), "Mean (strong)": strong[c].mean(),
                    "U p-value": stats.mannwhitneyu(weak[c], strong[c]).pvalue} for c in share_cols])

# Trend control: partial correlation = correlation of residuals after removing the linear effect of Year.
# Both vote share and genre mix drift over 70 years, so this checks whether the link survives once time is held fixed.
def partial_corr(frame):
    def resid(v):
        m, b = np.polyfit(frame["Year"], v, 1)
        return v - (m * frame["Year"] + b)
    rv = resid(frame["PERCENTAGE"])
    rows = []
    for c in share_cols:
        r, p = stats.pearsonr(rv, resid(frame[c]))
        rows.append({"Genre": c.replace(" %", ""), "Partial r (Year held fixed)": r, "p": p})
    return pd.DataFrame(rows)
partial = partial_corr(df)
partial.round(4).to_csv(f"{RES_DIR}/elections_partial_correlation.csv", index=False)

corr_year.round(4).to_csv(f"{RES_DIR}/elections_correlation_election_year.csv", index=False)
corr_3yr.round(4).to_csv(f"{RES_DIR}/elections_correlation_3yr_avg.csv", index=False)
decade.to_csv(f"{RES_DIR}/elections_decade_summary.csv")
mw.round(4).to_csv(f"{RES_DIR}/elections_weak_vs_strong_mandate.csv", index=False)
df.round(3).to_csv(f"{RES_DIR}/elections_merged_data.csv", index=False)

# ---------------------------------------------------------------- Plotly charts
# 1. winning party's vote share per election
fig = go.Figure(go.Bar(x=df["Year"].astype(str), y=df["PERCENTAGE"], marker_color=[PARTY_COLORS.get(p, "grey") for p in df["PARTY"]],
                       text=df["PARTY"], textposition="outside", hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
fig.add_hline(y=df["PERCENTAGE"].median(), line_dash="dash", annotation_text="median")
fig.update_layout(template="plotly_white", title="Vote share of winning party in each Lok Sabha election",
                  yaxis_title="% of total votes", xaxis_title="Election year")
fig.write_html(f"{CHART_DIR}/elections_winning_share.html")

# 2. genre mix over time + winning vote share
fig = make_subplots(specs=[[{"secondary_y": True}]])
for g in GENRES:
    fig.add_trace(go.Scatter(x=movies["Year"], y=movies[g + " %"], stackgroup="one", name=g,
                             line=dict(width=0.5, color=COLORS[g])), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Year"], y=df["PERCENTAGE"], mode="lines+markers", name="Winning party vote %",
                         line=dict(color="black", width=3), marker=dict(size=8)), secondary_y=True)
fig.update_layout(template="plotly_white", hovermode="x unified", legend=dict(orientation="h", y=-0.2),
                  title="Genre mix of Indian movies vs winning party's vote share (1951-2019)")
fig.update_yaxes(title_text="Genre share (%)", range=[0, 100], secondary_y=False)
fig.update_yaxes(title_text="Winning party vote (%)", range=[0, 60], secondary_y=True)
fig.write_html(f"{CHART_DIR}/elections_genre_mix_vs_vote_share.html")

# 3. correlation bars (election year vs 3-year average)
fig = go.Figure()
fig.add_trace(go.Bar(x=corr_year["Genre"], y=corr_year["Spearman rho"], name="Election year", marker_color="#2e86de"))
fig.add_trace(go.Bar(x=corr_3yr["Genre"], y=corr_3yr["Spearman rho"], name="3-year average", marker_color="#e4572e"))
fig.add_hline(y=0, line_color="black")
fig.update_layout(barmode="group", template="plotly_white", yaxis_title="Spearman rho with winning party vote %",
                  title="Does a stronger mandate go with more/less of a genre? (n = 17 elections)")
fig.write_html(f"{CHART_DIR}/elections_correlation_bars.html")

# 4. weak vs strong mandate
fig = go.Figure()
fig.add_trace(go.Bar(x=mw["Genre"], y=mw["Mean (weak)"], name="Weak mandate (< median vote share)", marker_color="#e4572e"))
fig.add_trace(go.Bar(x=mw["Genre"], y=mw["Mean (strong)"], name="Strong mandate (>= median)", marker_color="#2e86de"))
fig.update_layout(barmode="group", template="plotly_white", yaxis_title="Average genre share (%)",
                  title="Genre share in election years: weak vs strong mandates")
fig.write_html(f"{CHART_DIR}/elections_weak_vs_strong.html")

# 5. decade-by-decade mix
dec = df.groupby("Decade")[share_cols].mean()
fig = go.Figure()
for g in GENRES:
    fig.add_trace(go.Bar(x=dec.index, y=dec[g + " %"], name=g, marker_color=COLORS[g]))
fig.add_trace(go.Scatter(x=decade.index, y=decade["avg_win_pct"], name="Avg winning vote %", mode="lines+markers",
                         yaxis="y2", line=dict(color="black", width=3)))
fig.update_layout(barmode="stack", template="plotly_white", title="Decade-by-decade genre mix (election years) and average winning vote %",
                  yaxis=dict(title="Genre share (%)"), yaxis2=dict(title="Avg winning vote %", overlaying="y", side="right", range=[0, 60]))
fig.write_html(f"{CHART_DIR}/elections_decade_mix.html")

# 6. scatter grid
pick = ["Action", "Drama", "Romance", "Crime"]
fig = make_subplots(rows=2, cols=2, subplot_titles=[f"Winning vote % vs {g} share" for g in pick])
for i, g in enumerate(pick):
    r_, c_ = i // 2 + 1, i % 2 + 1
    x, y = df["PERCENTAGE"], df[g + " %"]; m, b = np.polyfit(x, y, 1)
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers+text", text=df["Year"].astype(str), textposition="top center",
                             marker=dict(color=COLORS[g], size=9), showlegend=False), row=r_, col=c_)
    fig.add_trace(go.Scatter(x=[x.min(), x.max()], y=[m * x.min() + b, m * x.max() + b], mode="lines",
                             line=dict(color="black", dash="dash"), showlegend=False), row=r_, col=c_)
    fig.update_xaxes(title_text="Winning party vote (%)", row=r_, col=c_); fig.update_yaxes(title_text=f"{g} share (%)", row=r_, col=c_)
fig.update_layout(template="plotly_white", height=750, title="Scatter plots with trend line")
fig.write_html(f"{CHART_DIR}/elections_scatter_grid.html")

# ---------------------------------------------------------------- matplotlib (static, for the report)
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(df["Year"].astype(str), df["PERCENTAGE"], color=[PARTY_COLORS.get(p, "grey") for p in df["PARTY"]])
for i, (pct, p) in enumerate(zip(df["PERCENTAGE"], df["PARTY"])): ax.text(i, pct + 0.6, p, ha="center", fontsize=7)
ax.axhline(df["PERCENTAGE"].median(), ls="--", color="k", lw=0.8)
ax.set_ylabel("% of total votes"); ax.set_title("Vote share of winning party per Lok Sabha election"); plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_winning_share.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.stackplot(movies["Year"], [movies[g + " %"] for g in GENRES], labels=GENRES, colors=[COLORS[g] for g in GENRES], alpha=0.85)
ax.set_ylim(0, 100); ax.set_ylabel("Genre share (%)"); ax.set_xlabel("Year")
ax2 = ax.twinx(); ax2.plot(df["Year"], df["PERCENTAGE"], "ko-", lw=2.5, label="Winning party vote %"); ax2.set_ylim(0, 60)
ax2.set_ylabel("Winning party vote (%)")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
ax.set_title("Genre mix of Indian movies vs winning party's vote share")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_genre_mix_vs_vote_share.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5)); xs = np.arange(len(corr_year)); w = 0.38
ax.bar(xs - w / 2, corr_year["Spearman rho"], w, label="Election year", color="#2e86de")
ax.bar(xs + w / 2, corr_3yr["Spearman rho"], w, label="3-year average", color="#e4572e")
ax.axhline(0, color="k", lw=0.8); ax.set_xticks(xs); ax.set_xticklabels(corr_year["Genre"], rotation=30, ha="right")
ax.set_ylabel("Spearman rho with winning vote %"); ax.legend(); ax.set_title("Genre share vs winning party vote % (n = 17)")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_correlation_bars.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5)); xs = np.arange(len(mw))
ax.bar(xs - w / 2, mw["Mean (weak)"], w, label="Weak mandate", color="#e4572e"); ax.bar(xs + w / 2, mw["Mean (strong)"], w, label="Strong mandate", color="#2e86de")
ax.set_xticks(xs); ax.set_xticklabels(mw["Genre"], rotation=30, ha="right"); ax.set_ylabel("Average genre share (%)")
ax.legend(); ax.set_title("Genre share in election years: weak vs strong mandates")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_weak_vs_strong.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5)); bottom = np.zeros(len(dec))
for g in GENRES:
    ax.bar(dec.index, dec[g + " %"], bottom=bottom, color=COLORS[g], label=g); bottom += dec[g + " %"].values
ax.set_ylabel("Genre share (%)"); ax2 = ax.twinx(); ax2.plot(decade.index, decade["avg_win_pct"], "ko-", lw=2.5, label="Avg winning vote %")
ax2.set_ylim(0, 60); ax2.set_ylabel("Avg winning vote (%)")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False)
ax.set_title("Decade-by-decade genre mix and average winning vote %")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_decade_mix.png", dpi=150); plt.close(fig)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, g in zip(axes.ravel(), pick):
    x, y = df["PERCENTAGE"], df[g + " %"]; m, b = np.polyfit(x, y, 1); r, p = stats.pearsonr(x, y)
    ax.scatter(x, y, color=COLORS[g])
    for xi, yi, yr in zip(x, y, df["Year"]): ax.annotate(str(yr)[2:], (xi, yi), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.plot([x.min(), x.max()], [m * x.min() + b, m * x.max() + b], "k--")
    ax.set_title(f"{g}: r = {r:.2f}, p = {p:.3f}"); ax.set_xlabel("Winning party vote (%)"); ax.set_ylabel(f"{g} share (%)")
fig.tight_layout(); fig.savefig(f"{CHART_DIR}/elections_scatter_grid.png", dpi=150); plt.close(fig)

# ---------------------------------------------------------------- summary
f = lambda t: t.round(3).to_string(index=False)
lines = ["MOVIES vs ELECTIONS (1951-2019, n = %d general elections)" % len(df), "=" * 60,
         "Excluded as non-general-election records: " + ", ".join(f"{r.Year} ({r.PARTY}, {r.VOTES:,} votes)" for r in suspect.itertuples()),
         "\nA) Winning vote % vs genre share in election year", f(corr_year),
         "\nB) Same, using 3-year average around the election (robustness)", f(corr_3yr),
         "\nB2) PARTIAL correlation - effect of Year removed (the fairer test)", f(partial),
         "\nC) Weak vs strong mandate (split at median %.1f%%) - Mann-Whitney U" % df["PERCENTAGE"].median(), f(mw),
         "\nD) Decade summary", decade.to_string(),
         "\nSignificant after removing the time trend (p<0.05): " + (", ".join(partial.loc[partial["p"] < 0.05, "Genre"]) or "none"),
         "\nSignificant (Pearson p<0.05, election year, no trend control): " + (", ".join(corr_year.loc[corr_year["Pearson p"] < 0.05, "Genre"]) or "none"),
         "\nCaveat: winning vote share is a rough proxy for dissatisfaction, and 70 years of changing cinema is a confound."]
open(f"{RES_DIR}/elections_summary.txt", "w").write("\n".join(lines))
print("\n".join(lines))
