import matplotlib.pyplot as plt
import pandas as pd

puc = pd.read_csv("data/organized_data/puc_2001_2012.csv")
movies = pd.read_csv("data/organized_data/movies.csv")

full = movies.merge(puc, on="Year", how="inner")
genres = [col for col in movies.columns if col != "Year"]

correlations = (
    full[genres]
    .corrwith(full["PUC"])
    .sort_values(ascending=False)
)

# Save the correlation for each genre
correlation_file = correlations.rename_axis("genre").reset_index(name="Correlation")
correlation_file.round(3).to_csv(
    "correlation/correlation_results/with_puc.csv",
    index=False
)

# Plot the correlations
plt.figure(figsize=(9, 5))
plt.bar(correlations.index, correlations.values)
plt.axhline(0, color="black", linewidth=0.8)

plt.xlabel("Movie genre")
plt.ylabel("Correlation coefficient")
plt.title("Correlation Between Movie Genres and PUC")
plt.xticks(rotation=45, ha="right")
plt.ylim(-1, 1)
plt.tight_layout()

plt.savefig(
    "correlation/graphs/movie_genre_puc_correlation.png",
    dpi=300,
    bbox_inches="tight"
)
