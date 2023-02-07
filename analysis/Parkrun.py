# Last updated: 2023-03-07


# libs -----------------------------------------------
import requests
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import timedelta


# helper functions ----------------------------------
def get_text_before_first_number(s):
    if not pd.isna(s):
        match = re.search(r'^\D+', s)
        if match:
            return match.group().strip()
    return np.nan

def get_number_before_parkruns(s):
    match = re.search(r'\d+\s+parkruns', s)
    if match:
        number_str = match.group().split()[0]
        return int(number_str)
    return 0

def get_age_group(s):
    """Helper function to extract age group from last results"""
    # handle na
    if pd.isna(s):
        return np.nan
    elif 'JM10' in s or 'JW10' in s:
        return s[:4]
    else:
        return s[:7]

def get_pb(s):
    """Helper function to extract PB from last results"""
    # handle na
    if pd.isna(s):
        return np.nan
    # new pb or first timer - take current time
    elif 'New PB!' in s or 'First Timer' in s:
        return s[:5]
    # otherwise, take existing PB
    else:
        return s[-5:]

def convert_time(mm_ss):
    """Helper function to convert mm:ss times to numeric"""
    if pd.isna(mm_ss):
        return np.nan
    else:
        return int(mm_ss.split(":")[0]) + \
               int(mm_ss.split(":")[1]) / 60


parkrun_url = 'https://www.parkrun.com.au/'
event_name = 'Rhodes'

# latest results -----------------------------------

latest_results_url = parkrun_url + event_name + '/results/latestresults/'

page_all_results = requests.get(latest_results_url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'})
results = pd.read_html(page_all_results.text)[0]

# Clean raw data
results = \
    results \
    .assign(
        # extract from results.parkrunner
        # e.g. 'John DOE245 parkruns | Male  1  | Member of the 100 Club  SM25-29 | 77.63%  CLUB'
        name = lambda x: x.parkrunner.apply(get_text_before_first_number),
        n_parkruns = lambda x: x.parkrunner.apply(get_number_before_parkruns),

        # extract from results.Gender
        # e.g. Female  127
        gender = lambda x: x.Gender.apply(get_text_before_first_number),
        gender_position = lambda x: x.Gender \
                                        .apply(lambda s: int(s.split()[-1]) if not pd.isna(s) else np.nan),

        # extract from results['Age Group']
        # e.g. SM25-2977.63% age grade
        full_age_group = lambda x: x['Age Group'].apply(get_age_group),
        age_group = lambda x: x.full_age_group.apply(lambda s: s[2:] if not pd.isna(s) else np.nan),
        age_grade = lambda x: x['Age Group'] \
                                .apply(lambda s: s[7:13] if not pd.isna(s) else np.nan),

        # extract from results.Time
        # e.g. 16:37PB15:58, 17:05New PB!
        # WARNING - assumes times xx:xx
        finish_time = lambda x: x.Time \
                                    .apply(lambda s: s[:5] if not pd.isna(s) else np.nan),
        curr_pb = lambda x: x.Time.apply(get_pb)
    ) \
    .rename(columns = {'Position': 'position',
                       'Club': 'club'}) \
    .loc[:, ['position', 'name', 'n_parkruns', 'gender', 'gender_position', 'club', 'full_age_group',
             'age_group', 'age_grade', 'finish_time', 'curr_pb']]

# Formatting
results['finish_time_numeric'] = results.finish_time.apply(convert_time)
results['curr_pb_numeric'] = results.curr_pb.apply(convert_time)


# plots -------------------------------

# plot times
def plot_dist_finish_times(df, by_gender = False):

    if by_gender == True:
        plot_data = df[~pd.isna(df.gender)]
        plot_hue = "gender"
    else:
        plot_data = results
        plot_hue = None

    sns.displot(plot_data,
                x = "finish_time_numeric",
                hue = plot_hue,
                # kind="kde", bw_adjust=2,
                kde = True,
                fill = True)
    plt.xlabel('Finishing time')
    plt.ylabel('Number of parkrunners')
    plt.title('Distribution of finishing times')
    plt.tight_layout()

    return plt

plot_dist_finish_times(results,
                  by_gender = True)


# boxplot of times
def plot_boxplot_finish_times(df, by = None):

    if by == "age_group":
        df = df[~pd.isna(df.age_group)]
        ylab = "Age group"
        sort_order = sorted(df.age_group.unique().astype('str'))
    elif by == "gender":
        df = df[~pd.isna(df.gender)]
        ylab = "Gender"
        sort_order = ['Male', 'Female']

    sns.boxplot(data = df,
            x = 'finish_time_numeric',
            y = by,
            order = sort_order
    )
    plt.xlabel('Finishing time')
    plt.ylabel(ylab)
    plt.title('Distribution of finishing times')
    plt.tight_layout()

    return plt

plot_boxplot_finish_times(results,
                          by = "age_group")


# performance vs pb -- scrapped, this doesn't work great if we can't get previous pb

# df['pb_diff'] = df.curr_pb_numeric - df.finish_time_numeric
# sns.scatterplot(data = df,
#                 x = 'finish_time_numeric',
#                 y = 'pb_diff')