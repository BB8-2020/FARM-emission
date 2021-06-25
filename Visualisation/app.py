# This file visualises data of SOC in europe, and predicts values from hyperspectral data
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import pandas as pd
import plotly.express as px
from joblib import load
from tensorflow import keras
import numpy as np

# Load in datasets and models
lucas = pd.read_pickle('data/Lucas.pkl')
knnspec = pd.read_pickle('data/spec.pkl')
cnnspec = pd.read_pickle('data/cnnspec.pkl')
knn = load('knn-lucas.joblib')
cnn = keras.models.load_model('cnn_regr_1')

# Load in pictures for webpage
farm_logo = 'logo.56e22df1.png'
farm_logo = base64.b64encode(open(farm_logo, 'rb').read())
cap_logo = 'capgemini-logo.dd5491a8.png'
cap_logo = base64.b64encode(open(cap_logo, 'rb').read())

# Initialise the app
app = dash.Dash()


def SOC_map(data):
    """
    Create a scatter_mapbox with the given values and return it.

    Parameters
    ----------
        occurances (pd.DataFrame): DataFrame containing data that needs to be displayed.

    Returns
    -------
        Scatter_mapbox of given data.

    """
    # Load mapbox token to get certain map-styles
    token = open("token.txt").read()
    fig = px.scatter_mapbox(data, lat="GPS_LAT", lon="GPS_LONG",
                            color_discrete_sequence=["green"], zoom=2, height=600, size_max=10,
                            color_continuous_scale=px.colors.diverging.RdYlGn, color='OC',
                            range_color=[lucas['OC'].min(), lucas['OC'].max()], opacity=0.75, hover_name="Point_ID",
                            animation_frame='Year')
    # Change the map style, margin and colors of the map
    fig.update_layout(mapbox_style="satellite-streets", mapbox_accesstoken=token)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'font': {'color': 'black'}
    })
    fig.update_layout(clickmode='event')
    return fig


@app.callback(
    [Output('range-slider_info', 'children'),
     Output('range-map', 'figure')],

    [Input('range-slider', 'value')])
def update_output(value):
    """
    Update the scatter_mapbox and the text on the range page based on the range-slider.

    Parameters
    ----------
        value (list): list containing the minimum and maximum selected values from range-slider.

    Returns
    -------
        Text line with info about the data and a scatter_mapbox with values within the given range.

    """
    data = lucas[(lucas['OC'] >= value[0]) & (lucas['OC'] <= value[1])]
    return 'There are {} points in the range {} to {}'.format(len(data), value[0], value[1]), SOC_map(data)


@app.callback(
    [Output('range-known', 'data'),
     Output('range-predict', 'data')],
    [Input('range-map', 'clickData'),
     Input('range-model', 'value')])
def update_range(clickData, model):
    """
    Display data of clicked point in DataFrame and predicted data on Data-Tables.

    Parameters
    ----------
        clickData (dict): Dictionary containing all map-data of selected point.
        model (str): String defining which model is to be used.

    Returns
    -------
        Data to be put into Data-Table's.

    """
    if clickData is not None:
        # Turn ID into integer if possible
        try:
            ID = int(clickData['points'][0]['hovertext'])
        except ValueError:
            ID = clickData['points'][0]['hovertext']
    else:
        ID = None

    data = lucas[lucas['Point_ID'] == ID].to_dict('records')

    # Based on model, different predictions are given
    if model == 'KNN':
        pred = range_predict(model, knn, ID, knnspec)
    elif model == 'CNN':
        pred = range_predict(model, cnn, ID, cnnspec)
    else:
        pred = None

    return data, pred


def range_predict(model_name, model, ID, data):
    """
    Predict for given data with given model.

    Parameters
    ----------
        model_name (str): String defining which model is to be used.
        model (obj): Model that is used to predict.
        ID (str, int): ID of points to predict.
        data(pd.DataFrame): Spectral data for model.

    Returns
    -------
        Prediction from model.

    """
    if model_name == 'KNN':
        specs = data[data['Point_ID'] == ID].copy()
        if len(specs.index) != 0:
            ocs = model.predict(specs[specs.columns[2:]].values)
            specs['OC'] = ocs
            pred = specs.to_dict('records')
        else:
            pred = None
    elif model_name == 'CNN':
        specs = data[data['Point_ID'] == ID].copy()
        if len(specs.index) != 0:
            ocs = model.predict(np.array(list(specs['spectogram'].values)))
            specs['OC'] = ocs
            pred = specs.to_dict('records')
        else:
            pred = None
    else:
        pred = None

    return pred


@app.callback(
    [Output(component_id='closest-known', component_property='data'),
     Output(component_id='closest-predict', component_property='data'),
     Output('closest-map', 'figure')],
    [Input('input-button', 'n_clicks'),
     Input('closest-model', 'value')],
    state=[State(component_id='lon-input', component_property='value'),
           State(component_id='lat-input', component_property='value')]
)
def update_closest(n_clicks, model, lon, lat):
    """
    Update the scatter_mapbox and both Data-Table's on the closest page based on the input fields.

    Parameters
    ----------
        n_clicks (int): Integer of how many times the input button has been pressed.
        lon (float): Given Longitude value.
        lat (float): Given Latitude value.

    Returns
    -------
        Data of the 5 closest Points_ID's to given coordinates, predicted values for these points,
        and a Scatter-mapbox visualising these points.

    """
    if lon is not None and lat is not None:
        # Calculates the distance for each item in dataframe and selects the 5 closest unique Point_ID's
        items = pd.DataFrame({'distance': (abs(lucas['GPS_LONG'] - lon) + abs(lucas['GPS_LAT'] - lat)),
                              'Point_ID': lucas['Point_ID']})
        items.sort_values(by='distance', inplace=True)
        IDs = items['Point_ID'].unique()[:5]
    else:
        IDs = []

    if len(IDs) != 0:
        fulldata = lucas[lucas['Point_ID'].isin(IDs)]
        data = fulldata.to_dict('records')
    else:
        fulldata = lucas
        data = None

    # Based on model, different predictions are given
    if model == 'KNN':
        pred = closest_predict(model, knn, IDs, knnspec)
    elif model == 'CNN':
        pred = closest_predict(model, cnn, IDs, cnnspec)
    else:
        pred = None

    return data, pred, SOC_map(fulldata)


def closest_predict(model_name, model, IDs, data):
    """
    Predict for given data with given model.

    Parameters
    ----------
        model_name (str): String defining which model is to be used.
        model (obj): Model that is used to predict.
        IDs (list): IDs of points to predict.
        data(pd.DataFrame): Spectral data for model.

    Returns
    -------
        Prediction from model.

    """
    if model_name == 'KNN':
        specs = data[data['Point_ID'].isin(IDs)].copy()
        if len(specs.index) != 0:
            ocs = model.predict(specs[specs.columns[2:]].values)
            specs['OC'] = ocs
            pred = specs.to_dict('records')
        else:
            pred = None
    elif model_name == 'CNN':
        specs = data[data['Point_ID'].isin(IDs)].copy()
        if len(specs.index) != 0:
            ocs = model.predict(np.array(list(specs['spectogram'].values)))
            specs['OC'] = ocs
            pred = specs.to_dict('records')
        else:
            pred = None
    else:
        pred = None

    return pred


# Defining the layout of the app
app.layout = html.Div([
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='In Range', children=[
                html.Div([
                    html.Div(html.H1("SOC in Europa", style={'textAlign': 'center', 'color': 'white'}),
                             style={'backgroundColor': 'rgb(18,171,219)', 'padding': '0.1px'}),
                    html.Div(dcc.Graph(id="range-map", config={'displayModeBar': False}),
                             style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                    'backgroundColor': '#E8E8E8'}),
                    html.Div([
                        html.Div([
                            html.Div(id='range-slider_info',
                                     style={'padding': '5px', 'display': 'inline-block', 'height': '18px'}),
                            html.Div(
                                dcc.RangeSlider(
                                    id='range-slider',
                                    min=lucas["OC"].min(),
                                    max=lucas["OC"].max(),
                                    step=0.5,
                                    value=[lucas["OC"].min(), lucas["OC"].max()],
                                    allowCross=False,
                                    pushable=0.5,
                                    tooltip={
                                        'always_visible': True,
                                        'placement': 'bottom'
                                    }))
                        ], style={'height': '70px'}),
                        html.Div([
                            dcc.Markdown("""**Current model: **"""),
                            dcc.Dropdown(
                                id='range-model',
                                options=[
                                    {'label': 'KNN', 'value': 'KNN'},
                                    {'label': 'CNN', 'value': 'CNN'}
                                ],
                                value='KNN',
                                searchable=False,
                                clearable=False,
                                style={
                                    'width': '150px'
                                }
                            )
                        ]),
                        html.Div([
                            dcc.Markdown("""**Known Data**"""),
                            dash_table.DataTable(
                                id='range-known',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in lucas.columns],
                                editable=False)
                        ], style={'min-height': '130px'}),
                        html.Div([
                            dcc.Markdown("""**Predicted Data**"""),
                            dash_table.DataTable(
                                id='range-predict',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in lucas.columns],
                                editable=False)
                        ], style={'min-height': '130px'})
                    ], style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                              'backgroundColor': '#E0E0E0', 'verticalAlign': 'top', 'textAlign': 'left'})
                ], style={'textAlign': 'center'})
            ], style={'backgroundColor': '#F0F0F0', 'border': '1px solid #C0C0C0'},
                selected_style={'backgroundColor': '#C0C0C0', 'border': '1px solid #F0F0F0'}),
            dcc.Tab(label='Closest', children=[
                html.Div([
                    html.Div(html.H1("SOC in Europa", style={'textAlign': 'center', 'color': 'white'}),
                             style={'backgroundColor': 'rgb(18,171,219)', 'padding': '0.1px'}),
                    html.Div(dcc.Graph(id="closest-map", config={'displayModeBar': False}),
                             style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                    'backgroundColor': '#E8E8E8', 'verticalAlign': 'top'}),
                    html.Div([
                        html.Div([
                            dcc.Input(
                                id="lon-input", type="number", placeholder="Longitude",
                                min=lucas['GPS_LONG'].min(), max=lucas['GPS_LONG'].max()),
                            dcc.Input(
                                id="lat-input", type="number", placeholder="Latitude",
                                min=lucas['GPS_LAT'].min(), max=lucas['GPS_LAT'].max()),
                            html.Button('Get Data', id='input-button')
                        ]),
                        html.Div([
                            dcc.Markdown("""**Current model: **"""),
                            dcc.Dropdown(
                                id='closest-model',
                                options=[
                                    {'label': 'KNN', 'value': 'KNN'},
                                    {'label': 'CNN', 'value': 'CNN'}
                                ],
                                value='KNN',
                                searchable=False,
                                clearable=False,
                                style={
                                    'width': '150px'
                                }
                            )
                        ]),
                        html.Div([
                            dcc.Markdown("""**Known Data**"""),
                            dash_table.DataTable(
                                id='closest-known',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in lucas.columns],
                                editable=False)
                        ], style={'min-height': '130px'}),
                        html.Div([
                            dcc.Markdown("""**Predicted Data**"""),
                            dash_table.DataTable(
                                id='closest-predict',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in lucas.columns],
                                editable=False)
                        ], style={'min-height': '130px'})
                    ], style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                              'backgroundColor': '#E0E0E0', 'verticalAlign': 'top', 'textAlign': 'left'})
                ], style={'textAlign': 'center'})
            ], style={'backgroundColor': '#F0F0F0', 'border': '1px solid #C0C0C0'},
                selected_style={'backgroundColor': '#C0C0C0', 'border': '1px solid #F0F0F0'})

        ])
    ], style={'padding': '10px 10px 55px 10px', 'backgroundColor': 'lightgrey'}),
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(farm_logo.decode()),
                 style={'padding': '11px', 'width': '68px', 'display': 'inline-block', 'float': 'left'}),
        html.Img(src='data:image/png;base64,{}'.format(cap_logo.decode()),
                 style={'padding': '10px', 'width': '135px', 'display': 'inline-block', 'float': 'right'})
    ], style={'height': '50px', 'width': '100vw', 'position': 'fixed', 'bottom': '0', 'backgroundColor': 'white'})
], style={'height': '100vh', 'width': '100vw', 'font-family': 'Calibri'})

# Running the file
if __name__ == '__main__':
    app.run_server(debug=False, port=8080, host='0.0.0.0')
