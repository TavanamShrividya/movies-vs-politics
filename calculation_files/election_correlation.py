"""Correlate movie genre ratios with winning-party election vote percentages.

Run this script from the repository root. It reads:
    organized_data/movies_ratio.csv
    organized_data/elections.csv

Alignment assumption:
- If the election file has Start_Year and End_Year, each election is treated as
  an inclusive period. Annual movie genre ratios in that interval are averaged
  to create one genre profile for that election period.
- Otherwise, the election file must have YEAR (or Start_Year) and each election
  is aligned to the movie data for that exact year. No period boundaries are
  inferred from gaps between election years.

The output contains the basic Pearson correlation, correlation with the
first difference in vote percentage, and correlation between the previous
period's vote percentage and the current period's movie genre ratios.
"""

from pathlib import Path

import pandas as pd


DATA_DIR = Path("organized_data")
RESULT_PATH = Path("results") / "correlation_with_elections.csv"
MOVIES_PATH = DATA_DIR / "movies_ratio.csv"
ELECTIONS_PATH = DATA_DIR / "elections.csv"


def find_column(frame: pd.DataFrame, candidates: list[str], description: str) -> str:
    """Return the first case-insensitive matching column name."""
    normalized = {str(column).strip().casefold(): column for column in frame.columns}
    for candidate in candidates:
        found = normalized.get(candidate.casefold())
        if found is not None:
            return found
    raise ValueError(
        f"Could not find {description}. Expected one of {candidates}; "
        f"found columns: {list(frame.columns)}"
    )


def numeric_years(series: pd.Series, label: str) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any():
        bad_rows = values.index[values.isna()].tolist()[:5]
        raise ValueError(f"{label} contains missing or non-numeric years at rows {bad_rows}.")
    return values.astype(int)


def build_aligned_data(movies: pd.DataFrame, elections: pd.DataFrame,
                       movie_year_col: str, vote_col: str) -> tuple[pd.DataFrame, list[str]]:
    genre_cols = [column for column in movies.columns if column != movie_year_col]
    if not genre_cols:
        raise ValueError("movies_ratio.csv must contain at least one genre column.")

    movies = movies.copy()
    elections = elections.copy()
    movies[movie_year_col] = numeric_years(movies[movie_year_col], movie_year_col)
    elections[vote_col] = pd.to_numeric(elections[vote_col], errors="coerce")

    start_col = find_column(elections, ["Start_Year"], "period start year") if any(
        str(c).strip().casefold() == "start_year" for c in elections.columns
    ) else None
    end_col = find_column(elections, ["End_Year"], "period end year") if any(
        str(c).strip().casefold() == "end_year" for c in elections.columns
    ) else None

    if start_col and end_col:
        elections[start_col] = numeric_years(elections[start_col], start_col)
        elections[end_col] = numeric_years(elections[end_col], end_col)
        if (elections[end_col] < elections[start_col]).any():
            raise ValueError("Election period End_Year cannot be earlier than Start_Year.")

        # One row per election period: average the annual genre ratios over
        # the inclusive interval; preserve election-file order for differencing.
        rows = []
        movie_years = movies[movie_year_col]
        for _, election in elections.iterrows():
            start, end = int(election[start_col]), int(election[end_col])
            mask = movie_years.between(start, end, inclusive="both")
            period_movies = movies.loc[mask, genre_cols]
            if period_movies.empty:
                continue
            row = period_movies.mean(numeric_only=True).to_dict()
            row["_vote_percentage"] = election[vote_col]
            row["_period_start"] = start
            rows.append(row)
        full = pd.DataFrame(rows)
        if full.empty:
            raise ValueError("No election periods overlap the years in movies_ratio.csv.")
        full = full.sort_values("_period_start", kind="stable").reset_index(drop=True)
        return full, genre_cols

    # Annual election data: align matching calendar years exactly.
    election_year_col = find_column(
        elections, ["YEAR", "Start_Year"], "election year"
    )
    elections[election_year_col] = numeric_years(elections[election_year_col], election_year_col)
    election_rows = elections[[election_year_col, vote_col]].rename(
        columns={election_year_col: "_year", vote_col: "_vote_percentage"}
    )
    movie_rows = movies.rename(columns={movie_year_col: "_year"})
    full = movie_rows.merge(election_rows, on="_year", how="inner", sort=True)
    if full.empty:
        raise ValueError("No election years match Year values in movies_ratio.csv.")
    return full.reset_index(drop=True), genre_cols


def main() -> None:
    movies = pd.read_csv(MOVIES_PATH)
    elections = pd.read_csv(ELECTIONS_PATH)

    movie_year_col = find_column(movies, ["Year"], "movie year column")
    vote_col = find_column(
        elections,
        ["PERCENTAGE", "Vote_Percentage", "Winning_Vote_Percentage"],
        "winning-party vote percentage column",
    )

    full, genres = build_aligned_data(movies, elections, movie_year_col, vote_col)
    vote = full["_vote_percentage"]

    # Match the sample scripts' Pearson corrwith method. The lag compares the
    # previous period's election vote share with the current period's genres.
    correlation = full[genres].corrwith(vote)
    vote_change = vote.diff()
    correlation_change = full[genres].corrwith(vote_change)
    correlation_lag = full[genres].corrwith(vote.shift(1))

    result = pd.DataFrame(
        {
            "genre": genres,
            "Correlation": correlation.reindex(genres).to_numpy(),
            "With change in winning-party vote percentage": correlation_change.reindex(genres).to_numpy(),
            "prev. period winning-party vote percentage vs curr. period movies": correlation_lag.reindex(genres).to_numpy(),
        }
    ).round(3)
    result = result.sort_values("Correlation", key=lambda values: values.abs(), ascending=False)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(RESULT_PATH, index=False)
    print(f"Saved election correlation results to {RESULT_PATH}")


if __name__ == "__main__":
    main()
