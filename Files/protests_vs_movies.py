import matplotlib.pyplot as plt
import pandas as pd

movies = pd.read_csv("../organized_data/movies.csv")
protests = pd.read_csv("../organized_data/protests.csv")

df = pd.merge(movies, protests, on="Year", how="inner").sort_values("Year")

genres = [
    "Action", "Comedy", "Crime", "Non-fiction",
    "Drama", "Horror", "Romance", "War"
]

# Compress movie lines slightly
df[genres] = df[genres] * 0.9

# Rescale protests into the space above the movie lines
lowest = df["Protests"].min()
highest = df["Protests"].max()
df["Protests_scaled"] = (
    0.65 + (df["Protests"] - lowest) / (highest - lowest) * 0.35
)

colors = [
    "blue", "orange", "green", "red",
    "purple", "brown", "pink", "gray", "crimson"
]

ax = df.plot(
    x="Year",
    y=genres + ["Protests_scaled"],
    kind="line",
    color=colors,
    marker="o",
    figsize=(12, 7)
)

ax.set_title("Movie Genre Shares and Protests Over Time")
ax.set_xlabel("Year")
ax.set_ylabel("Movie shares and display-scaled protests")
ax.set_ylim(0, 1.05)
ax.legend(title="Category")

plt.tight_layout()
plt.savefig("movies_and_protests.png", dpi=300, bbox_inches="tight")
plt.show()