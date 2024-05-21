import pandas as pd
import numpy as np

from dash import dash_table
from dash_extensions.enrich import dcc, html, Input, Output, State, Serverside #ServersideOutput

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign, Namespace

from parkrun.Parkrunner import Parkrunner
from parkrun.load_data import get_parkrun_locations

from dash_app.parkrunner_app.global_scheme import parkrun_purple, parkrun_purple_lighter

def register_callbacks(app):

    # Note - don't do @app.callback here. DashProxy() runs into duplicate callback output errors
    # from dash import callback
    from dash_extensions.enrich import callback

    #################################   Load data   #################################
    @callback(
        Output("store-parkrunner", "data"),
        Output("alert-wrong-id","children"),
        Input('input-ok-athlete-id', 'n_clicks'),
        State('input-athlete-id', 'value'),
        prevent_initial_call=True
    )
    def update_parkrunner(n_clicks, athlete_id):
        """Load parkrunner data"""
        if n_clicks:
            try:
                parkrunner = Parkrunner(athlete_id)
                parkrunner.fetch_data()
                error_alert = ""
            except:
                parkrunner = None
                error_alert = dbc.Alert(
                    [
                        html.P(
                            "No parkrunner profile found for this parkrunner ID.",
                            className="mb-0"
                        )
                    ],
                    color="danger"
                )

            # If need to JSON serialise the parkrunner class:
            # serialised_parkrunner = pickle.dumps(parkrunner)
            # encoded_parkrunner = base64.b64encode(serialised_parkrunner).decode('utf-8')

            # To decode:
            # decoded_parkrunner = base64.b64decode(encoded_parkrunner)
            # parkrunner = pickle.loads(decoded_parkrunner)

        return Serverside(parkrunner), error_alert


    #################################   Summary tab   #################################

    @callback(
        [
            Output("output-loading", "children"),

            Output('output-name', 'children'),
            Output('output-age-category', 'children'),
            Output('output-nbr-parkruns', 'children'),

            Output('output-summary-stats', 'children'),
            Output('output-recent-parkruns', 'children')
        ],
        Input('store-parkrunner', 'data'),

        prevent_initial_call=True
    )
    def render_parkrunner_summary_tab(parkrunner):
        """Update summary tab"""
        print(parkrunner)
        
        all_results_dld = parkrunner.tables['all_results_dld']
        other_info = parkrunner.other_info
        summary_stats = parkrunner.tables['summary_stats']

        info = other_info

        name = f'Parkrunner: {info["athlete_name"]}'
        age_category = f'Last updated age category: {info["last_age_category"]}'
        nbr_parkruns = f'Parkrun attendances: {info["nbr_parkruns"]} parkruns @ {all_results_dld.Event.nunique()} locations'

        summary_stats = (
            summary_stats
                .set_index(summary_stats.columns[0])
                .T
                .reset_index()
                .rename({"index": ""}, axis=1)
        )
        tbl_summary_stats = html.Div([
            html.H6("Summary statistics"),
            dash_table.DataTable(
                # to json
                data=summary_stats.to_dict('records'),
                columns=[{"name": i, "id": i} for i in summary_stats.columns],
                # formatting
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': parkrun_purple_lighter}],
                style_header={'backgroundColor': parkrun_purple, 'color': 'white', 'fontWeight': 'bold'},
                style_cell={'font-family': "Segoe UI"}
            )
        ])

        recent_parkruns = all_results_dld
        tbl_recent_parkruns = html.Div([
            html.H6("All parkrun results"),
            dash_table.DataTable(
                # to json
                data=recent_parkruns.to_dict('records'),
                columns=[{"name": i, "id": i} for i in recent_parkruns.columns],
                tooltip_header={
                    "Parkrun Number": ["Index number for count of parkruns completed, for this parkrunner"],
                    "Event": ["Parkrun event location name"],
                    "Run Date": ["Parkrun event date - this will typically be a Saturday, but could be other days for national special events!"],
                    "PB": ["Identifies if this finishing time was an all time personal best, at the time of the parkrun"],
                    "Age Grade": ["Age grade compares your time to other times of parkrunner's of your gender and age. The higher the age grade, the better the performance."]
                },

                # user interactivity
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_current=0,
                page_size=10,
                # export_format='csv',

                # formatting
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': parkrun_purple_lighter}],
                style_header={'backgroundColor': parkrun_purple,
                                'color': 'white',
                                'fontWeight': 'bold'},
                style_header_conditional=[{
                        'if': {'column_id': ["Parkrun Number", "Event", "Run Date", "PB", "Age Grade"]},
                        'textDecoration': 'underline',
                        'textDecorationStyle': 'dotted',
                }],
                css=[{
                    'selector': '.dash-table-tooltip',
                    'rule': 'background-color: black; color: white; border-radius: 6px'
                }],
                style_cell={'font-family': "Segoe UI"}
            ),

            html.Button("Download as CSV", id="dld-btn-parkrun-results"),
            dcc.Download(id="download-results-csv")
        ])

        return "", \
                name, age_category, nbr_parkruns, \
                tbl_summary_stats, tbl_recent_parkruns


    # SUMMARY TAB: Download parkrun results
    @callback(
        Output('download-results-csv', 'data'),
        Input('dld-btn-parkrun-results', 'n_clicks'),
        State('store-parkrunner', 'data'),
        prevent_initial_call=True
    )
    def download_tbl_parkrun_results(n_clicks, parkrunner):
        if n_clicks and parkrunner:
            df = parkrunner.tables['all_results_dld']
            return dcc.send_data_frame(df.to_csv, f"results-{parkrunner.athlete_id}.csv", index=False)
        

    #################################   Finishing times plot tab   #################################

    @callback(
        Output('output-finishing-times', 'figure'),
        Input('store-parkrunner', 'data'),
        prevent_initial_call=True
    )
    def render_parkrunner_results_plot(parkrunner):
        return parkrunner.plot_finishing_times()


    #################################   Locations box plot tab   #################################
    @callback(
        Output('output-boxplot-times', 'figure'),
        Input('input-boxplot-order-by', 'value'),
        Input('store-parkrunner', 'data'),
        prevent_initial_call=True
    )
    def render_parkrunner_locations_boxplot(by, parkrunner):
        if by == "Most attendances":
            return parkrunner.plot_boxplot_times_by_event(order_by="events")
        else:
            return parkrunner.plot_boxplot_times_by_event(order_by="time")
                

    #################################   Map tab  #################################

    @callback(
        Output('output-locations-map', 'children'),
        Input('store-parkrunner', 'data'),
        prevent_initial_call=True
    )
    def render_parkrunner_map(parkrunner):

        # Get parkrun locations json and convert to geojson
        features = get_parkrun_locations()

        all_results = parkrunner.tables["all_results"]

        search_for = all_results.Event.unique()
        keep_locations = []
        for x in features:
            if x["properties"]["EventShortName"] in search_for:

                event = x["properties"]["EventShortName"]
                df = all_results
                df = df[df.Event == event]

                last_attendance = str(df['Run Date'].max().date())
                attendances = len(df)
                fastest_time = str(df.Time_datetime.min())

                add_text = f"Most recent attendance: {last_attendance}<br>Total attendances: {attendances}<br>Fastest time: {fastest_time} "
                x['add_text'] = add_text

                keep_locations.append(x)

        dicts = [
            {
                "tooltip": f"{m['properties']['EventLongName']}<br> {m['add_text']}",
                "popup": f"{m['properties']['EventLongName']}<br> {m['add_text']}",
                "lat": m['geometry']['coordinates'][1],
                "lon": m['geometry']['coordinates'][0]
            } for m in keep_locations
        ]

        ns = Namespace('dashExtensions','dashExtensionssub')
        dl_cluster = dl.GeoJSON(
            id="markers",
            data=dlx.dicts_to_geojson(dicts),
            cluster=True,
            zoomToBoundsOnClick=True,
            options=dict(pointToLayer=ns('customMarker'))
        )

        # Centre coordinates
        centre_coords = keep_locations[0]['geometry']['coordinates']
        centre_coords.reverse()

        return dl.Map(
                            center=centre_coords, 
                            zoom=4,
                            children=[
                                dl.TileLayer(),
                                dl_cluster
                            ],
                            style={'width': '100%', 'height': '60vh'}
                        )
    

    #################################  Attendance heatmap tab  #################################

    @callback(
        Output('output-heatmap-attendance', 'figure'),
        Input('store-parkrunner', 'data'),
        prevent_initial_call=True
    )
    def render_parkrunner_attendance_heatmap(parkrunner):
        return parkrunner.plot_heatmap_mthly_attendance()