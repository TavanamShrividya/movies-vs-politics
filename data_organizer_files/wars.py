import pandas as pd

# 1948 - 2025
# Organizing war_post_ind.csv, major_operations.csv to find war tense periods/ years of india
# for wars, nearly all finished within the same year but one so stacking start, end years will work
# sorted by the date, dropping duplicate dates(only need years of war, not number of wars)

wars1= pd.read_csv("raw_data/wars_post_ind.csv", usecols=['start_year'])
wars2= pd.read_csv("raw_data/wars_post_ind.csv", usecols=['end_year'])
ops= pd.read_csv("raw_data/major_operations.csv", header= None, usecols=[1])

ops[1]=ops[1].astype(str).str[:4]

wars1.to_csv("organized_data/wars.csv", index=0)
wars2.to_csv("organized_data/wars.csv", mode = 'a', header = False, index = False)
ops.to_csv("organized_data/wars.csv", mode = 'a', header = False, index = False)

df = pd.read_csv("organized_data/wars.csv", usecols=['start_year']).drop_duplicates('start_year').sort_values(by= "start_year")
df.rename(columns={'start_year':'Year'}, inplace=True)

# removing 2025 to align with the elections dataset
df= df[~df["Year"].isin([2025])]

df.to_csv("organized_data/wars.csv", index=0)

