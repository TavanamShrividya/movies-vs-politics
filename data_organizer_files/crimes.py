import pandas as pd

# Organizing crimes_2001-2012.csv to only include year and number of crimes
# og data set was district wise, got total per state, total from year from there,changed col name
crimes = pd.read_csv("raw_data/crimes_2001-2012.csv", usecols=['DISTRICT','YEAR','TOTAL IPC CRIMES'])

df = crimes[crimes['DISTRICT']=="TOTAL"]
df = df.groupby('YEAR')['TOTAL IPC CRIMES'].sum().reset_index()

# renamed column
df.rename(columns={'YEAR':'Year'}, inplace=True)
df.rename(columns={'TOTAL IPC CRIMES':'Crimes'}, inplace=True)
df.to_csv("organized_data/crimes.csv", index=0)