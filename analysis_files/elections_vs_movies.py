# Election wise movies (1951 - 2019)
# run from the main repo folder: python analysis_files/elections_vs_movies.py

import pandas as pd
import matplotlib.pyplot as plt

movies = pd.read_csv("organized_data/election_wise_movies.csv")
elections = pd.read_csv("organized_data/elections.csv")

genres = ["Action", "Comedy", "Crime", "Non-fiction", "Drama", "Horror", "Romance", "War"]

# vote % of the party that won the election at the start of each period
elections = elections.rename(columns={"YEAR": "Start_Year"})
data = pd.merge(movies, elections[["Start_Year", "PERCENTAGE"]], on="Start_Year")

# label for the x axis, like 1951-57
data["Period"] = data["Start_Year"].astype(str) + "-" + (data["End_Year"] % 100).astype(str).str.zfill(2)

# Chart : winning vote % (bars) and ratio of each genre (lines)
fig, ax1 = plt.subplots(figsize=(11, 6))
ax1.bar(data["Period"], data["PERCENTAGE"], color="lightgrey")
ax1.set_xlabel("Election period")
ax1.set_ylabel("Vote % of winning party")
ax1.tick_params(axis="x", rotation=60)

ax2 = ax1.twinx()
for g in genres:
    ax2.plot(data["Period"], data[g], marker="o", label=g)
ax2.set_ylabel("Ratio of movies")
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=8)

plt.title("Winning party vote % vs ratio of movies in each genre")
plt.tight_layout()
plt.savefig("analysis_files/elections_vs_movies.png", dpi=150)

plt.show()
