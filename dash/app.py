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
    "width": "100vw",
    #"margin-left": sidebar_width,
    "padding": "1rem 1rem"
}

header = html.Div(
    [
        html.Div(html.I(className = "fa-solid fa-person-running", style = {"font-size": "30px", "padding-right":"10px"}), 
                 style={'display': 'inline-block'}),
        html.Div(html.H4('Parkrun Dash', style = {"vertical-align": "middle"}),
                 style={'display': 'inline-block'})
        
    ], 
    style = HEADER_STYLE
)

sidebar = html.Div(
    [

    ],
    style = SIDEBAR_STYLE
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
                        style={'width': '70%',
                               'height': '300px',
                               'overflowY': 'auto'})
                ]

content = html.Div(
    [
        html.H4('🏃 Parkrunner profile'),
        html.P(""), 

        dbc.Label("Athlete to look up:"),
        dbc.Input(id="input_athlete_id",
                  placeholder="Athlete ID e.g. 7417035",
                  style={"width":"700px"}),
        html.P(""), 
        html.Button('Search', id='input_ok_athlete_id', n_clicks=0),

        html.Hr(),
        html.P(""),

        dbc.Row(
            [
                dbc.Col([
                        dcc.Loading(
                            children=[
                                html.Div(id="output_loading"),
                                dbc.Tabs([
                                    dbc.Tab(summary_tab,
                                            label = "Summary"),
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
                            ],
                            type="circle",
                            style={"width": "20rem", "height": "20rem"}
                        ),
                ], width = 12)
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
    Output("output_loading", "children"), 

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
    summary_stats = parkrunner.tables['summary_stats']
    summary_stats.set_index('Unnamed: 0').T.reset_index(drop=False, inplace=True)
    summary_stats.rename({"Unnamed: 0": ""}, axis=1, inplace=True) 
    tbl_summary_stats = html.Div([
        html.H5("Summary statistics"),
        dash_table.DataTable(
            # to json
            data = summary_stats.to_dict(orient='rows'),
            columns = [{"name": i, "id": i} for i in summary_stats.columns],
            # formatting
            style_data={'color': 'black', 'backgroundColor': 'white'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
            style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold'},
            style_cell={'font-family':"Segoe UI"}
        )
    ])

    # recent_N = 5
    recent_parkruns = parkrunner.tables['all_results'] \
        [["Parkrun Number", "Event", "Run Date",  "Position", "Time", "Age Grade"]] \
        .sort_values("Run Date", ascending = False) #\
        # .head(recent_N) 
    recent_parkruns["Run Date"] = recent_parkruns["Run Date"].apply(lambda x: x.date())
    tbl_recent_parkruns = html.Div([
        html.H5("All parkrun results"),
        dash_table.DataTable(
            # to json
            data = recent_parkruns.to_dict(orient='rows'),
            columns = [{"name": i, "id": i} for i in recent_parkruns.columns],
            
            # user interactivity
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            page_current=0,
            page_size=10,

            # formatting
            style_data={'color': 'black', 'backgroundColor': 'white'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
            style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold'},
            style_cell={'font-family':"Segoe UI"}
        )
    ])


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

    return "", \
        name, age_category, nbr_parkruns, \
        tbl_summary_stats, tbl_recent_parkruns, \
        fig_finishing_times, fig_boxplot_times, fig_heatmap_attendance


# Run app ----
if __name__ == "__main__":
    app.run_server(debug=True,
                   use_reloader=False)
