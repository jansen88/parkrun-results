import io
import base64
import pickle
import pandas as pd
import numpy as np

import dash
from dash import  dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq

from parkrun.Parkrunner import Parkrunner

from dash_app.parkrunner_app.global_scheme import parkrun_purple, parkrun_purple_lighter

def register_callbacks(app):

    #################################   Load data   #################################
    @app.callback(
        Output("store_parkrunner", "data"),
        Input('input_ok_athlete_id', 'n_clicks'),
        State('input_athlete_id', 'value'),
        prevent_initial_call=True
    )
    def update_parkrunner(n_clicks, athlete_id):
        """Load parkrunner data"""
        if n_clicks:
            parkrunner = Parkrunner(athlete_id)

            # TODO - check if can do ServersideOutput - may not need to serialise
            # dcc.Store needs to serialise what it's storing
            # As class is complex, use pickle to serialise and base64 to encode/decode the 'bytes' object
            # returned by pickle
            serialised_parkrunner = pickle.dumps(parkrunner)
            encoded_parkrunner = base64.b64encode(serialised_parkrunner).decode('utf-8')
        return encoded_parkrunner


    #################################   Update outputs   #################################
    @app.callback(
        [
            Output("output_loading", "children"),

            Output('output_name', 'children'),
            Output('output_age_category', 'children'),
            Output('output_nbr_parkruns', 'children'),

            Output('output_summary_stats', 'children'),
            Output('output_recent_parkruns', 'children'),

            Output('output_finishing_times', 'figure'),
            Output('output_heatmap_attendance', 'figure'),
        ],
        Input('store_parkrunner', 'modified_timestamp'),
        State('store_parkrunner', 'data'),
        prevent_initial_call=True
    )
    def update_outputs(ts, encoded_parkrunner):
        """Update everything"""
        if ts is None:
            raise dash.exceptions.PreventUpdate
        else:
            ctx = dash.callback_context
            if ctx.triggered:
                prop_id = ctx.triggered[0]['prop_id']
                if prop_id == 'store_parkrunner.modified_timestamp':
                    decoded_parkrunner = base64.b64decode(encoded_parkrunner)
                    parkrunner = pickle.loads(decoded_parkrunner)

                    ###### Parkrunner info ######
                    info = parkrunner.other_info

                    name = f'Parkrunner: {info["athlete_name"]}'
                    age_category = f'Last updated age category: {info["last_age_category"]}'
                    nbr_parkruns = f'Parkrun attendances: {info["nbr_parkruns"]} parkruns @ {parkrunner.tables["all_results"].Event.nunique()} locations'

                    ###### Tables ######
                    summary_stats = (
                        parkrunner.tables['summary_stats']
                            .set_index('Unnamed: 0')
                            .T
                            .reset_index(drop=False)
                            .rename({"Unnamed: 0": ""}, axis=1)
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

                    recent_parkruns = parkrunner.tables['all_results_dld']
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

                        html.Button("Download as CSV", id="dld_btn_parkrun_results"),
                        dcc.Download(id="download_parkrun_results")
                    ])

                    ###### Charts ######
                    fig_finishing_times = parkrunner.plot_finishing_times()
                    fig_boxplot_times = parkrunner.plot_boxplot_times_by_event(order_by="time")
                    fig_heatmap_attendance = parkrunner.plot_heatmap_mthly_attendance()

                    return "", \
                           name, age_category, nbr_parkruns, \
                           tbl_summary_stats, tbl_recent_parkruns, \
                           fig_finishing_times, \
                           fig_heatmap_attendance


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


    # LOCATIONS BOXPLOT TAB: Order axis by
    @app.callback(
        Output('output_boxplot_times', 'figure'),
        Input('input_boxplot_order_by', 'value'),
        Input('store_parkrunner', 'modified_timestamp'),
        State('store_parkrunner', 'data'),
    )
    def refresh_plot(order_by, ts, encoded_parkrunner):

        if ts is None:
            raise dash.exceptions.PreventUpdate
        else:
            ctx = dash.callback_context
            if ctx.triggered:
                prop_id = ctx.triggered[0]['prop_id']
                if prop_id in ['store_parkrunner.modified_timestamp', 'input_boxplot_order_by.value']:
                    decoded_parkrunner = base64.b64decode(encoded_parkrunner)
                    parkrunner = pickle.loads(decoded_parkrunner)
                    if order_by == "Most attendances":
                        BY = "events"
                    else:
                        BY = "time"
                    return parkrunner.plot_boxplot_times_by_event(order_by=BY)

