import pandas as pd
import matplotlib.pyplot as plt

movies = pd.read_csv("organized_data/movies.csv")
puc = pd.read_csv("organized_data/puc_2001_2012.csv")

genres = ["Action", "Comedy", "Crime", "Non-fiction", "Drama", "Horror", "Romance", "War"]

# total movies in each year
movies["total"] = movies[genres].sum(axis=1)

# ratio of each genre
for g in genres:
    movies[g] = movies[g] / movies["total"]

# only keep years 2001 to 2012
data = pd.merge(movies, puc, on="Year")

fig, ax1 = plt.subplots(figsize=(10, 6))

# bar graph for puc
ax1.bar(data["Year"], data["PUC"], color="lightgray")
ax1.set_xlabel("Year")
ax1.set_ylabel("PUC")
ax1.set_xticks(data["Year"])

# line graph for ratio of movies
ax2 = ax1.twinx()
for g in genres:
    ax2.plot(data["Year"], data[g], marker="o", label=g)
ax2.set_ylabel("Ratio of movies")

# put lines in front of bars
ax2.set_zorder(ax1.get_zorder() + 1)
ax2.patch.set_visible(False)

plt.title("PUC vs ratio of movies in each genre")
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=8)

plt.tight_layout()
plt.savefig("movies_vs_puc.png")
plt.show()
