import pandas as pd

# Organizing movies_dataset.csv - 1950 to 2024
movies= pd.read_csv("raw_data/movies_dataset.csv", usecols=['Year','Genre']).sort_values(by="Year")

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
war_movies= pd.read_csv("raw_data/war_themed_movies.csv", usecols=['count'])
war_movies.rename(columns={'count':'War'}, inplace=True)

combined = pd.concat([result,war_movies], axis=1)

combined.to_csv("organized_data/movies.csv", index=0)