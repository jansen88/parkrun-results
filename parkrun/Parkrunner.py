# libs -----------------------------------------------
import requests
import numpy as np
import pandas as pd
import re
import datetime

import plotly.express as px
import plotly.graph_objs as go

from parkrun.constants import parkrun_url
import parkrun.load_data as load_data


# class for athlete data -----------------------------
class Parkrunner:
    """Scrapes athlete data from athlete_id and returns data and charts"""

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id

    def fetch_data(self):
        # scrape athlete data
        self.raw_scraped = self.scrape_data()

        # collect tables and other info from scraped data
        self.tables = self.collect_tables(raw_results=self.raw_scraped)
        self.other_info = self.collect_other_info(raw_results=self.raw_scraped)

    # Data scraping / collecting ----
    def scrape_data(self):
        """Scrape athlete data"""
        athlete_url = f"{parkrun_url}/parkrunner/{self.athlete_id}/all"

        return load_data.scrape_url(athlete_url)

    def collect_tables(self, raw_results) -> dict:
        """
        :param raw_results: Raw scraped output from self.scrape_data()
        :return: Dictionary of summary statistics, annual bests and all results
        """
        # scrape tables        
        scraped_tables = pd.read_html(raw_results.text)
        tables_map = {
            # table : table number (index)
            "summary_stats": 0,
            "annual_bests": 1,
            "all_results": 2,
        }

        scraped_tables = {k: scraped_tables[v] for k, v in tables_map.items()}

        # clean tables
        all_results = scraped_tables["all_results"]
        all_results["Run Date"] = pd.to_datetime(
            all_results["Run Date"], format="%d/%m/%Y"
        )

        all_results["Time_numeric"] = all_results["Time"].apply(self._convert_time_to_numeric)
        # FIXME - clean up, not sure why we had 2
        all_results["Time_datetime"] =  pd.to_datetime(
            all_results["Time"].apply(self._convert_time_to_string),
            format="%H:%M:%S"
        )
        all_results["Time_time"] = all_results["Time_datetime"].dt.time

        all_results = all_results.sort_values("Run Date")
        all_results["Parkrun Number"] = (
            all_results["Run Date"].rank(ascending=True).astype("int")
        )
        all_results.rename({"Pos": "Position"}, axis=1, inplace=True)

        # extra cleaning for download
        all_results_dld = (
            all_results
            # tag PBs
            .sort_values("Run Date", ascending=True)
            .assign(
                PB=lambda df: np.where(
                    df.Time_numeric == df.Time_numeric.cummin(), "⭐", None
                )
            )
            # reorder
            .loc[
                :,
                [
                    "Parkrun Number",
                    "Event",
                    "Run Date",
                    "Position",
                    "Time",
                    "PB",
                    "Age Grade",
                ],
            ]
            .sort_values("Run Date", ascending=False)
            .assign(**{"Run Date": lambda df: df["Run Date"].apply(lambda x: x.date())})
        )

        # update with cleaned table
        scraped_tables["all_results"] = all_results
        scraped_tables["all_results_dld"] = all_results_dld

        return scraped_tables

    def collect_other_info(self, raw_results) -> dict:
        """
        :param raw_results: Raw scraped output from self.scrape_data()
        :return: Dictionary of info such as athlete_name and number of parkruns
        """

        # scrape other info
        other_info_map = {
            # info : [string_search_start, string_search_end]
            "athlete_name": [
                "<h2>",
                '\xa0<span style="font-weight: normal;" title="parkrun ID"',
            ],
            # "milestone_club": ["Member of the parkrun", "Club"],
            "nbr_parkruns": ["<h3>\n", "parkruns total"],
            "last_age_category": ["Most recent age category was ", "\n"],
        }

        other_info = {
            k: re.search(v[0] + "(.*)" + v[1], raw_results.text).group(1).strip()
            for k, v in other_info_map.items()
        }

        return other_info

    # Plot output ----
    def plot_finishing_times(
        self,
        filter_parkrun=None,
        show_PB_only=False,
        filter_start=pd.Timestamp.min,
        filter_end=pd.Timestamp.max,
        show_num_events=None,
    ) -> go.Figure:
        """
        Note - Expects Run Date to be datetime and Time_numeric column to be created
        :param athlete: athlete id or name to plot in title of chart
        :param show_num_events: number of events (points) to show in chart
        :param filter_parkrun: name of parkrun event to filter to
        :param show_PB_only: filter PBs only - if parkrun filtered, shows PBs for that parkrun
        :return: Plot of parkrun finish times over all events from all_results table
        """

        df = self.tables["all_results"]

        # filter parkrun before PBs so PBs are for specific parkrun
        if filter_parkrun is not None:
            df = df[df.Event == filter_parkrun]

        # required calcs
        df["PB_times"] = df["Time"][(df["Time_numeric"] == df["Time_numeric"].cummin())]
        df["PB_times_numeric"] = df["Time_numeric"][
            (df["Time_numeric"] == df["Time_numeric"].cummin())
        ]

        # filter dates
        df = df[df["Run Date"].between(filter_start, filter_end)]

        # filter PB only
        if show_PB_only:
            df = df[df.Time == df.PB_times]

        # subset after PB calcs
        if show_num_events:
            df = df.tail(show_num_events)

        df_pb = df[~pd.isnull(df.PB_times_numeric)]

        ### build plot - ty chatgpt for converting from matplotlib

        # Create color map
        color_map = {
            event: color
            for event, color in zip(df["Event"].unique(), px.colors.qualitative.Dark24)
        }

        # Create scatter plot of all data
        scatter = px.scatter(
            df,
            x="Run Date",
            y="Time_numeric",
            color="Event",
            color_discrete_map=color_map,
            labels={"Time": "Finishing time", "Run Date": "Parkrun date"},
            hover_data={"Event": True, "Time": True, "Time_numeric": False},
        )
        scatter.update_traces(marker=dict(size=12))

        # Add a dotted line through all the points
        scatter.add_trace(
            go.Scatter(
                x=df["Run Date"],
                y=df["Time_numeric"],
                mode="lines",
                line=dict(color="DarkSlateGrey", dash="dot"),
                name="Trend",
                showlegend=False,
            )
        )

        # Add a circle border around personal best time data points
        pb_points = df.loc[df["Time_numeric"] == df["PB_times_numeric"]]
        scatter.add_trace(
            go.Scatter(
                x=pb_points["Run Date"],
                y=pb_points["Time_numeric"],
                mode="markers",
                marker=dict(
                    symbol="circle-open",
                    size=18,
                    line=dict(width=2),
                    color="DarkSlateGrey",
                ),
                hoverinfo="text",
                text=pb_points["Event"],
                name="Personal best",
            )
        )

        scatter.update_layout(
            height=600,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all", label="All"),
                        ]
                    )
                ),
                rangeslider=dict(visible=True),
                type="date",
            ),
            yaxis=dict(scaleanchor="x", scaleratio=1, autorange="reversed"),
            xaxis_title="Parkrun date",
            yaxis_title="Finishing time (mins)",
            plot_bgcolor="white",
        )

        # More styling
        scatter.update_xaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="DarkSlateGrey",
            gridcolor="lightgrey",
        )
        scatter.update_yaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="DarkSlateGrey",
            gridcolor="lightgrey",
        )

        # scatter.show()

        return scatter

    def plot_boxplot_times_by_event(self, order_by="time") -> go.Figure:
        """
        :param order_by: Order y axis by - accepted arguments 'events' and 'time'
        :return: Boxplot of finishing times by event
        """

        if order_by not in ["events", "time"]:
            raise ValueError(
                "Input argument `order_by` not in accepted arguments - 'events', 'time'."
            )

        df = self.tables["all_results"]

        # add participation count to Event y axis label, get n_event and avg_time to order by
        df = df.assign(
            n_event=lambda x: x.groupby("Event")["Run Date"].transform("nunique"),
            Event_append=lambda x: x.Event + " [" + x.n_event.astype("str") + "]",
            min_time=lambda x: x.groupby("Event")["Time_time"].transform("min"),
        )
        if order_by == "time":
            df = df.sort_values("min_time")
        else:
            df = df.sort_values("n_event", ascending=False)

        fig = go.Figure()

        colours = px.colors.qualitative.Dark24[: df["Event"].unique().size]
        for event, colour in zip(df["Event"].unique(), colours):
            dff = df[df["Event"] == event]
            fig.add_trace(
                go.Box(
                    y=dff["Time_datetime"],
                    x=dff["Event_append"],
                    name=event,
                    marker_color=colour,
                    boxpoints="all",
                    customdata=np.stack(
                        (dff["Run Date"].astype("str"), dff["n_event"], dff["Event"]),
                        axis=-1,
                    ),
                    hovertemplate="<br>".join(
                        [
                            "Event: %{customdata[2]}",
                            "Count of attendances: %{customdata[1]}",
                            "Run date: %{customdata[0]}",
                            "Finishing time: %{y}",
                        ]
                    ),
                )
            )

        fig.update_yaxes(tickformat="%M:%S")
        fig.update_layout(
            height=600,
            yaxis=dict(scaleanchor="x", scaleratio=1, autorange="reversed"),
            xaxis=dict(rangeslider=dict(visible=True)),
            xaxis_title="Parkrun location and attendances",
            yaxis_title="Finishing time (mins)",
            plot_bgcolor="white",
            margin=dict(t=20),
        )

        # More styling
        fig.update_xaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="DarkSlateGrey",
            gridcolor="lightgrey",
        )
        fig.update_yaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="DarkSlateGrey",
            gridcolor="lightgrey",
        )

        return fig

    def plot_heatmap_mthly_attendance(self) -> go.Figure:
        """
        :return: Heatmap of attendance count by year / month
        """

        def tag_year_month(df, date_col):
            """Helper function for this heatmap - assign year / month"""
            return df.assign(
                year=lambda x: x[date_col].dt.year,
                month_int=lambda x: x[date_col].dt.month,
                month=lambda x: x[date_col].dt.month_name(),
            )

        # tag parkrunner run dates with year/month
        participation = tag_year_month(
            df=self.tables["all_results"], date_col="Run Date"
        )
        run_dates = self.tables["all_results"]["Run Date"]

        # create mapping table of all year/months to ensure completeness if no participation in some months
        dates = pd.date_range(
            run_dates.min().replace(day=1),  # floor first date
            datetime.datetime.now(),
            freq="MS",
        )
        all_dates = tag_year_month(df=pd.DataFrame({"dates": dates}), date_col="dates")

        # count attendance
        participation = (
            all_dates.merge(participation, how="left")
            .groupby(["year", "month", "month_int"])
            .agg(
                count=("Run Date", "nunique"),
                parkruns=("Event", lambda x: x.str.cat(sep=", ")),
                times=("Time_datetime", lambda x: x.astype("str").str.cat(sep=", ")),
            )
            .sort_values(["year", "month_int"])
            .reset_index()
        )
        participation["combined"] = [
            ([x], [y]) for x, y in zip(participation.parkruns, participation.times)
        ]

        months = (
            participation.loc[:, ["month", "month_int"]]
            .drop_duplicates()
            .sort_values("month_int")["month"]
            .to_list()
        )

        # pivot data for heatmap
        z1 = participation.pivot(index=["year"], columns="month", values="count").loc[
            :, months
        ]

        # pivot customdata for z2
        z2 = participation.pivot(
            index=["year"], columns="month", values="combined"
        ).loc[:, months]

        fig = px.imshow(
            z1,
            labels=dict(x="Month", y="Year", color="Number of parkruns"),
            x=[str(i) for i in z1.columns.to_list()],
            y=[str(i) for i in z1.index.to_list()],
            color_continuous_scale="oranges",
            text_auto=True,
        )
        fig.update(
            data=[
                {
                    "customdata": z2,
                    "hovertemplate": "Year: %{y}<br>Month: %{x}<br>Number of parkruns: %{z}<br>Parkrun locations: %{customdata[0]}<br>Times: %{customdata[1]}<extra></extra>",
                }
            ]
        )
        fig.update_layout(plot_bgcolor="white", margin=dict(t=20))

        return fig

    # helper functions -----
    def _extract_time(self, time_str):
        parts = time_str.split(':')
        
        hours = 0
        minutes = 0
        seconds = 0
        
        if len(parts) == 3:  # 'hh:mm:ss' format
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:  # 'mm:ss' format
            minutes, seconds = int(parts[0]), int(parts[1])
        else:
            raise ValueError("Invalid time format")
        
        return hours, minutes, seconds

    def _convert_time_to_numeric(self, time_str):
        """Helper function to convert mm:ss times to numeric"""
        hours, minutes, seconds = self._extract_time(time_str)
        return hours * 60 + minutes + seconds / 60

    def _convert_time_to_string(self, time_str): 
        hours, minutes, seconds = self._extract_time(time_str)
        return f"{hours}:{minutes}:{seconds}"

    def _label_point(self, x, y, val, ax):
        """Helper function to add labels - assumes x axis is datetime (for Run Date)"""
        a = pd.concat({"x": x, "y": y, "val": val}, axis=1)
        for i, point in a.iterrows():
            # NOTE - assumes x axis is datetime - Run Date
            ax.text(
                point["x"] + datetime.timedelta(days=4), point["y"], str(point["val"])
            )
