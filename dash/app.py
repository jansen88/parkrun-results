# Load packages ----
from pprint import pprint
import datetime
import pandas as pd

import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
# import plotly
# import mpld3
import io
import base64
import pickle
import numpy as np

import os
import sys

# add directory to paths to ensure module is imported correctly
CURR_DIR = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(os.path.dirname(CURR_DIR))
from modules.Parkrunner import Parkrunner
from modules.Parkrun import Parkrun

# Initialise dash app ----
app = Dash(__name__,
           external_stylesheets=[
               dbc.themes.BOOTSTRAP,
               {  # font-awesome
                   "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css",
                   "rel": "stylesheet",
                   # "integrity": "sha512-iBBXm8fW90+nuLcSKlbmrPcLa0OT92xO1BIsZ+ywDWZCvqsWgccV3gFoRBv0z+8dLJgyAHIhR35VZc2oM/gI1w==",
                   "crossorigin": "anonymous",
                   "referrerpolicy": "no-referrer"
               }]
           )
app.title = "Parkrun Dash"

# UI ----
header_height = "4rem"
sidebar_width = "12vw"
parkrun_purple = "#2b233d"
parkrun_purple_lighter = "#d1cae1" #"#afa3ca"

HEADER_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "right": 0,
    "height": header_height,
    "padding": "1rem 1rem",
    "background-color": parkrun_purple,
    "color": "#FFFFFF"
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": header_height,
    "left": 0,
    "bottom": 0,
    "width": sidebar_width,
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "position": "fixed",
    "top": header_height,
    "height": "90vh",
    "width": "100vw",
    # "margin-left": sidebar_width,
    "padding": "1rem 1rem",
    "overflowY": "scroll"
}

header = html.Div(
    [
        html.Div(html.I(className="fa-solid fa-person-running", style={"font-size": "30px", "padding-right": "10px"}),
                 style={'display': 'inline-block'}),
        html.Div(html.H4('Parkrun Dash', style={"vertical-align": "middle"}),
                 style={'display': 'inline-block'})

    ],
    style=HEADER_STYLE
)

sidebar = html.Div(
    [

    ],
    style=SIDEBAR_STYLE
)

summary_tab = [
    html.P(""),
    html.H4(id='output_name'),
    html.Div(id='output_age_category'),
    html.Div(id='output_nbr_parkruns'),
    html.P(""),

    html.Div(id='output_summary_stats',
             style={'width': '45%'}),
    html.P(""),
    html.Div(id='output_recent_parkruns',
             style={'width': '80%'#,
                    #'maxHeight': '400px'#,
                    #'overflowY': 'auto'
                    })
]

finishing_times_tab = [
    dcc.Graph(id='output_finishing_times')
]

content = html.Div(
    [
        html.H4('🏃 Parkrunner profile'),
        html.P(""),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H6("🔎 Parkrunner"),
                    dbc.Label("Search for parkrunner:"),
                    dbc.Input(id="input_athlete_id",
                            placeholder="Athlete ID e.g. 7417035",
                            style={"width": "400px"}),
                    html.P(""),
                    html.Button('Submit', id='input_ok_athlete_id', n_clicks=0,
                                style={"width": "100px"})
                ], style={"width": "90%", "padding": "20px", 'min-height':'35vh'}
                )
            ], width=4),

            dbc.Col([
                dbc.Card([
                    dcc.Loading(
                        children=[
                            html.H6("📊 Results"),
                            dbc.Tabs([
                                dbc.Tab(summary_tab,
                                        label="Parkrunner summary"),
                                dbc.Tab([
                                    html.P(""),
                                    html.H6("All parkrun results over time"),
                                    dbc.Label("Use the buttons and filters to zoom into the interactive plot below:"),
                                    dcc.Graph(id='output_finishing_times')
                                ], label="Parkrun results over time"),
                                dbc.Tab([
                                    html.P(""),
                                    html.H6("Parkrun location attendance and times"),
                                    dbc.Label("Use the filters to zoom into the interactive plot below:"),
                                    dcc.Graph(id='output_boxplot_times')
                                ], label="Top parkrun locations"),
                                dbc.Tab([
                                    html.Img(id='output_heatmap_attendance')
                                ], label="Parkrun attendance")
                            ]),
                            html.Div(id="output_loading"),
                            dcc.Store(id='store_parkrunner', data=None)
                        ],
                        type="circle",
                        color=parkrun_purple,
                        style={"width": "20rem", "height": "20rem", "padding-top": "30vh"}
                    )
                ], style={"width": "90%", "padding": "20px",'min-height':'50vh'})
            ], width=8)
        ])
    ],
    style=CONTENT_STYLE
)

app.layout = html.Div([
    header,
    # sidebar
    content
])


# Callbacks ----

# Fetch parkrunner class and store intermediate value for other callbacks
@app.callback(
    Output("store_parkrunner", "data"),
    Input('input_ok_athlete_id', 'n_clicks'),
    State('input_athlete_id', 'value'),
    prevent_initial_call=True
)
def update_parkrunner(n_clicks, athlete_id):
    if n_clicks:
        parkrunner = Parkrunner(athlete_id)

        # dcc.Store needs to serialise what it's storing
        # As class is complex, use pickle to serialise and base64 to encode/decode the 'bytes' object
        # returned by pickle
        serialised_parkrunner = pickle.dumps(parkrunner)
        encoded_parkrunner = base64.b64encode(serialised_parkrunner).decode('utf-8')
    return encoded_parkrunner


# Update outputs when parkrunner store is updated
@app.callback(
    Output("output_loading", "children"),

    Output('output_name', 'children'),
    Output('output_age_category', 'children'),
    Output('output_nbr_parkruns', 'children'),

    Output('output_summary_stats', 'children'),
    Output('output_recent_parkruns', 'children'),

    Output('output_finishing_times', 'figure'),
    Output('output_boxplot_times', 'figure'),
    Output('output_heatmap_attendance', 'src'),

    Input('store_parkrunner', 'modified_timestamp'),
    State('store_parkrunner', 'data'),
    prevent_initial_call=True
)
def update_outputs(ts, encoded_parkrunner):
    if ts is None:
        raise dash.exceptions.PreventUpdate
    else:
        ctx = dash.callback_context
        if ctx.triggered:
            prop_id = ctx.triggered[0]['prop_id']
            if prop_id == 'store_parkrunner.modified_timestamp':
                decoded_parkrunner = base64.b64decode(encoded_parkrunner)
                parkrunner = pickle.loads(decoded_parkrunner)

                # Parkrunner info
                info = parkrunner.other_info

                name = f'Parkrunner: {info["athlete_name"]}'
                age_category = f'Last updated age category: {info["last_age_category"]}'
                nbr_parkruns = f'Total parkrun attendances: {info["nbr_parkruns"]}'

                # Tables
                summary_stats = parkrunner.tables['summary_stats']
                summary_stats.set_index('Unnamed: 0').T.reset_index(drop=False, inplace=True)
                summary_stats.rename({"Unnamed: 0": ""}, axis=1, inplace=True)
                tbl_summary_stats = html.Div([
                    html.H6("Summary statistics"),
                    dash_table.DataTable(
                        # to json
                        data=summary_stats.to_dict(orient='rows'),
                        columns=[{"name": i, "id": i} for i in summary_stats.columns],
                        # formatting
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': parkrun_purple_lighter}],
                        style_header={'backgroundColor': parkrun_purple, 'color': 'white', 'fontWeight': 'bold'},
                        style_cell={'font-family': "Segoe UI"}
                    )
                ])

                recent_parkruns = parkrunner.tables['all_results_dld']
                tbl_recent_parkruns = html.Div([
                    html.H6("All parkrun results"),
                    dash_table.DataTable(
                        # to json
                        data=recent_parkruns.to_dict(orient='rows'),
                        columns=[{"name": i, "id": i} for i in recent_parkruns.columns],

                        # user interactivity
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_current=0,
                        page_size=10,
                        # export_format='csv',

                        # formatting
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': parkrun_purple_lighter}],
                        style_header={'backgroundColor': parkrun_purple, 'color': 'white', 'fontWeight': 'bold'},
                        style_cell={'font-family': "Segoe UI"}
                    ),

                    html.Button("Download as CSV", id="dld_btn_parkrun_results"),
                    dcc.Download(id="download_parkrun_results")
                ])

                # Charts

                def matplotlib_to_img(fig):
                    """Helper function - convert matplotlib charts to img to show in Dash"""

                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
                    buf.close()
                    return "data:image/png;base64,{}".format(data)

                fig_finishing_times = parkrunner.plot_finishing_times()
                # fig_finishing_times = matplotlib_to_img(fig_finishing_times)

                fig_boxplot_times = parkrunner.plot_boxplot_times_by_event(order_by="time")
                # fig_boxplot_times = matplotlib_to_img(fig_boxplot_times)

                fig_heatmap_attendance = parkrunner.plot_heatmap_mthly_attendance()
                fig_heatmap_attendance = matplotlib_to_img(fig_heatmap_attendance)

                return "", \
                       name, age_category, nbr_parkruns, \
                       tbl_summary_stats, tbl_recent_parkruns, \
                       fig_finishing_times, fig_boxplot_times, fig_heatmap_attendance


# SUMMARY TAB: Download parkrun results
@app.callback(
    Output('download_parkrun_results', 'data'),
    Input('dld_btn_parkrun_results', 'n_clicks'),
    State('store_parkrunner', 'data'),
    prevent_initial_call=True
)
def download_tbl_parkrun_results(n_clicks, encoded_parkrunner):
    if n_clicks and encoded_parkrunner:
        decoded_parkrunner = base64.b64decode(encoded_parkrunner)
        parkrunner = pickle.loads(decoded_parkrunner)

        return dcc.send_data_frame(parkrunner.tables['all_results_dld'].to_csv,
                                   filename="All Results.csv", index=False)


# Run app ----
if __name__ == "__main__":
    app.run_server(debug=True,
                   use_reloader=False)
