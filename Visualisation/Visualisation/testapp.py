import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_caching import Cache

import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go

df2 = pd.read_pickle('Lucas.pkl')

app = dash.Dash()
cache = Cache(app.server, config={"CACHE_TYPE": "simple"})


def SOC_map(occurances):
    token = open("token.txt").read() # you will need your own token
    fig2 = px.scatter_mapbox(occurances, lat="GPS_LAT", lon="GPS_LONG",
                            color_discrete_sequence=["green"], zoom=2, height=500, size_max=10,
                            color_continuous_scale=px.colors.diverging.RdYlGn, color='OC',
                            range_color=[df2['OC'].min(), df2['OC'].max()], opacity=0.75, hover_name="POINT_ID")
    fig2.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
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
    Output('editing-columns', 'data'),
    Input('SOC-map', 'clickData'))
def update_columns(clickData):
    try:
        ID = clickData['points'][0]['hovertext']
        data = df2[df2['POINT_ID'] == ID].to_dict('records')
    except:
        ID = None
        data =df2[df2['POINT_ID'] == ID].to_dict('records')
    return data

@cache.memoize(10)
# def filter_sightings(filter_text):
#     return df2[df2["OC"].astype(str).str.contains(filter_text, na=False)]
def filter_occurances(filter_text):
    return df2[(df2['OC'] >= filter_text[0]) & (df2['OC'] <= filter_text[1])]


app.layout = html.Div([
    html.Div(html.H1("SOC in Europa"), style={'backgroundColor': 'green'}),
    html.Div(dcc.Graph(id="SOC-map"), style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        html.Div(id='output-range-slider', style={'padding': '5px', 'display': 'inline-block'}),
        html.Div(
            dcc.RangeSlider(
                id='range-slider',
                min=df2["OC"].min(),
                max=df2["OC"].max(),
                step=0.5,
                value=[df2["OC"].min(), df2["OC"].max()],
                allowCross=False,
                pushable= 0.5,
                tooltip={
                    'always_visible': True,
                    'placement': 'bottom'
                })),
        html.Div([
            dcc.Markdown("""**Selected Point**"""),
            html.Pre(id='click-data'),
            dash_table.DataTable(
                id='editing-columns',
                columns=[{
                    'name': i,
                    'id': i
                } for i in df2.columns],
                editable=False)
        ])

    ], style={'width': '49%', 'display': 'inline-block', 'backgroundColor': 'red', 'vertical-align': 'top'}),
], style={'backgroundColor': 'orange'})

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter