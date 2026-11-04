import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("../correlation_results/correlation_with_protests.csv")
df = df.sort_values("Correlation", ascending=True)

plt.figure(figsize=(9, 5))
plt.bar(df["genre"], df["Correlation"])
plt.axhline(0, color="black", linewidth=0.8)

plt.xlabel("Movie genre")
plt.ylabel("Correlation coefficient")
plt.title("Correlation Between Movie Genres and Protests")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    "../graphs/movie_genre_protest_correlation.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()