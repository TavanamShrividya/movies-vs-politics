import pandas as pd

#finding correlation of election win percentages and movie genres
#reading elections and movies
elections=pd.read_csv("data/organized_data/elections.csv", usecols=["YEAR","PERCENTAGE"])
movies=pd.read_csv("data/organized_data/movies_election_periods.csv", usecols=lambda c: c not in ["End_Year"])

#merge tables acc to year, get genre columns
full=movies.merge(elections,left_on="Start_Year",right_on="YEAR")
full = full.drop(columns="Start_Year")
genres=[col for col in full.columns if col not in ['YEAR','PERCENTAGE']]

#finding basic correlation of genres and election percentage
corr=full[genres].corrwith(full['PERCENTAGE'])

#found increase in win percentage tenure by tenure for more fine tuning
percentage_change =full['PERCENTAGE'].diff()
corr_diff=full[genres].corrwith(percentage_change)

#to see correlation between previous tenures win percentage and this tenures movies
full_lag =full[genres].shift(1).corrwith(full['PERCENTAGE'])

result= pd.DataFrame({'genre':genres,'Correlation':corr, 'With change in election win percentage': corr_diff, 'prev. tenure win percent vs curr. tenure movies': full_lag}).round(3)

result =result.sort_values('Correlation', key=abs, ascending=False)
result.to_csv("correlation/correlation_results/correlation_with_elections.csv", index=0)
