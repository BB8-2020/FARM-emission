import geopandas as gpd
import pandas as pd

df1 = pd.read_excel('LUCAS_TOPSOIL_v1.xls')
df2 = gpd.read_file('LUCAS_Topsoil_2015_20200323.shp')

df1 = df1.rename(columns={'POINT_ID': 'Point_ID', 'coarse': 'Coarse', 'clay': 'Clay', 'silt': 'Silt', 'sand': 'Sand',
                          'pH_in_H2O': 'pH_H20', 'pH_in_CaCl2': 'pH_CaCl2'})
df1['Year'] = 2009

df2['GPS_LAT'] = df2['geometry'].y
df2['GPS_LONG'] = df2['geometry'].x
df2 = pd.DataFrame(df2.drop(columns='geometry'))
df2['Year'] = 2015

dfx = df1.append(df2, ignore_index=True, sort=False)
dfx = dfx.sort_values(by='Year')

dfx.to_pickle('Lucas0_3.pkl')

df3 = pd.read_csv('spec_Lucas.csv')
dfy = df3[df3.columns[1:]]
dfy.to_pickle('spec0_3.pkl')
