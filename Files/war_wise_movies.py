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
    kind="line",
    marker="o",
    figsize=(16, 9),
    colormap="tab10",
)

war_line = ax.lines[genres.index("War")]
war_line.set_zorder(10)
war_line.set_linewidth(3)

# Show every period label along the bottom
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df["Period"], rotation=90, ha="center")

ax.set_title("Movie Genre Ratios by Period")
ax.set_xlabel("Start year–end year")
ax.set_ylabel("Share of movies (%)")
ax.legend(title="Genre")

plt.tight_layout()
plt.savefig("war_wise_movies.png", dpi=300, bbox_inches="tight")
plt.show()