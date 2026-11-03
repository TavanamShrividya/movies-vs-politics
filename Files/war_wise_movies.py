import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("../organized_data/war_wise_movies.csv")

genres = [
    "Action", "Comedy", "Crime", "Non-fiction",
    "Drama", "Horror", "Romance", "War"
]

df["Period"] = df["Start_Year"].astype(str) + "–" + df["End_Year"].astype(str)
df[genres] = df[genres] * 100

ax = df.plot(
    x="Period",
    y=genres,
    kind="barh",
    stacked=True,
    figsize=(11, 8),
    colormap="tab10"
)

ax.set_title("Movie Genres by War Period")
ax.set_xlabel("Share of movies (%)")
ax.set_ylabel("Year range")
ax.set_xlim(0, 100)
ax.legend(title="Genre", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig("war_wise_movies.png", dpi=300, bbox_inches="tight")
plt.show()