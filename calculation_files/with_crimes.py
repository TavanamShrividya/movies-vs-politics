import pandas as pd

#finding correlation of crimes and movie genres
#reading crimes and movies
crimes=pd.read_csv("organized_data/crimes.csv")
movies=pd.read_csv("organized_data/movies_ratio.csv")

#merge tables acc to year, get genre columns
full=movies.merge(crimes,on='Year')
genres=[col for col in movies.columns if col!='Year']

#finding basic correlation of genres and crimes
corr=full[genres].corrwith(full['Crimes'])

#found increase in crimes year by year for more fine tuning
crime_change =full['Crimes'].diff()
corr_diff=full[genres].corrwith(crime_change)

#to see correlation between previous years crimes and this years movies
full_lag =full[genres].shift(1).corrwith(full['Crimes'])

result = pd.DataFrame({'genre':genres,'Correlation':corr, 'With change in crimes': corr_diff, 'prev. year crimes vs curr. year movies': full_lag}).round(3)

result.to_csv("results/correlation_with_crimes.csv", index=0)
