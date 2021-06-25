import pandas as pd

df = pd.read_pickle('data/Lucas0_1.pkl')
print(df)
lon = 6.514
lat = 52.748
items = (abs(df['GPS_LONG'] - lon) + abs(df['GPS_LAT'] - lat))
itemmin = min(items)
items.sort_values(inplace=True)
head = items.head()
headmin = head.index
print(head)
print((items == itemmin).sum())
index = items.idxmin()
print(index)
newdata = df.loc[headmin, :]
newitems = (abs(newdata['GPS_LONG'] - lon) + abs(newdata['GPS_LAT'] - lat))
print(df.loc[headmin, :])
print(newitems)

print(df.loc[index, :])
