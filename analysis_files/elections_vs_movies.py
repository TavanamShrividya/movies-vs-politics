# Election wise movies (1951 - 2019)
# run from the main repo folder: python analysis_files/elections_vs_movies.py

import pandas as pd
import matplotlib.pyplot as plt

movies = pd.read_csv("organized_data/election_wise_movies.csv")

genres = ["Action", "Comedy", "Crime", "Non-fiction", "Drama", "Horror", "Romance", "War"]

# every row is the time between two elections, label for the x axis like 1951-57
movies["Period"] = movies["Start_Year"].astype(str) + "-" + (movies["End_Year"] % 100).astype(str).str.zfill(2)

# Chart : ratio of each genre in every election period
plt.figure(figsize=(11, 6))
for g in genres:
    plt.plot(movies["Period"], movies[g], marker="o", label=g)
plt.xlabel("Election period")
plt.ylabel("Ratio of movies")
plt.xticks(rotation=60)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=8)
plt.title("Ratio of movies in each genre in every election period")
plt.tight_layout()
plt.savefig("analysis_files/elections_vs_movies.png", dpi=150)

plt.show()
