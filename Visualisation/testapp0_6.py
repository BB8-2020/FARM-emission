import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_caching import Cache
import base64
import pandas as pd
import plotly.express as px
from joblib import load
from tensorflow import keras
import numpy as np

df2 = pd.read_pickle('data/Lucas0_4.pkl')
spec = pd.read_pickle('data/spec0_4.pkl')
cnnspec = pd.read_pickle('data/cnnspec0_4.pkl')
knn = load('knn-lucas.joblib')
cnn = keras.models.load_model('cnn_regr_1')

farm_logo = 'logo.56e22df1.png'
farm_logo = base64.b64encode(open(farm_logo, 'rb').read())

cap_logo = 'capgemini-logo.dd5491a8.png'
cap_logo = base64.b64encode(open(cap_logo, 'rb').read())

app = dash.Dash()

cache = Cache(app.server, config={"CACHE_TYPE": "simple"})


def SOC_map(occurances):
    """
    Create a scatter_mapbox with the given values and return it.

    Parameters
    ----------
        occurances (pd.DataFrame): DataFrame containing data that needs to be displayed.

    Returns
    -------
        Scatter_mapbox of given data.

    """
    token = open("token.txt").read()
    fig2 = px.scatter_mapbox(occurances, lat="GPS_LAT", lon="GPS_LONG",
                             color_discrete_sequence=["green"], zoom=2, height=600, size_max=10,
                             color_continuous_scale=px.colors.diverging.RdYlGn, color='OC',
                             range_color=[df2['OC'].min(), df2['OC'].max()], opacity=0.75, hover_name="Point_ID",
                             animation_frame='Year')
    fig2.update_layout(mapbox_style="satellite-streets", mapbox_accesstoken=token)
    fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig2.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'font': {'color': 'black'}
    })
    fig2.update_layout(clickmode='event')
    return fig2


@app.callback(
    [Output('output-range-slider', 'children'),
     Output('SOC-map', 'figure')],

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
    filterset = filter_occurances(value)
    return 'There are {} points in the range {} to {}'.format(len(filterset), value[0], value[1]), SOC_map(filterset)


@app.callback(
    [Output('known-table', 'data'),
     Output('predict-table', 'data')],
    [Input('SOC-map', 'clickData'),
     Input('range-model', 'value')])
def update_columns(clickData, model):
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
        try:
            ID = int(clickData['points'][0]['hovertext'])
        except ValueError:
            ID = clickData['points'][0]['hovertext']
    else:
        ID = None

    data = df2[df2['Point_ID'] == ID].to_dict('records')

    if model == 'KNN':
        pred = range_predict(model, knn, ID, spec)
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
    [Output(component_id='known-table2', component_property='data'),
     Output(component_id='predict-table2', component_property='data'),
     Output('SOC-map2', 'figure')],
    [Input('input-button', 'n_clicks'),
     Input('closest-model', 'value')],
    state=[State(component_id='lon-input', component_property='value'),
           State(component_id='lat-input', component_property='value')]
)
def update_output_div(n_clicks, model, lon, lat):
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
        items = pd.DataFrame({'distance': (abs(df2['GPS_LONG'] - lon) + abs(df2['GPS_LAT'] - lat)),
                              'Point_ID': df2['Point_ID']})
        items.sort_values(by='distance', inplace=True)
        IDs = items['Point_ID'].unique()[:5]
    else:
        IDs = []

    if len(IDs) != 0:
        datafull = df2[df2['Point_ID'].isin(IDs)]
        data = datafull.to_dict('records')
    else:
        datafull = df2
        data = None

    if model == 'KNN':
        pred = closest_predict(model, knn, IDs, spec)
    elif model == 'CNN':
        pred = closest_predict(model, cnn, IDs, cnnspec)
    else:
        pred = None

    return data, pred, SOC_map(datafull)


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


@cache.memoize(10)
def filter_occurances(filter_text):
    """
    Select data that falls within given OC-range.

    Parameters
    ----------
        filter_text (list): list containing the minimum and maximum selected values from range-slider.

    Returns
    -------
        DataFrame containing data withing the minimum and maximum value.

    """
    return df2[(df2['OC'] >= filter_text[0]) & (df2['OC'] <= filter_text[1])]


app.layout = html.Div([
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='In Range', children=[
                html.Div([
                    html.Div(html.H1("SOC in Europa", style={'textAlign': 'center', 'color': 'white'}),
                             style={'backgroundColor': 'rgb(18,171,219)', 'padding': '0.1px'}),
                    html.Div(dcc.Graph(id="SOC-map", config={'displayModeBar': False}),
                             style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                    'backgroundColor': '#E8E8E8'}),
                    html.Div([
                        html.Div([
                            html.Div(id='output-range-slider',
                                     style={'padding': '5px', 'display': 'inline-block', 'height': '18px'}),
                            html.Div(
                                dcc.RangeSlider(
                                    id='range-slider',
                                    min=df2["OC"].min(),
                                    max=df2["OC"].max(),
                                    step=0.5,
                                    value=[df2["OC"].min(), df2["OC"].max()],
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
                                id='known-table',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in df2.columns],
                                editable=False)
                        ], style={'min-height': '130px'}),
                        html.Div([
                            dcc.Markdown("""**Predicted Data**"""),
                            dash_table.DataTable(
                                id='predict-table',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in df2.columns],
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
                    html.Div(dcc.Graph(id="SOC-map2", config={'displayModeBar': False}),
                             style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                    'backgroundColor': '#E8E8E8', 'verticalAlign': 'top'}),
                    html.Div([
                        html.Div([
                            dcc.Input(
                                id="lon-input", type="number", placeholder="Longitude",
                                min=df2['GPS_LONG'].min(), max=df2['GPS_LONG'].max()),
                            dcc.Input(
                                id="lat-input", type="number", placeholder="Latitude",
                                min=df2['GPS_LAT'].min(), max=df2['GPS_LAT'].max()),
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
                            html.Pre(id='click-data2'),
                            dash_table.DataTable(
                                id='known-table2',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in df2.columns],
                                editable=False)
                        ], style={'min-height': '130px'}),
                        html.Div([
                            dcc.Markdown("""**Predicted Data**"""),
                            html.Pre(id='predict-data2'),
                            dash_table.DataTable(
                                id='predict-table2',
                                columns=[{
                                    'name': i,
                                    'id': i
                                } for i in df2.columns],
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

app.run_server(debug=True)
