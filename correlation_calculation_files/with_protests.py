import pandas as pd

#finding correlation of protests and movie genres
#reading protests and movies
protests=pd.read_csv("organized_data/protests.csv")
movies=pd.read_csv("organized_data/movies_ratio.csv")

#merge tables acc to year, get genre columns
full=movies.merge(protests,on='Year')
genres=[col for col in movies.columns if col!='Year']

#finding basic correlation of genres and protests
corr=full[genres].corrwith(full['Protests'])

#found increase in protests year by year for more fine tuning
protest_change =full['Protests'].diff()
corr_diff=full[genres].corrwith(protest_change)

#to see correlation between previous years protests and this years movies
full_lag =full[genres].shift(1).corrwith(full['Protests'])

result= pd.DataFrame({'genre':genres,'Correlation':corr, 'With change in protests': corr_diff, 'prev. year protests vs curr. year movies': full_lag}).round(3)

result =result.sort_values('Correlation', key=abs, ascending=False)
result.to_csv("correlation_results/correlation_with_protests.csv", index=0)