import geopandas as gpd
import pandas as pd
import h5py

df1 = pd.read_excel('data/LUCAS_TOPSOIL_v1.xls')
df2 = gpd.read_file('data/LUCAS_Topsoil_2015_20200323.shp')

df1 = df1.rename(columns={'POINT_ID': 'Point_ID', 'coarse': 'Coarse', 'clay': 'Clay', 'silt': 'Silt', 'sand': 'Sand',
                          'pH_in_H2O': 'pH_H20', 'pH_in_CaCl2': 'pH_CaCl2'})
df1['Year'] = 2009

df2['GPS_LAT'] = df2['geometry'].y
df2['GPS_LONG'] = df2['geometry'].x
df2 = pd.DataFrame(df2.drop(columns='geometry'))
df2['Year'] = 2015

dfx = df1.append(df2, ignore_index=True, sort=False)
dfx = dfx.sort_values(by='Year')

dfx.to_pickle('data/Lucas0_4.pkl')
print('Pickled Lucas')

df3 = pd.read_csv('data/spec_Lucas.csv')
dfy = df3[df3.columns[1:]]
dfy.to_pickle('data/spec0_4.pkl')
print('Pickled spec')

f = h5py.File('data/labeled_data.hdf5', 'r')
reread = pd.read_hdf("data/labeled_data.hdf5", key='FR')
countries = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
             'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']
for country in countries:
    temppd = pd.read_hdf("data/labeled_data.hdf5", key=country)
    reread = pd.concat((reread, temppd), ignore_index=True)
reread = pd.DataFrame(reread.drop(columns=['OC', 'NUTS_0']))
reread.insert(1, 'Year', 2015)
reread.to_pickle('data/cnnspec0_4.pkl')
print('Pickled cnnspec')
