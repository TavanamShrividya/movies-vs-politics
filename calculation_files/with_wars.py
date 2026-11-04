import pandas as pd

MAX_LAG = 10

movies = pd.read_csv("../organized_data/movies.csv").sort_values("Year")
wars = pd.read_csv("../organized_data/wars.csv")

war_years = sorted(wars["Year"].dropna().astype(int).unique())
genres = [col for col in movies.columns if col != "Year"]

movies["War_Share"] = movies["War"] / movies[genres].sum(axis=1)

event_results = []

for i, war_year in enumerate(war_years):
    if i + 1 < len(war_years):
        last_year = min(MAX_LAG + war_year, war_years[i + 1] - 1)
    else:
        last_year = war_year + MAX_LAG

    after = movies[
        (movies["Year"] > war_year) &
        (movies["Year"] <= last_year)
    ]

    if after.empty:
        continue

    peak = after.loc[after["War_Share"].idxmax()]

    event_results.append({
        "war_year": war_year,
        "peak_year": int(peak["Year"]),
        "years_until_peak": int(peak["Year"] - war_year),
        "peak_war_movie_count": int(peak["War"])
    })

events = pd.DataFrame(event_results).round(2)
events.to_csv("../results/war_movie_peak_after_each_war.csv", index=False)