import pandas as pd

#simple linear regression with elections (% win rate of party) and movie genres
#reading elections and movies
elections=pd.read_csv("organized_data/elections.csv", usecols=["YEAR","PERCENTAGE"])
movies=pd.read_csv("organized_data/movies_election_periods.csv", usecols=lambda c: c not in ["End_Year"])

#merge tables acc to year, get genre columns
full=movies.merge(elections,left_on="Start_Year",right_on="YEAR")
full = full.drop(columns="Start_Year")
genres=[col for col in full.columns if col not in ['YEAR','PERCENTAGE']]

# movie ratio data belongs to (0,1), elections has numbers in 10s, normalizing election data
full['PERCENTAGE']=full['PERCENTAGE']/50

def fit(x,y,lag):
    # Y' = A + BX' B = slope = summation((x-x')*(y-y'))/(summation(x-x')**2) 
    # x.cov(y) =  summation((x-x')*(y-y'))/n-1, (summation(x-x')**2)/(n-1) = var(x)
    slope = x.cov(y)/x.var()
    # y = mx+c, c=y-mx
    return {f'slope_{lag}': slope, f'intercept_{lag}': y.mean() - slope * x.mean(),f'r_squared_{lag}': x.corr(y) ** 2}

#first, checking same tenure election with same tenures movies
result={}
x=full['PERCENTAGE']
rows_0={g: fit(x,full[g],0) for g in genres}
# getting transpose to put genres as row indicators instead of columns
res_0=pd.DataFrame(rows_0).T

#second, with lag of one tenure (this tenure elections have what affect on next tenure movies?)
x=full['PERCENTAGE'].shift(1)
rows_1={g: fit(x,full[g],1) for g in genres}
res_1=pd.DataFrame(rows_1).T

result = pd.concat([res_0,res_1], axis=1)
result.insert(0,'Genre',genres)

result =result.sort_values('slope_0', key=abs, ascending=False).round(3)
result.to_csv("regression_results/regression_elections_on_genres.csv", index=0)