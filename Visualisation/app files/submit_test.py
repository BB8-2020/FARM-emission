import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

app.layout = html.Div([
    dcc.Input(id='my-id', value='initial value', type="text"),
    html.Button('Click Me', id='button'),
    html.Div(id='my-div')
])


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input('button', 'n_clicks')],
    state=[State(component_id='my-id', component_property='value')]
)
def update_output_div(n_clicks, input_value):
    """
    Update the text line with the input given and the amount of clicks.

    Parameters
    ----------
        n_clicks (int): The amount of clicks.
        input_value (str): The given input.

    Returns
    -------
        String containing input_value and n_clicks.

    """
    return 'You\'ve entered "{}" and clicked {} times'.format(input_value, n_clicks)


if __name__ == '__main__':
    app.run_server(debug=True)
