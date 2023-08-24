import dash_core_components as dcc
import dash_html_components as html
# from dash_app.dash_shared import shared_dash_nav_links
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq

from dash_app.parkrunner_app.global_scheme import HEADER_STYLE, SIDEBAR_STYLE, CONTENT_STYLE,\
      parkrun_purple, parkrun_purple_lighter

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

content = html.Div(
    [
        html.H4('🏃 Parkrunner profile'),
        html.P(""),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H6("🔎 Parkrunner"),
                    html.Div([
                        html.Div(dbc.Label("Search for parkrunner"), style={'display': 'inline-block'}),
                        html.Div(html.I(className="fa-solid fa-info-circle", style={"padding-left": "5px"}),
                                 id="tooltip_parkrunner_search",
                                 style={'display': 'inline-block'}),
                        dbc.Tooltip(
                            "Search using parkrun ID - e.g. 4360023 - as parkrunners are not currently searchable by name.",
                            target="tooltip_parkrunner_search",
                        ),
                        html.Div(dbc.Label(":"), style={'display': 'inline-block'})
                    ]),
                    dbc.Input(id="input_athlete_id",
                            placeholder="Athlete ID e.g. 4360023",
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
                                    dbc.Label("This plot shows how this parkrunner's finishing times have improved over time."),
                                    html.Br(),
                                    dbc.Label("Use the buttons and filters to zoom into the interactive plot below:"),
                                    dcc.Graph(id='output_finishing_times')
                                ], label="Parkrun results over time"),

                                dbc.Tab([
                                    html.P(""),
                                    html.H6("Parkrun location attendance and times"),
                                    html.Div([
                                        html.Div(dbc.Label("Order plot by:"), style={"display": "inline-block"}),
                                        html.Div(dcc.Dropdown(["Best times", "Most attendances"],
                                                     value="Best times",
                                                     id="input_boxplot_order_by",
                                                     clearable=False,
                                                     style={"width": "300px"}),
                                                 style={"margin-left": "10px",
                                                        "display": "inline-block",
                                                        "vertical-align": "middle"})
                                    ]),
                                    html.P(""),
                                    dbc.Label("This plot provides insights into this parkrunner's favourite and fastest parkruns."),
                                    html.Br(),
                                    dbc.Label("Use the filters to zoom into the interactive plot below:"),
                                    dcc.Graph(id='output_boxplot_times')
                                ], label="Top parkrun locations"),

                                dbc.Tab([
                                    html.P(""),
                                    html.H6("Parkrun location attendance"),
                                    dbc.Label("This plot illustrates how consistently this parkrunner attends parkruns:"),
                                    dcc.Graph(id='output_heatmap_attendance')
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

layout = html.Div([
    header,
    # sidebar
    content
])