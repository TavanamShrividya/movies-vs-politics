import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("correlation/correlation_results/correlation_with_crimes.csv")
df = df.sort_values("Correlation", ascending=True)

plt.figure(figsize=(9, 5))
plt.bar(df["genre"], df["Correlation"])
plt.axhline(0, color="black", linewidth=0.8)

plt.xlabel("Movie genre")
plt.ylabel("Correlation coefficient")
plt.title("Correlation Between Movie Genres and Crime")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    "correlation/graphs/movie_genre_crime_correlation.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()