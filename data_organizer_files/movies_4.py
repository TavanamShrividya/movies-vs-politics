
import pandas as pd

# --------------------------------------------------
# 1. Read election years
# --------------------------------------------------

elections = pd.read_csv(
    "raw_data/elections_dataset.csv",
    usecols=["YEAR"]
)

election_years = sorted(
    elections["YEAR"].dropna().astype(int).unique()
)

# Observation periods between consecutive elections
periods = list(zip(election_years[:-1], election_years[1:]))

# --------------------------------------------------
# 2. Read and clean movies
# --------------------------------------------------

movies = pd.read_csv(
    "raw_data/movies_dataset.csv",
    usecols=["Year", "Genre"]
)

movies["Genre"] = (
    movies["Genre"]
    .str.split(",")
    .str[0]
    .str.strip()
)

movies = movies[movies["Genre"] != "-"]

# Valid release years
movies = movies[
    movies["Year"].str.fullmatch(r"\d{4}", na=False)
]

movies["Year"] = movies["Year"].astype(int)

movies = movies[movies["Year"] > 1949]

# --------------------------------------------------
# 3. Remove unpopular genres
# --------------------------------------------------

removed_genres = [
    "Adventure", "Animation", "News", "Reality-TV",
    "Short", "Talk-Show", "War", "Music", "Musical",
    "Sport", "Sci-Fi", "Fantasy"
]

movies = movies[
    ~movies["Genre"].isin(removed_genres)
]

# --------------------------------------------------
# 4. Combine similar genres
# --------------------------------------------------

genre_map = {
    "Thriller": "Crime",
    "Mystery": "Horror",
    "Family": "Drama",
    "Biography": "Non-fiction",
    "History": "Non-fiction"
}

movies["Genre"] = movies["Genre"].replace(genre_map)

# --------------------------------------------------
# 5. Count movies genre-wise for each year
# --------------------------------------------------

yearly = pd.crosstab(
    movies["Year"],
    movies["Genre"]
)

# --------------------------------------------------
# 6. Add war movie counts
# --------------------------------------------------

war_movies = pd.read_csv(
    "raw_data/war_themed_movies.csv",
    usecols=["count"]
)

# Assuming war counts correspond to consecutive years
# starting from 1950, as in the original organiser
war_movies["Year"] = range(
    1950, 1950 + len(war_movies)
)

war_movies = war_movies.set_index("Year")

yearly["War"] = war_movies["count"].reindex(
    yearly.index
).fillna(0)

# --------------------------------------------------
# 7. Aggregate movies between elections
# --------------------------------------------------

results = []

for start, end in periods:

    # Movies released from the starting election
    # year up to (but excluding) the next election
    period_counts = yearly.loc[
        (yearly.index >= start) &
        (yearly.index < end)
    ].sum()

    # Calculate genre proportions
    period_ratios = (
        period_counts / period_counts.sum()
    ).round(4)

    # Store results
    row = period_ratios.to_dict()

    row["Start_Year"] = start
    row["End_Year"] = end

    results.append(row)

# --------------------------------------------------
# 8. Create final dataset
# --------------------------------------------------

combined = pd.DataFrame(results)

combined = combined[
    ["Start_Year", "End_Year"] +
    [col for col in combined.columns
     if col not in ["Start_Year", "End_Year"]]
]

combined.to_csv(
    "organized_data/movies_election_periods.csv",
    index=False
)
