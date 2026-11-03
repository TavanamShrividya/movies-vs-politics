# Crimes vs movies (2001 - 2012)
# run from the main repo folder: python analysis_files/crimes_vs_movies.py

import pandas as pd
import matplotlib.pyplot as plt

movies = pd.read_csv("organized_data/movies.csv")
crimes = pd.read_csv("organized_data/crimes.csv")

genres = ["Action", "Comedy", "Crime", "Non-fiction", "Drama", "Horror", "Romance", "War"]

# if movies.csv still has number of movies, change it to a ratio
# (movies of a genre / all movies of that year)
if movies["Action"].max() > 1:
    total = movies[genres].sum(axis=1)
    for g in genres:
        movies[g] = movies[g] / total

# keep only the years that are in both files (2001 - 2012)
data = pd.merge(movies, crimes, on="Year")

# Chart 1 : crimes and all genres
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(data["Year"], data["Crimes"], color="lightgrey")
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of crimes")
ax1.set_xticks(data["Year"])

ax2 = ax1.twinx()
for g in genres:
    ax2.plot(data["Year"], data[g], marker="o", label=g)
ax2.set_ylabel("Ratio of movies")
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=8)

plt.title("Crimes vs ratio of movies in each genre")
plt.tight_layout()
plt.savefig("analysis_files/charts/crimes_vs_movies.png", dpi=150)

# Chart 2 : crimes and crime movies
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(data["Year"], data["Crimes"], color="red", marker="o")
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of crimes", color="red")
ax1.set_xticks(data["Year"])

ax2 = ax1.twinx()
ax2.plot(data["Year"], data["Crime"], color="blue", marker="o")
ax2.set_ylabel("Ratio of crime movies", color="blue")

plt.title("Crimes vs crime movies")
plt.tight_layout()
plt.savefig("analysis_files/charts/crimes_vs_crime_movies.png", dpi=150)

plt.show()
