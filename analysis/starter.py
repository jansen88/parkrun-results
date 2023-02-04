# Last updated: 2023-02-23


# libs -----------------------------------------------
import requests
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import timedelta


# scrape athlete data --------------------------------

# TODO - functionalise or make scraped data a class

parkrun_url = 'https://www.parkrun.com.au/parkrunner/'
athlete_id = '7417035'

athlete_url = parkrun_url + athlete_id + '/all'

page_all_results = requests.get(athlete_url, headers={
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'})

# scrape tables
scraped_tables = pd.read_html(page_all_results.text)
tables_map = {
    # table : table number (index)
    "summary_stats": 0,
    "annual_bests": 1,
    "all_results": 2
}
scraped_tables = {k: scraped_tables[v] for k, v in tables_map.items()}

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

other_info = {k: re.search(v[0] + '(.*)' + v[1], page_all_results.text) \
                    .group(1) \
                    .strip() \
              for k, v in other_info_map.items()}


# now let's visualise some of this


# Helper functions -------------------------------

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


# PLOT parkrun finish times ------------------------

def plot_finishing_times(df, athlete):

    """Plots parkrun finish times over all events, from all_results table.
       Expects Run Date to be datetime and Time_numeric column to be created"""
    # required calcs
    df['PB_times'] = df['Time'] \
        [(df['Time_numeric'] == df['Time_numeric'].cummin())]
    df['PB_times_numeric'] = df['Time_numeric'] \
        [(df['Time_numeric'] == df['Time_numeric'].cummin())]

    # build plot
    sns.lineplot(x="Run Date", y="Time_numeric", data=all_results,
                 linewidth=1.5, linestyle='--',
                 color='grey', legend=False)
    sns.scatterplot(x='Run Date', y='PB_times_numeric', data=all_results,
                    s=120, facecolor='white', edgecolor='black', linewidth=1.5)
    sns.scatterplot(x='Run Date', y='Time_numeric', data=all_results,
                    hue='Event', s=80, ec=None)
    label_point(df['Run Date'], df['PB_times_numeric'], df['PB_times'], plt.gca())

    plt.xlabel('Run date')
    plt.ylabel('Finishing time (mins)')
    plt.legend(title='Event location')
    plt.title(f"Parkrun finish times for {athlete}")
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])

    return plt

## test function

# get finishing times data
all_results = scraped_tables['all_results']

# format event dates and finishing times
all_results['Run Date'] = pd.to_datetime(all_results['Run Date'], format = "%d/%m/%Y")
all_results['Time_numeric'] = all_results['Time'].apply(convert_time)
all_results = all_results.sort_values('Run Date')

plot_finishing_times(all_results, other_info['athlete_name'])




