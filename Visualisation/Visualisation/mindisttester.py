import pandas as pd

df = pd.read_pickle('Dash/Lucas.pkl')

lon = 50.1
lat = 50.1
items = (abs(df['GPS_LONG'] - lon)+abs(df['GPS_LAT'] - lat))
itemmin = min(items)
items.sort_values(inplace=True)
head = items.head()
headmin = head.index
print(head)
print((items == itemmin).sum())
index = items.idxmin()
print(index)
print(df.iloc[headmin,:])


print(df.loc[ index , : ])