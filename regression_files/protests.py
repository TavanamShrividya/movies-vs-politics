import pandas as pd

#simple linear regression with protests and movie genres
#reading protests and movies
protests=pd.read_csv("organized_data/protests.csv")
movies=pd.read_csv("organized_data/movies_ratio.csv")

#merge tables acc to year, get genre columns
full=movies.merge(protests,on='Year')
genres=[col for col in movies.columns if col!='Year']

# movie ratio data belongs to (0,1), protests has numbers in 10s, normalizing protest data
full['Protests']=full['Protests']/10

def fit(x,y,lag):
    # Y' = A + BX' B = slope = summation((x-x')*(y-y'))/(summation(x-x')**2) 
    # x.cov(y) =  summation((x-x')*(y-y'))/n-1, (summation(x-x')**2)/(n-1) = var(x)
    slope = x.cov(y)/x.var()
    # y = mx+c, c=y-mx
    return {f'slope_{lag}': slope, f'intercept_{lag}': y.mean() - slope * x.mean(),f'r_squared_{lag}': x.corr(y) ** 2}

#first, checking same years protestss with same years movies
result={}
x=full['Protests']
rows_0={g: fit(x,full[g],0) for g in genres}
# getting transpose to put genres as row indicators instead of columns
res_0=pd.DataFrame(rows_0).T

#second, with lag of one year (this years protests have what affect on next years movies?)
x=full['Protests'].shift(1)
rows_1={g: fit(x,full[g],1) for g in genres}
res_1=pd.DataFrame(rows_1).T

result = pd.concat([res_0,res_1], axis=1)
result.insert(0,'Genre',genres)

result =result.sort_values('slope_0', key=abs, ascending=False).round(3)
result.to_csv("regression_results/regression_protests_on_genres.csv", index=0)