# Last updated: 2023-02-23
# Dev notes - returns a lot of warnings right now
# Doesn't seem to break anything but probably want to look at fixing
# e.g. posx and posy should be finite values
# e.g. A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead


# libs -----------------------------------------------
import requests
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import timedelta

# helper functions -----------------------------------
def convert_time(mm_ss):
    """Helper function to convert mm:ss times to numeric"""
    return int(mm_ss.split(":")[0]) + \
        int(mm_ss.split(":")[1])/60

def label_point(x, y, val, ax):
    """Helper function to add labels - assumes x axis is datetime (for Run Date)"""
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        # NOTE - assumes x axis is datetime - Run Date
        ax.text(point['x'] + timedelta(days = 4), point['y'], str(point['val']))


# class for athlete data -----------------------------
class Parkrunner():
    """ Scrapes athlete data from athlete_id and returns data and charts """

    def __init__(self, athlete_id):
        self.athlete_id = athlete_id

        # scrape athlete data
        self.raw_scraped = self.scrape_data()

        # collect tables and other info from scraped data
        self.tables = self.collect_tables(raw_results = self.raw_scraped)
        self.other_info = self.collect_other_info(raw_results = self.raw_scraped)


    # Data scraping / collecting ----
    def scrape_data(self):
        """ Scrape athlete data """
        parkrun_url = 'https://www.parkrun.com.au/parkrunner/'
        athlete_url = parkrun_url + self.athlete_id + '/all'

        page_all_results = requests.get(athlete_url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'})

        return page_all_results

    def collect_tables(self, raw_results):
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
            "all_results": 2
        }

        scraped_tables = {k: scraped_tables[v] for k, v in tables_map.items()}

        # clean tables
        all_results = scraped_tables['all_results']
        all_results['Run Date'] = pd.to_datetime(all_results['Run Date'], format="%d/%m/%Y")
        all_results['Time_numeric'] = all_results['Time'].apply(convert_time)
        all_results = all_results.sort_values('Run Date')

        # update with cleaned table
        scraped_tables['all_results'] = all_results

        return scraped_tables

    def collect_other_info(self, raw_results):

        """
        :param raw_results: Raw scraped output from self.scrape_data()
        :return: Dictionary of info such as athlete_name and number of parkruns
        """

        # scrape other info
        other_info_map = {
            # info : [string_search_start, string_search_end]
            "athlete_name": ["<h2>",
                             '\xa0<span style="font-weight: normal;" title="parkrun ID"'],
            "milestone_club": ["Member of the parkrun",
                               "Club"],
            "nbr_parkruns": ["<h3>\n",
                             "parkruns total"],
            "last_age_category": ["Most recent age category was ",
                                  "\n"]
        }

        other_info = {k: re.search(v[0] + '(.*)' + v[1], raw_results.text) \
                        .group(1) \
                        .strip() \
                      for k, v in other_info_map.items()}

        return other_info


    # Plot output ----
    def plot_finishing_times(self,
                             athlete = parkrunner.other_info['athlete_name'],
                             filter_parkrun = None,
                             show_num_events = 50):

        """
        Note - Expects Run Date to be datetime and Time_numeric column to be created
        :param athlete: athlete id or name to plot in title of chart
        :param show_num_events: number of events (points) to show in chart
        :param filter_parkrun: name of parkrun event to filter to
        :return: Plot of parkrun finish times over all events from all_results table
        """

        df = self.tables['all_results']

        # filter parkrun before PBs so PBs are for specific parkrun
        if filter_parkrun is not None:
            df = df[df.Event == filter_parkrun]

        # required calcs
        df['PB_times'] = df['Time'] \
            [(df['Time_numeric'] == df['Time_numeric'].cummin())]
        df['PB_times_numeric'] = df['Time_numeric'] \
            [(df['Time_numeric'] == df['Time_numeric'].cummin())]

        # subset after PB calcs
        df = df.tail(show_num_events)

        # build plot
        sns.lineplot(x="Run Date", y="Time_numeric", data=df,
                     linewidth=1.5, linestyle='--',
                     color='grey', legend=False)
        sns.scatterplot(x='Run Date', y='PB_times_numeric', data=df,
                        s=120, facecolor='white', edgecolor='black', linewidth=1.5)
        sns.scatterplot(x='Run Date', y='Time_numeric', data=df,
                        hue='Event', s=80, ec=None)
        label_point(df['Run Date'], df['PB_times_numeric'], df['PB_times'], plt.gca())

        plt.xlabel('Run date')
        plt.ylabel('Finishing time (mins)')
        plt.legend(title='Event location')
        plt.title(f"Parkrun finish times for {athlete}")
        ax = plt.gca()
        ax.set_ylim(ax.get_ylim()[::-1])

        return plt #, df
# END Parkrun class


# test  --------------------------------------------

athlete_id = '7417035'
parkrunner = Parkrunner(athlete_id)

print(parkrunner.tables)
print(parkrunner.other_info)

parkrunner.plot_finishing_times(
    show_num_events = 25,
    filter_parkrun = 'Rhodes'
)




