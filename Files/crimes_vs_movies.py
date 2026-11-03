import matplotlib.pyplot as plt
import pandas as pd

movies = pd.read_csv("../organized_data/movies.csv")
crimes = pd.read_csv("../organized_data/crimes.csv")

genres = [
    "Action", "Comedy", "Crime", "Non-fiction",
    "Drama", "Horror", "Romance", "War"
]

# Keep only years that appear in both files
df = pd.merge(movies, crimes, on="Year", how="inner").sort_values("Year")

# Scaling so that crime fits in the graph 
df["Crimes_millions"] = df["Crimes"] / 1_000_000
df[genres] = df[genres] * 3

colors = [
    "red", "blue", "green", "orange",
    "purple", "brown", "pink", "black", "crimson"
]

ax = df.plot(
    x="Year",
    y=genres + ["Crimes_millions"],
    kind="line",
    color=colors,
    marker="o",
    figsize=(12, 7)
)

ax.set_title("Movie Genre Shares and Crimes, 2001–2012")
ax.set_xlabel("Year")
ax.set_ylabel("Genre share × 3 / crimes in millions")
ax.set_xticks(df["Year"])
ax.legend(title="Category")
plt.tight_layout()
plt.savefig("crimes_vs_movies.png", dpi=300, bbox_inches="tight")
plt.show()