import pandas as pd
import geopandas as gpd

df2 = gpd.read_file('data/LUCAS_Topsoil_2015_20200323.shp')

df2['GPS_LAT'] = df2['geometry'].y
df2['GPS_LONG'] = df2['geometry'].x
df2 = pd.DataFrame(df2.drop(columns='geometry'))

df2.to_pickle('data/Lucas0_1a.pkl')
