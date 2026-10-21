import pandas as pd

# 2000 - 2026
# Organizing protest_dataset.csv to only include start of protest dates (other data is either irrelevant or missing (like death count))
# 'end_date' is not used as it doesn't show the start of dissatisfaction
# sorted by the date, calculating number of protests per year

protests = pd.read_csv("raw_data/protest_dataset.csv", usecols=['start_date'])

# to get year
protests['start_date']=protests['start_date'].str.split('-').str[0].str.strip()

# sort - index == otherwise reverse sorted, resed_index == otherwise it was single columned
# value - counts == find no. of protests per year
number = protests.value_counts().sort_index().reset_index()
number.columns = ['protests','Protests']

number.rename(columns={'protests':'Year'}, inplace=True)

# removing 2023, 2024, 2025, 2026 to align with the elections dataset
number= number[~number["Year"].isin(['2023', '2024','2025', '2026'])]

number.to_csv("organized_data/protests.csv", index=0)
