import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_caching import Cache

import pandas as pd
import plotly.express as px

df2 = pd.read_pickle('Lucas0_2.pkl')

app = dash.Dash()

cache = Cache(app.server, config={"CACHE_TYPE": "simple"})


def SOC_map(occurances):
    token = open("token.txt").read()
    fig2 = px.scatter_mapbox(occurances, lat="GPS_LAT", lon="GPS_LONG",
                             color_discrete_sequence=["green"], zoom=2, height=600, size_max=10,
                             color_continuous_scale=px.colors.diverging.RdYlGn, color='OC',
                             range_color=[df2['OC'].min(), df2['OC'].max()], opacity=0.75, hover_name="Point_ID",
                             animation_frame='Year')
    fig2.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
    fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig2.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'font': {'color': '#f2f5fa'}
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
    Output('editing-columns', 'data'),
    Input('SOC-map', 'clickData'))
def update_columns(clickData):
    try:
        ID = clickData['points'][0]['hovertext']
        data = df2[df2['Point_ID'] == ID].to_dict('records')
    except:
        ID = None
        data = df2[df2['Point_ID'] == ID].to_dict('records')
    return data


@app.callback(
    [Output(component_id='inputtab', component_property='data'),
     Output('SOC-map2', 'figure')],
    [Input('button', 'n_clicks')],
    state=[State(component_id='my-id', component_property='value'),
           State(component_id='my-id2', component_property='value')]
)
def update_output_div(n_clicks, input_value1, input_value2):
    try:
        items = (abs(df2['GPS_LONG'] - input_value1) + abs(df2['GPS_LAT'] - input_value2))
        items.sort_values(inplace=True)
        head = items.head()
        headmin = head.index
        datafull = df2.loc[headmin, :]
        data = datafull.to_dict('records')
    except:
        datafull = df2
        data = None
    return data, SOC_map(datafull)


@cache.memoize(10)
def filter_occurances(filter_text):
    return df2[(df2['OC'] >= filter_text[0]) & (df2['OC'] <= filter_text[1])]


app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='In Range', children=[
            html.Div(html.H1("SOC in Europa", style={'text-align': 'center'}), style={'backgroundColor': 'green'}),
            html.Div(dcc.Graph(id="SOC-map", config={'displayModeBar': False}),
                     style={'padding': '5px', 'width': '49%', 'display': 'inline-block', 'backgroundColor': '#6CC4A6'}),
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
                        pushable=0.5,
                        tooltip={
                            'always_visible': True,
                            'placement': 'bottom'
                        })),
                dcc.Markdown("""**Selected Point**"""),
                html.Pre(id='click-data'),
                dash_table.DataTable(
                    id='editing-columns',
                    columns=[{
                        'name': i,
                        'id': i
                    } for i in df2.columns],
                    editable=False)
            ], style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                      'backgroundColor': '#6CC4A6', 'vertical-align': 'top'})
        ], style={'backgroundColor': '#6CC4A6', 'border': '1px solid #348C6E'},
                selected_style={'backgroundColor': '#348C6E', 'border': '1px solid #6CC4A6'}),
        dcc.Tab(label='Closest', children=[
            html.Div(html.H1("SOC in Europa", style={'text-align': 'center'}), style={'backgroundColor': 'green'}),
            html.Div(dcc.Graph(id="SOC-map2", config={'displayModeBar': False}),
                     style={'padding': '5px', 'width': '49%', 'display': 'inline-block', 'backgroundColor': '#6CC4A6'}),
            html.Div([
                dcc.Input(
                    id="my-id", type="number", placeholder="Longetude",
                    min=df2['GPS_LONG'].min(), max=df2['GPS_LONG'].max(),
                    style={'backgroundColor': '#4EA688', 'border': '1px solid #348C6E', 'color': 'white'}),
                dcc.Input(
                    id="my-id2", type="number", placeholder="Lattetude",
                    min=df2['GPS_LAT'].min(), max=df2['GPS_LAT'].max()),
                html.Button('Click Me', id='button'),
                dash_table.DataTable(
                    id='inputtab',
                    columns=[{
                        'name': i,
                        'id': i
                    } for i in df2.columns],
                    editable=False,
                    style_cell={'backgroundColor': '#4EA688', 'border': '1px solid #348C6E', 'color': 'white'},
                    style_header={'backgroundColor': '#348C6E', 'border': '1px solid #4EA688', 'color': 'white'}
                )
            ], style={'padding': '5px', 'width': '49%', 'display': 'inline-block',
                      'backgroundColor': '#6CC4A6', 'vertical-align': 'top'})
        ], style={'backgroundColor': '#6CC4A6', 'border': '1px solid #348C6E'},
                selected_style={'backgroundColor': '#348C6E', 'border': '1px solid #6CC4A6'})
    ])
], style={'padding': '10px', 'backgroundColor': '#4EA688'})

app.run_server(debug=True)
