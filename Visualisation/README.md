# Visualisation Project-Farm
> Prep SOC data and visualize SOC data in an interactive dashboard
## Usage Command

OS X & Linux:

```sh
python <filename.py>
```

Windows:

```sh
python <filename.py>
```

## Usage example
To use it:
- Download the entire code as ZIP or clone it
- Download data and model from https://www.dropbox.com/sh/uw96s25ayrid56u/AAATGV6mbZXQqQcmIZ_04S52a?dl=0
- Run the pickler file for the test- or app-file you want to run (If the pickles are not available)
- Run the test- or app-file you want to run
  
This will give you either an output, or a link to the visualisation-page, which you will need to put into your browser  

This folder currently contains data, but this data can be swapped if the new data has the same structure

## Library Install

OS X & Linux:
```sh
pip3 install dash
pip3 install dash_table
pip3 install dash_core_components
pip3 install dash_html_components
pip3 install flask
pip3 install numpy
pip3 install pandas
pip3 install geopandas
pip3 install plotly
pip3 install joblib
pip3 install tensorflow
```

Windows:
```sh
pip install dash
pip install dash_table
pip install dash_core_components
pip install dash_html_components
pip install flask
pip install numpy
pip install pandas
pip install geopandas
pip install plotly
pip install joblib
pip install tensorflow
```

Geopandas sometimes needs to download a geodatabase to run properly

## Requirements GUI
- Input satellitedata, output 'soil organic carbon'
- Visualize data on map
- All data of points on map able to be visualised in table
- Multiple models that can be switched

## Manual (app.py)
Manual for the pages In Range and Closest
### In Range
When opening this page you are shown a map, a slider, two tables and a dropdown-menu.

The slider allows the user to change de OC data that is visualised on the map, doing so with a minimum and maximum.

The map is a interactive map that sends data to the two tables when a point on the map is clicked.
The map can also switch between the year that is shown.

The two tables contain the data that is known of the selected point, and the data that is real-time predicted by the 
current model.

The dropdown-menu allows the user to change the current model that is used to predict the data.

### Closest
When opening this page you are shown a map, two input-fields, a button, two tables and a dropdown-menu.

The input fields and button are used to determine the point you want the closest data of. The inputs are for the 
longitude and latitude, and the button to confirm the point.

The two tables contain the data that is known of the 5 closest points, and the data that is real-time predicted by the 
current model.

The map is a interactive map that visualises the known data of the closest points.
The map can also switch between the year that is shown.

The dropdown-menu allows the user to change the current model that is used to predict the data.

## Docker
A version of the app that doesn't contain CNN is avalable on Docker.
To run it you need to install docker and then run the following commands:
```sh
docker pull dragonkiller952/farm-emission:gui
docker run -p 8080:8080 dragonkiller952/farm-emission:gui
```

## Code Explaination
There are 3 types of python files: tests, picklers and apps
### Tests
#### min_dist_tester.py
- Tester for gathering 5 closest indexes to given longitude and latitude
#### submit_test.py
- Tester for input fields and buttons in app

### Picklers
(Picklers are used for certain test- or app-files)
#### pickler0_1.py
- Reads 2009 lucas data from .xls into DataFrame
- Pickles DataFrame
#### pickler0_1a.py
- Reads 2015 lucas data from .shp into DataFrame
- Cleans data
- Pickles DataFrame
#### pickler0_2.py
Does the same things as 0_1 and 0_1a, only combines them both into 1 DataFrame
#### pickler0_2a.py
- Reads Kenya data from .csv into DataFrame
- Decreases size of DataFrame
- Creates DataFrame from data within .shp file of Kenya
- Pickles DataFrame
#### pickler0_3.py
Does the same thing as 0_2, only added:
- Reads KNN spectral data from .csv into DataFrame
- Pickles DataFrame
#### pickler0_4.py
Does the same thing as 0_3, only added:
- Reads CNN spectograms from .hdf5 into DataFrame
- Pickles DataFrame
#### pickler.py (Final version)
Does the same thing as 0_4, only with changed variable names, and documentation

### Apps
#### testapp0_1.py
- Creates scatter_mapbox with data from lucas pickle
- Creates scatter_plot with data from lucas pickle
#### testapp0_2.py
- Creates scatter_mapbox with data from lucas pickle
- Uses range-slider to affect data visible in mapbox
- Uses click-events to show data of point in data-table
- Uses experimental page layout
#### testapp0_3a.py
Does the same thing as 0_2, only added:
- Uses second page
- Uses input fields and button to select data from 5 closest indexes, and displays it in data-table
- Uses 1st version of page layout
#### testapp0_3b.py
Does the same thing as 0_3a, only uses different data
#### testapp0_4.py
Does the same things as 0_3a and 0_3b, only added:
- Uses data of multiple years
- Has year slider on mapbox to switch visual data
#### testapp0_4a.py
Does the same things as 0_3a and 0_3b, only uses data from kenya
#### testapp0_5.py
Does the same thing as 0_4, only added:
- Now uses 5 closet unique Point_ID instead of index
- Uses spectral data for KNN
- Uses KNN model to live-predict data for same Point_ID's as in other data-table
- Displays predicted data in new data-table on respective page
- Uses final version of page layout
#### testapp0_6.py
Does the same thing as 0_5, only added:
- Uses spectrogram data for CNN
- Uses CNN model to live-predict data for same Point_ID's as in other data-table
- Uses dropdown to choose between prediction models
#### app.py (Final version)
Does the same thing as 0_6, only without internal cashe, with changed variable names, and with documentation