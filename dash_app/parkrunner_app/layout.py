from dash_extensions.enrich import dcc, html

import dash_bootstrap_components as dbc

from dash_app.parkrunner_app.global_scheme import HEADER_STYLE, SIDEBAR_STYLE, CONTENT_STYLE, FOOTER_STYLE, \
    parkrun_purple, parkrun_purple_lighter, tab_height



layout = html.Div([
    ################ Header ################
    html.Div(
        children=[
            html.Div(html.I(className="fa-solid fa-person-running", style={"font-size": "30px", "padding-right": "10px"}),
                    style={'display': 'inline-block'}),
            html.Div(html.H4('Parkrunner', style={"vertical-align": "middle"}),
                    style={'display': 'inline-block'}),
        ],
        style=HEADER_STYLE
    ),

    ################ Content ################
    html.Div(
        children=[
            html.H4('🏃 Parkrunner profile'),
            html.P(""),
            html.Hr(),

            dbc.Row([
                ################ Search /filter ################
                dbc.Col([
                    dbc.Card([
                        html.H6("🔎 Parkrunner"),
                        html.Div([
                            html.Div(dbc.Label("Search for parkrunner"), style={'display': 'inline-block'}),
                            html.Div(
                                    html.I(className="fa-solid fa-info-circle", style={"padding-left": "5px"}),
                                    id="tooltip_parkrunner_search",
                                    style={'display': 'inline-block'}
                            ),
                            dbc.Tooltip(
                                "Search using parkrun ID - e.g. 7417035 (remove any prefix e.g. 'A') - as parkrunners are not currently searchable by name. Your parkrun ID can be found on your barcode or your profile page. ",
                                target="tooltip_parkrunner_search",
                            ),
                            html.Div(dbc.Label(":"), style={'display': 'inline-block'})
                        ]),
                        html.Div(id="alert-wrong-id"),
                        dbc.Input(id="input-athlete-id",
                                placeholder="Athlete ID e.g. 7417035",
                                style={"width": "400px"}),
                        html.P(""),
                        html.Button('Submit', id='input-ok-athlete-id', n_clicks=0,
                                    style={"width": "100px"})
                    ], style={"width": "90%", "padding": "20px", 'min-height':'35vh'}
                    )
                ], width=4),

                ################ Tabs ################
                dbc.Col([
                    dbc.Card([
                        dcc.Loading(
                            children=[
                                html.H6("📊 Results"),
                                dcc.Tabs([

                                    ################ Summary tab ################
                                    dcc.Tab([
                                                html.P(""),
                                                html.H4(id='output-name'),
                                                html.Div(id='output-age-category'),
                                                html.Div(id='output-nbr-parkruns'),
                                                html.P(""),

                                                html.Div(id='output-summary-stats', style={'width': '45%'}),
                                                html.P(""),
                                                html.Div(id='output-recent-parkruns', style={'width': '80%'})
                                            ],
                                            label="Summary",
                                            style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}
                                            ),
                                            
                                    ################ Finishing times plot tab ################
                                    dcc.Tab(
                                        [
                                            html.P(""),
                                            html.H6("All parkrun results over time"),
                                            dbc.Label("This plot shows how this parkrunner's finishing times have improved over time."),
                                            html.Br(),
                                            dbc.Label("Use the buttons and filters to zoom into the interactive plot below:"),
                                            dcc.Graph(id='output-finishing-times')
                                        ], 
                                        label="Results over time",
                                        style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}
                                    ),

                                    ################ Location bar plot tab ################
                                    dcc.Tab(
                                        [
                                            html.P(""),
                                            html.H6("Parkrun location attendance and times"),
                                            html.Div([
                                                html.Div(dbc.Label("Order plot by:"), style={"display": "inline-block"}),
                                                html.Div(
                                                        dcc.Dropdown(
                                                            ["Best times", "Most attendances"],
                                                            value="Best times",
                                                            id="input-boxplot-order-by",
                                                            clearable=False,
                                                            style={"width": "300px"}
                                                        ),
                                                        style={
                                                                "margin-left": "10px",
                                                                "display": "inline-block",
                                                                "vertical-align": "middle"
                                                        }
                                                )
                                            ]),
                                            html.P(""),
                                            dbc.Label("This plot provides insights into this parkrunner's favourite and fastest parkruns."),
                                            html.Br(),
                                            dbc.Label("Use the filters to zoom into the interactive plot below:"),
                                            dcc.Graph(id='output-boxplot-times')
                                        ],
                                        label="Top event locations",
                                        style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}
                                    ),

                                    # ################ Location map tab ################
                                    dcc.Tab(
                                    # dbc.Tab doesn't play well with dash-leaflet
                                        children=[
                                            html.P(""),
                                            html.H6("Parkrun locations"),
                                            dbc.Label("This interactive map shows the geographical locations of all the parkruns this parkrunner has attended:"),
                                            
                                            html.Div(id="output-locations-map"),
                                        ],
                                        label = "Locations map",
                                        style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}
                                    ),

                                    ################ Attendance heatmap tab ################
                                    dcc.Tab(
                                        [
                                            html.P(""),
                                            html.H6("Parkrun location attendance"),
                                            dbc.Label("This plot illustrates how consistently this parkrunner attends parkruns:"),
                                            dcc.Graph(id='output-heatmap-attendance')
                                        ],
                                        label="Parkrun attendance",
                                        style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}
                                    ),
                                        
                                ], style={'height': tab_height}),
                                html.Div(id="output-loading"),
                                
                                dcc.Store(id='store-parkrunner')
                                
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
    ),

    # ################ Footer ################
    # html.Div(
    #     children=[
    #         dbc.Row(
    #             [
    #                 html.A("GitHub", href='https://github.com/jansen88/parkrun-results', target="_blank",
    #                     style={"color": "grey"})
    #             ], style={"width": "100%", "display": "flex", "align-items":"center", "justify-content":"center"}
    #         )
    #     ],
    #     style=FOOTER_STYLE
    # ),

])