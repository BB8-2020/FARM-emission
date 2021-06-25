# This file pickles the data of SOC in europe, and hyperspectral data for app.py
import geopandas as gpd
import pandas as pd
import h5py

# Pickling lucas data
lucas2009 = pd.read_excel('data/LUCAS_TOPSOIL_v1.xls')
lucas2015 = gpd.read_file('data/LUCAS_Topsoil_2015_20200323.shp')

lucas2009 = lucas2009.rename(
    columns={'POINT_ID': 'Point_ID', 'coarse': 'Coarse', 'clay': 'Clay', 'silt': 'Silt', 'sand': 'Sand',
             'pH_in_H2O': 'pH_H20', 'pH_in_CaCl2': 'pH_CaCl2'})
lucas2009['Year'] = 2009

lucas2015['GPS_LAT'] = lucas2015['geometry'].y
lucas2015['GPS_LONG'] = lucas2015['geometry'].x
lucas2015 = pd.DataFrame(lucas2015.drop(columns='geometry'))
lucas2015['Year'] = 2015

lucas = lucas2009.append(lucas2015, ignore_index=True, sort=False)
lucas = lucas.sort_values(by='Year')

lucas.to_pickle('data/Lucas.pkl')
print('Pickled Lucas')

# Pickling knn data
knnspec2015 = pd.read_csv('data/spec_Lucas.csv')
knnspec = knnspec2015[knnspec2015.columns[1:]]
knnspec.to_pickle('data/spec.pkl')
print('Pickled spec')

# Pickling cnn data
f = h5py.File('data/labeled_data.hdf5', 'r')
cnn2015 = pd.read_hdf("data/labeled_data.hdf5", key='FR')
countries = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
             'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']
for country in countries:
    tempdf = pd.read_hdf("data/labeled_data.hdf5", key=country)
    cnn2015 = pd.concat((cnn2015, tempdf), ignore_index=True)
cnn2015 = pd.DataFrame(cnn2015.drop(columns=['OC', 'NUTS_0']))
cnn2015.insert(1, 'Year', 2015)
cnn2015.to_pickle('data/cnnspec.pkl')
print('Pickled cnnspec')
