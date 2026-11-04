from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "organized_data"
OUTPUT_FILE = DATA_DIR / "puc_2001_2012.csv"

START_YEAR = 2001
END_YEAR = 2012

WEIGHTS = {
    "electoral": 0.15,
    "crime": 0.40,
    "protests": 0.35,
    "war": 0.10,
}


def read_csv(filename):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}")
    return pd.read_csv(path)


def find_column(df, candidates, file_label):
    """Find a column case-insensitively, allowing common naming variations."""
    lookup = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    raise ValueError(
        f"Could not find any of {candidates} in {file_label}. "
        f"Available columns: {list(df.columns)}"
    )


def minmax(series):
    """Min-max normalize; constant series becomes 0 to avoid division by zero."""
    series = pd.to_numeric(series, errors="coerce")
    minimum, maximum = series.min(), series.max()
    if pd.isna(minimum) or pd.isna(maximum):
        raise ValueError("Cannot normalize a column containing no valid values.")
    if maximum == minimum:
        return pd.Series(0.0, index=series.index)
    return (series - minimum) / (maximum - minimum)


def load_annual_count(filename, value_candidates, label):
    df = read_csv(filename)
    year_col = find_column(df, ["Year", "YEAR"], filename)
    value_col = find_column(df, value_candidates, filename)

    df = df[[year_col, value_col]].copy()
    df.columns = ["Year", label]
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df[label] = pd.to_numeric(df[label], errors="coerce")
    df = df.dropna(subset=["Year", label])
    df["Year"] = df["Year"].astype(int)

    # If a year occurs more than once, add its counts.
    return df.groupby("Year", as_index=False)[label].sum()


def load_war_years():
    """Support either a wars.csv with a Year column or a list of event years."""
    df = read_csv("wars.csv")
    year_col = find_column(df, ["Year", "YEAR"], "wars.csv")
    years = pd.to_numeric(df[year_col], errors="coerce").dropna().astype(int)
    return set(years)


def load_election_scores():
    df = read_csv("elections.csv")
    year_col = find_column(df, ["YEAR", "Year"], "elections.csv")
    pct_col = find_column(
        df, ["PERCENTAGE", "Percentage", "Vote Percentage", "Vote_Share"],
        "elections.csv"
    )

    df = df[[year_col, pct_col]].copy()
    df.columns = ["ElectionYear", "VoteShare"]
    df["ElectionYear"] = pd.to_numeric(df["ElectionYear"], errors="coerce")
    df["VoteShare"] = pd.to_numeric(df["VoteShare"], errors="coerce")
    df = df.dropna().sort_values("ElectionYear")
    df["ElectionYear"] = df["ElectionYear"].astype(int)

    # Electoral component: lower winning-party vote share => higher component.
    df["ElectoralComponent"] = 1 - df["VoteShare"] / 100
    return df[["ElectionYear", "ElectoralComponent"]].reset_index(drop=True)


def nearest_election_component(year, elections):
    """Return component from closest election; ties go to the earlier election."""
    distances = (elections["ElectionYear"] - year).abs()
    min_distance = distances.min()
    tied = elections.loc[distances == min_distance]
    chosen = tied.sort_values("ElectionYear").iloc[0]
    return float(chosen["ElectoralComponent"])


def main():
    years = pd.DataFrame({"Year": range(START_YEAR, END_YEAR + 1)})

    crimes = load_annual_count("crimes.csv", ["Crimes", "Crime", "CrimeCount"], "Crimes")
    protests = load_annual_count(
        "protests.csv", ["Protests", "Protest", "ProtestCount"], "Protests"
    )

    # Merge annual crime and protest counts.
    data = years.merge(crimes, on="Year", how="left")
    data = data.merge(protests, on="Year", how="left")

    # Missing values are NOT silently treated as zero.
    missing_crime = data.loc[data["Crimes"].isna(), "Year"].tolist()
    missing_protests = data.loc[data["Protests"].isna(), "Year"].tolist()
    if missing_crime or missing_protests:
        raise ValueError(
            "Missing annual observations. "
            f"Crime missing in: {missing_crime}; "
            f"protests missing in: {missing_protests}. "
            "Add the data or explicitly decide whether missing means zero."
        )

    # Normalize within the requested 2001–2012 window.
    data["Crime_norm"] = minmax(data["Crimes"])
    data["Protests_norm"] = minmax(data["Protests"])

    # War indicator: 1 if the year appears in wars.csv, otherwise 0.
    war_years = load_war_years()
    data["War"] = data["Year"].isin(war_years).astype(int)

    # Assign each year the electoral component of its nearest general election.
    elections = load_election_scores()
    data["Electoral"] = data["Year"].apply(
        lambda year: nearest_election_component(year, elections)
    )

    data["PUC"] = 100 * (
        WEIGHTS["electoral"] * data["Electoral"]
        + WEIGHTS["crime"] * data["Crime_norm"]
        + WEIGHTS["protests"] * data["Protests_norm"]
        + WEIGHTS["war"] * data["War"]
    )

    # Output exactly the requested columns.
    result = data[["Year", "PUC"]].copy()
    result["PUC"] = result["PUC"].round(4)
    result.to_csv(OUTPUT_FILE, index=False)



if __name__ == "__main__":
    main()
