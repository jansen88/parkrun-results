# Load packages ----
from pprint import pprint
import datetime
import pandas as pd

from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
# import plotly
# import mpld3
import io
import base64

import os
import sys
CURR_DIR = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(os.path.dirname(CURR_DIR))
from modules.Parkrunner import Parkrunner
from modules.Parkrun import Parkrun


# Initialise dash app ----
app = Dash(__name__,
            external_stylesheets = [
                dbc.themes.BOOTSTRAP,
                { # font-awesome
                    "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css",
                    "rel": "stylesheet",
                    #"integrity": "sha512-iBBXm8fW90+nuLcSKlbmrPcLa0OT92xO1BIsZ+ywDWZCvqsWgccV3gFoRBv0z+8dLJgyAHIhR35VZc2oM/gI1w==",
                    "crossorigin": "anonymous",
                    "referrerpolicy": "no-referrer"
                }]
        )
app.title = "Parkrun Dash"


# UI ----
header_height = "4rem"
sidebar_width = "12vw"

HEADER_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "right": 0,
    "height": header_height,
    "padding": "1rem 1rem",
    "background-color": "#2b233d", # parkrun purple
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
    #"margin-left": sidebar_width,
    "padding": "1rem 1rem",
}

header = html.Div(
    [
        html.Div(html.I(className = "fa-solid fa-person-running", style = {"font-size": "30px", "padding-right":"10px"}), 
                 style={'display': 'inline-block'}),
        html.Div(html.H3('Parkrun Dash', style = {"vertical-align": "middle"}),
                 style={'display': 'inline-block'})
        
    ], 
    style = HEADER_STYLE
)

sidebar = html.Div(
    [

    ],
    style = SIDEBAR_STYLE
)

content = html.Div(
    [
        html.H3('🏃 Parkrunner profile'),
        html.P(""), 

        dbc.Label("Athlete to look up:"),
        dbc.Input(id="input_athlete_id",
                  placeholder="Athlete ID e.g. 7417035", size="lg"),
        html.P(""), 
        html.Button('Search', id='input_ok_athlete_id', n_clicks=0),

        html.Hr(),
        html.P(""),

        dbc.Row(
            [
                dbc.Col([
                    dbc.Card(
                    dbc.CardBody([
                        html.H4(id='output_name'),
                        html.Div(id='output_age_category'),
                        html.Div(id='output_nbr_parkruns'),
                        html.P(""),
                        
                        dbc.Label("Summary stats - all time"),
                        html.Div(id='output_summary_stats'),
                        html.P(""),
                        dbc.Label("Most recent results"),
                        html.Div(id='output_recent_parkruns')
                        ])
                    ),
                    html.P("")
                ]),
                dbc.Col([
                        dbc.Card(
                            dbc.Tabs([
                                dbc.Tab([
                                    html.Img(id='output_finishing_times')
                                ], label = "Finishing times"),
                                dbc.Tab([
                                    html.Img(id='output_boxplot_times')
                                ], label = "Top parkrun locations"),
                                dbc.Tab([
                                    html.Img(id='output_heatmap_attendance')
                                ], label = "Parkrun attendance")
                            ])
                        )
                ])
            ]
        )
    ],
    style = CONTENT_STYLE
)

app.layout = html.Div([
    header,
    #sidebar
    content
])


# Callbacks ----
@app.callback(
    Output('output_name', 'children'),
    Output('output_age_category', 'children'),
    Output('output_nbr_parkruns', 'children'),

    Output('output_summary_stats', 'children'),
    Output('output_recent_parkruns', 'children'),

    Output('output_finishing_times', 'src'),
    Output('output_boxplot_times', 'src'),
    Output('output_heatmap_attendance', 'src'),

    [Input('input_athlete_id', 'value'),
     Input('input_ok_athlete_id', 'n_clicks')]
)
def get_athlete_details(athlete_id, button):
    
    # Parkrunner class
    parkrunner = Parkrunner(athlete_id)

    # Parkrunner info
    info = parkrunner.other_info

    name = f'Parkrunner: {info["athlete_name"]}'
    age_category = f'Last updated age category: {info["last_age_category"]}'
    nbr_parkruns = f'Total parkrun attendances: {info["nbr_parkruns"]}'

    # Tables
    def pd_df_to_dash_table(df):
        return dash_table.DataTable(
            # to json
            data = df.to_dict(orient='rows'),
            columns = [{"name": i, "id": i} for i in df.columns],
            # formatting
            style_data={'color': 'black', 'backgroundColor': 'white'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
            style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold'},
            style_cell={'font-family':"Segoe UI"}
        )

    summary_stats = parkrunner.tables['summary_stats']
    tbl_summary_stats = pd_df_to_dash_table(summary_stats)

    recent_N = 5
    recent_parkruns = parkrunner.tables['all_results'] \
        [["Event", "Run Date", "Pos", "Time", "Age Grade"]] \
        .sort_values("Run Date", ascending = False) \
        .head(recent_N) 
    tbl_recent_parkruns = pd_df_to_dash_table(recent_parkruns)


    # Charts

    def matplotlib_to_img(fig):
        """Helper function - convert matplotlib charts to img to show in Dash"""

        buf = io.BytesIO() 
        fig.savefig(buf, format = "png")
        data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        buf.close()
        return "data:image/png;base64,{}".format(data) 

    fig_finishing_times = parkrunner.plot_finishing_times(show_num_events = 25)
    fig_finishing_times = matplotlib_to_img(fig_finishing_times)

    fig_boxplot_times = parkrunner.plot_boxplot_times_by_event(order_by = "time")
    fig_boxplot_times = matplotlib_to_img(fig_boxplot_times)

    fig_heatmap_attendance = parkrunner.plot_heatmap_mthly_attendance()
    fig_heatmap_attendance = matplotlib_to_img(fig_heatmap_attendance)

    return name, age_category, nbr_parkruns, \
        tbl_summary_stats, tbl_recent_parkruns, \
        fig_finishing_times, fig_boxplot_times, fig_heatmap_attendance


# Run app ----
if __name__ == "__main__":
    app.run_server(debug=True,
                   use_reloader=False)
