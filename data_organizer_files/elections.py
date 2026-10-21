import pandas as pd

# Organizing elections_dataset.csv - 1951 to 2019
# og dataset contained state, party, candidate. Candidate column was dropped as the focus is only on the party's (so added all the votes candidate of candidates belonging to same party)
elections= pd.read_csv("raw_data/elections_dataset.csv", usecols=['YEAR','PARTY','VOTES']).sort_values(by="YEAR")
total_votes= elections.groupby(["YEAR","PARTY"], as_index=False)['VOTES'].sum()

# added all the votes in year to get total votes, took percentage for each party
# found highest percent each year, dropped all the other rows(party) for that year
total_votes["PERCENTAGE"]= ((total_votes["VOTES"])/( total_votes.groupby("YEAR")["VOTES"].transform("sum"))*100)
total_votes = total_votes.loc[total_votes.groupby("YEAR")["PERCENTAGE"].idxmax()].reset_index(drop=True)

total_votes.to_csv("organized_data/elections.csv", index=0)