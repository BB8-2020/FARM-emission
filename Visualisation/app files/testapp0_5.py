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

df2 = pd.read_pickle('Lucas0_3.pkl')
spec = pd.read_pickle('spec0_3.pkl')
knn = load('knn-lucas.joblib')

farm_logo = 'logo.56e22df1.png'
farm_logo = base64.b64encode(open(farm_logo, 'rb').read())

cap_logo = 'capgemini-logo.dd5491a8.png'
cap_logo = base64.b64encode(open(cap_logo, 'rb').read())

app = dash.Dash()

cache = Cache(app.server, config={"CACHE_TYPE": "simple"})


def SOC_map(occurances):
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
    filterset = filter_occurances(value)
    return 'There are {} points in the range {} to {}'.format(len(filterset), value[0], value[1]), SOC_map(filterset)


@app.callback(
    [Output('known-table', 'data'),
     Output('predict-table', 'data')],
    Input('SOC-map', 'clickData'))
def update_columns(clickData):
    try:
        ID = clickData['points'][0]['hovertext']
    except:
        ID = None

    data = df2[df2['Point_ID'] == ID].to_dict('records')

    try:
        specs = spec[spec['Point_ID'] == ID]
        ocs = knn.predict(specs[specs.columns[2:]].values)
        specs['OC'] = ocs
        pred = specs.to_dict('records')
    except:
        pred = spec[spec['Point_ID'] == ID].to_dict('records')

    return data, pred


@app.callback(
    [Output(component_id='known-table2', component_property='data'),
     Output(component_id='predict-table2', component_property='data'),
     Output('SOC-map2', 'figure')],
    [Input('input-button', 'n_clicks')],
    state=[State(component_id='lon-input', component_property='value'),
           State(component_id='lat-input', component_property='value')]
)
def update_output_div(n_clicks, lon, lat):
    try:
        items = pd.DataFrame({'distance': (abs(df2['GPS_LONG'] - lon) + abs(df2['GPS_LAT'] - lat)),
                              'Point_ID': df2['Point_ID']})
        items.sort_values(by='distance', inplace=True)
        IDs = items['Point_ID'].unique()[:5]
    except:
        IDs = None

    try:
        datafull = df2[df2['Point_ID'].isin(IDs)]
        data = datafull.to_dict('records')
    except:
        datafull = df2
        data = None

    try:
        specs = spec[spec['Point_ID'].isin(IDs)]
        ocs = knn.predict(specs[specs.columns[2:]].values)
        specs['OC'] = ocs
        pred = specs.to_dict('records')
    except:
        pred = None

    return data, pred, SOC_map(datafull)


@cache.memoize(10)
def filter_occurances(filter_text):
    return df2[(df2['OC'] >= filter_text[0]) & (df2['OC'] <= filter_text[1])]


app.layout = html.Div([
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='In Range', children=[
                html.Div(html.H1("SOC in Europa", style={'textAlign': 'center'}),
                         style={'backgroundColor': 'green', 'padding': '0.1px'}),
                html.Div(dcc.Graph(id="SOC-map", config={'displayModeBar': False}),
                         style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                'backgroundColor': '#6CC4A6'}),
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
                          'backgroundColor': '#6CC4A6', 'verticalAlign': 'top'})
            ], style={'backgroundColor': '#6CC4A6', 'border': '1px solid #348C6E'},
                    selected_style={'backgroundColor': '#348C6E', 'border': '1px solid #6CC4A6'}),
            dcc.Tab(label='Closest', children=[
                html.Div(html.H1("SOC in Europa", style={'textAlign': 'center'}),
                         style={'backgroundColor': '#E8E8E8', 'padding': '0.1px'}),
                html.Div(dcc.Graph(id="SOC-map2", config={'displayModeBar': False}),
                         style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                                'backgroundColor': '#F0F0F0'}),
                html.Div([
                    html.Div([
                        dcc.Input(
                            id="lon-input", type="number", placeholder="Longetude",
                            min=df2['GPS_LONG'].min(), max=df2['GPS_LONG'].max()),
                        dcc.Input(
                            id="lat-input", type="number", placeholder="Lattetude",
                            min=df2['GPS_LAT'].min(), max=df2['GPS_LAT'].max()),
                        html.Button('Get Data', id='input-button')
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
                          'backgroundColor': '#6CC4A6', 'verticalAlign': 'top'})
            ], style={'backgroundColor': '#6CC4A6', 'border': '1px solid #348C6E'},
                    selected_style={'backgroundColor': '#348C6E', 'border': '1px solid #6CC4A6'})
        ])
    ], style={'padding': '10px 10px 55px 10px', 'backgroundColor': 'lightgrey'}),
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(farm_logo.decode()),
                 style={'padding': '11px', 'width': '68px', 'display': 'inline-block', 'float': 'left'}),
        html.Img(src='data:image/png;base64,{}'.format(cap_logo.decode()),
                 style={'padding': '10px', 'width': '135px', 'display': 'inline-block', 'float': 'right'})
    ], style={'height': '50px', 'width': '100vw', 'position': 'fixed', 'bottom': '0', 'backgroundColor': 'white'})
], style={'height': '100vh', 'width': '100vw'})

app.run_server(debug=True)
