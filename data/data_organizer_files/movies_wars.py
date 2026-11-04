import pandas as pd

# getting movies made per genre between wars 
# Organizing movies_dataset.csv - 1950 to 2024
movies= pd.read_csv("data/raw_data/movies_dataset.csv", usecols=['Year','Genre']).sort_values(by="Year")

#getting war years
wars = pd.read_csv("data/organized_data/wars.csv",usecols=["Year"])
war_years = sorted(wars["Year"].dropna().astype(int).unique())

# getting periods between consecutive war
periods = list(zip(war_years[:-1], war_years[1:]))

# Picking primary genre for all movies, removing movies with no specified genre
movies['Genre']= movies['Genre'].str.split(',').str[0].str.strip()
movies= movies[movies['Genre']!="-"]

# Picking movies with valid release years [0-9]{4}, picking release years > 1949
movies= movies[movies['Year'].str.fullmatch(r'\d{4}', na=False)]
movies = movies[movies['Year']>'1949']

# adding the genres as columns, movies.csv now has no. of movies released in an genre each year
result= pd.crosstab(movies['Year'], movies['Genre']).reset_index()

# removed unpopular genres, genres with very few movies released every years
result=result.drop(columns=["Adventure","Animation","News","Reality-TV","Short","Talk-Show","War","Music","Musical","Sport","Sci-Fi","Fantasy"])

# combined some similar genres into one
result['Crime'] = result['Crime'] + result['Thriller']
result = result.drop(columns='Thriller')

result['Horror'] = result['Horror'] + result['Mystery']
result = result.drop(columns='Mystery')

result['Drama'] = result['Drama'] + result['Family']
result = result.drop(columns='Family')

result['Documentary'] = result['Documentary'] + result['Biography']+result['History']
result = result.drop(columns=['Biography','History'])
result.rename(columns={'Documentary':'Non-fiction'}, inplace=True)

# append war_movies to movies.csv
war_movies= pd.read_csv("data/raw_data/war_themed_movies.csv", usecols=['count'])
war_movies.rename(columns={'count':'War'}, inplace=True)

and_wars = pd.concat([result,war_movies], axis=1)

yearly = and_wars.set_index("Year")
yearly.index = yearly.index.astype(int)
results = []
for start, end in periods:
     period_counts = yearly.loc[(yearly.index>=start)&(yearly.index < end)].sum()
  
     row = period_counts.to_dict()
     row["Start_Year"] = start
     row["End_Year"] = end
     results.append(row)

combined=pd.DataFrame(results)
combined = combined[["Start_Year", "End_Year"] + [col for col in combined.columns if col not in ["Start_Year", "End_Year"]]]
genres=combined.columns.drop(["Start_Year", "End_Year"])

combined[genres] = combined[genres].div(combined[genres].sum(axis=1), axis=0).round(4)
# removing 2023, 2024 to align with the elections dataset
combined=combined[combined["End_Year"] <= 2022]
combined=combined[combined["Start_Year"] >= 1948]

combined.to_csv("data/organized_data/war_wise_movies.csv", index=0)