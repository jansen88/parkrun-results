# Last updated: 2023-02-23


# libs ----
import requests
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from scipy import stats


# scrape athlete data ----
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


# visualise some of this ----

all_results = scraped_tables['all_results']

all_results['Run Date'] = pd.to_datetime(all_results['Run Date'], format = "%d/%m/%Y")

def convert_time(mm_ss):
    """Helper function to convert mm:ss times to numeric"""
    return int(mm_ss.split(":")[0]) + \
        int(mm_ss.split(":")[1])/60

all_results['Time'] = all_results['Time'].apply(convert_time)

# polyfit
y_vals = all_results['Time']
x_vals = np.linspace(0, 1, len(all_results['Time']))
# remove outliers - z-score >= 1
rm_outliers = np.abs(stats.zscore(y_vals) < 1)

z = np.polyfit(x = x_vals[rm_outliers], y = y_vals[rm_outliers], deg=1)
p = np.poly1d(z)
all_results['Time_trend'] = p(x_vals)

plt.plot(all_results['Run Date'], all_results['Time'],
         marker = '.',
         label = 'Recorded time')
plt.plot(all_results['Run Date'], all_results['Time_trend'],
         linestyle = '--',
         color = 'grey',
         label = 'Line of best fit')
plt.xlabel('Run date')
plt.ylabel('Finishing time')
plt.title(f"Parkrun finish times for {other_info['athlete_name']}")
ax = plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

