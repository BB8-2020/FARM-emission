import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html


df2 = pd.read_pickle('Lucas0_1.pkl')

token = open("token.txt").read()
fig2 = px.scatter_mapbox(df2, lat="GPS_LAT", lon="GPS_LONG",
                         color_discrete_sequence=["green"], zoom=5, height=500, size_max=10,
                         color_continuous_scale=px.colors.diverging.RdYlGn, color='OC', opacity=0.75,
                         hover_name="POINT_ID")
fig2.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

fig = go.Figure(data=go.Scatter(x=df2['POINT_ID'], y=df2['OC']))

app = dash.Dash()
app.layout = html.Div([
    html.H1("Bigfoot Sightings", className="text-center"),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig)
])

app.run_server(debug=True)
