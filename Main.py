
#    import section    #
import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np
import plotly.subplots as sp
import PySimpleGUI as sg

# Initialize the Dash app with suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Sample data - to be modified dynamically
phases = ["PRIOR", "TFFx1", "TFFx2", "ADJ1", "ADJ2", "ME"]
metrics = [
    "Screenline - Flow Difference < 5%",
    "Screenline - Flow Difference < 7.5%",
    "TAG Flow Criteria (Links)",
    "Links - GEH < 5",
    "Links - GEH <7.5",
    "JI- Routes w. Time difference < 15%"
]

# Preloaded list of schemes
preloaded_schemes = ["Scheme1", "Scheme2", "Scheme3", "Scheme4", "Scheme5", "Scheme6", "Scheme7", "Scheme8", "Scheme9", "Scheme10", "Scheme11", "Scheme12", "Scheme13", "Scheme14", "Scheme15"]

# Initialize your data here with the preloaded schemes
data = np.random.rand(len(metrics), len(preloaded_schemes))

# Format the data as text
text_data = np.around(data, decimals=2).astype(str)

# Import the necessary libraries
import plotly.subplots as sp
import plotly.graph_objects as go

# Variable to track whether GUI is initialized
gui_initialized = False

# Function to create the heatmap figure
def create_heatmap(data, schemes, metrics, phases, text_data, selected_schemes=None):
    if selected_schemes is not None:
        schemes_to_initialize = selected_schemes
    else:
        schemes_to_initialize = schemes
    
    # Calculate the width of each scheme block dynamically
    scheme_block_width = 2.0 / len(schemes_to_initialize)
    
    # Create a subplot figure with shared x-axes
    fig = sp.make_subplots(
        rows=len(phases), cols=1,
        shared_xaxes=True,
        subplot_titles=[f"Phase: {phase}" for phase in phases]
    )
    
    # Add a heatmap trace for each phase
    for i, phase in enumerate(phases):
        heatmap = go.Heatmap(
            z=data,
            x=schemes_to_initialize,  # Use schemes_to_initialize
            y=metrics,
            text=text_data,
            texttemplate="%{text}",
            hoverinfo="none",
            showscale=True,
            colorscale="RdYlGn",  # Change the colorscale to go from red to green
            colorbar=dict(title="Performance")
        )
        fig.add_trace(heatmap, row=i + 1, col=1)
        
        
        
    # Update annotations for each cell
    annotations = []
    for n, row in enumerate(data[:, :len(schemes_to_initialize)]):  # Slice data for current schemes
        for m, val in enumerate(row):
            annotations.append(
                go.layout.Annotation(
                    text=str(text_data[n][m]),  # Access text_data without additional slicing here
                    x=schemes_to_initialize[m],  # Use schemes_to_initialize
                    y=metrics[n],
                    xref="x" + str(i + 1) if i > 0 else "x",
                    yref="y" + str(i + 1) if i > 0 else "y",
                    showarrow=False,
                    font=dict(size=10),
                )
            )
    
    # Update layout settings for the figure
    fig.update_layout(
        height=1500,  # Increase the height
        width=800,    # Set an initial width
        title="Grid Heatmap for Performance Metrics",
        showlegend=False
    )

    # Return the created figure
    return fig

# PySimpleGUI window for selecting schemes
layout = [
    [sg.Text("Select schemes to initialize:")],
    [sg.Listbox(preloaded_schemes, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(20, 10), key="-SCHEMES-")],
    [sg.Button("Initialize Selected Schemes")],
]

# Event loop for PySimpleGUI window
while True:
    if not gui_initialized:
        window = sg.Window("Select Schemes", layout, finalize=True)
        gui_initialized = True
    
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Initialize Selected Schemes":
        selected_schemes = values["-SCHEMES-"]
        
       # Create a new heatmap figure with updated data
        fig = create_heatmap(data, selected_schemes, metrics, phases, text_data)

        # Update layout settings for the figure
        fig.update_layout(
            height=1500,  # Increase the height
            width=800 + 20 * len(selected_schemes),    # Set an initial width and increase it based on the number of schemes
            title="Grid Heatmap for Performance Metrics",
            showlegend=False
        )

        # Create the Dash app layout with the heatmap and Add/Remove buttons
        app.layout = html.Div([
            dcc.Graph(
                id='heatmap',
                figure=fig,
                style={'overflowX': 'scroll', 'width': '800px'}  # Add a horizontal scrollbar
            ),
            html.Div([
                dcc.Dropdown(
                    id='add-scheme-dropdown',
                    options=[{'label': scheme, 'value': scheme} for scheme in preloaded_schemes if scheme not in selected_schemes],
                    value=None,
                    multi=False
                ),
                html.Button('Add Scheme', id='add-scheme-button'),
                dcc.Dropdown(
                    id='remove-scheme-dropdown',
                    options=[{'label': scheme, 'value': scheme} for scheme in selected_schemes],
                    value=None,
                    multi=False
                ),
                html.Button('Remove Scheme', id='remove-button')
            ]),
        ])
        
        window.close()
        break

    
    selected_schemes = preloaded_schemes.copy()

@app.callback(
    [Output('heatmap', 'figure'),
     Output('remove-scheme-dropdown', 'options'),
     Output('add-scheme-dropdown', 'options')],
    [Input('add-scheme-button', 'n_clicks'),
     Input('remove-button', 'n_clicks')],
    [State('remove-scheme-dropdown', 'value'),
     State('add-scheme-dropdown', 'value'),
     State('heatmap', 'figure')]
)


def update_graph(add_clicks, remove_clicks, scheme_to_remove, scheme_to_add, current_figure):
    global selected_schemes, data, text_data

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-scheme-button' and scheme_to_add:
        selected_schemes.append(scheme_to_add)
        new_data_column = np.random.rand(len(metrics))
        data = np.column_stack((data, new_data_column))
    elif button_id == 'remove-button' and scheme_to_remove:
        index_to_remove = selected_schemes.index(scheme_to_remove)
        selected_schemes.remove(scheme_to_remove)
        data = np.delete(data, index_to_remove, axis=1)

    # Recalculate the text data
    text_data = np.around(data, decimals=2).astype(str)

    # Create a new heatmap figure with updated data
    fig = create_heatmap(data, selected_schemes, metrics, phases, text_data)

    # Update dropdown options
    add_dropdown_options = [{'label': scheme, 'value': scheme} for scheme in preloaded_schemes if scheme not in selected_schemes]
    remove_dropdown_options = [{'label': scheme, 'value': scheme} for scheme in selected_schemes]

    return fig, remove_dropdown_options, add_dropdown_options


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)

