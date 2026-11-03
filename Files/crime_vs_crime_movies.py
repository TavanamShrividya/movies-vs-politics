import matplotlib.pyplot as plt
import pandas as pd

crimes = pd.read_csv("../organized_data/crimes.csv")
movies = pd.read_csv("../organized_data/movies.csv")

df = pd.merge(
    crimes,
    movies[["Year", "Crime"]],
    on="Year",
    how="inner"
).sort_values("Year")

fig, ax1 = plt.subplots(figsize=(10, 6))

# Movie crime share, shown as a percentage
line1, = ax1.plot(
    df["Year"],
    df["Crime"] * 100,
    color="blue",
    marker="o",
    label="Crime genre movies (%)"
)
ax1.set_xlabel("Year")
ax1.set_ylabel("Crime genre movies (%)", color="blue")

# Reported crimes, shown in millions
ax2 = ax1.twinx()
line2, = ax2.plot(
    df["Year"],
    df["Crimes"] / 1_000_000,
    color="crimson",
    marker="o",
    label="Reported crimes (millions)"
)
ax2.set_ylabel("Reported crimes (millions)", color="crimson")

ax1.set_title("Reported Crimes and Crime Genre Movies Over Time")
ax1.legend([line1, line2], [line1.get_label(), line2.get_label()], loc="best")

plt.tight_layout()
plt.savefig("crimes_vs_crime_movies.png", dpi=300, bbox_inches="tight")
plt.show()