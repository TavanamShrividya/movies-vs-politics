import matplotlib.pyplot as plt
import pandas as pd

movies = pd.read_csv("../organized_data/election_wise_movies.csv")
elections = pd.read_csv("../organized_data/elections.csv")

genres = [
    "Action", "Comedy", "Crime", "Non-fiction",
    "Drama", "Horror", "Romance", "War"
]

df = movies.merge(
    elections[["YEAR", "PARTY", "PERCENTAGE"]],
    left_on="Start_Year",
    right_on="YEAR",
    how="left",
)

df["Period"] = df["Start_Year"].astype(str) + "–" + df["End_Year"].astype(str)
df[genres] = df[genres] * 100

ax = df.plot(
    x="Period",
    y=genres,
    kind="line",
    marker="o",
    figsize=(16, 9),
    colormap="tab10",
)

# Add election percentages as translucent background bars.
ax.bar(
    df["Period"],
    df["PERCENTAGE"],
    color="gray",
    alpha=0.2,
    width=0.8,
    label="Winning party vote (%)",
    zorder=1,
)

# Keep genre lines in front of the bars.
for line in ax.lines:
    line.set_zorder(3)

ax.set_title("Movie Genre Ratios and Election Results by Period")
ax.set_xlabel("Start year–end year")
ax.set_ylabel("Percentage (%)")
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df["Period"], rotation=90)
ax.legend(title="Genre / election result", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig("election_wise_movies.png", dpi=300, bbox_inches="tight")
plt.show()