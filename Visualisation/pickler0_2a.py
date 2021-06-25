import geopandas as gpd
import pandas as pd

df2 = pd.read_csv('data/kenya.csv')
df2 = df2.rename(columns={'value': 'OC', 'x': 'GPS_LONG', 'y': 'GPS_LAT'})
df2 = df2[df2['GPS_LONG'] < 41.9]
df2 = df2[df2['GPS_LONG'] > 33.7]
df2 = df2[df2['GPS_LAT'] < 4.7]
df2 = df2[df2['GPS_LAT'] > -4.7]
df2['Point_ID'] = range(0, len(df2))
for i in range(8):
    df2 = df2[df2['Point_ID'] % 2 != 0]
    df2['Point_ID'] = range(0, len(df2))
gdf = gpd.GeoDataFrame(
    df2, geometry=gpd.points_from_xy(df2.GPS_LONG, df2.GPS_LAT))
gdf2 = gpd.read_file('data/ken_admbnda_adm0_iebc_20191031.shp')
kenya = gdf2.geometry.unary_union
kenya_data = gdf[gdf.geometry.within(kenya)]
df2 = pd.DataFrame(kenya_data.drop(columns='geometry'))

df2.to_pickle('data/kenya0_2a.pkl')
