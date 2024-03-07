"""Functions to fetch data"""
import requests
import json
import pandas as pd

from parkrun.constants import events_url

def scrape_url(url):
    """Scrape target URL - return all"""
    # proxies = { 
    #     "http": 
    # }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    return(
        requests.get(
            url,
            # proxies=proxies,
            headers=headers
        )
    )


def get_parkrun_locations():
    """Scrape parkrun events json file from URL, then return df"""

    events_raw = scrape_url(events_url)
    events_dict = json.loads(events_raw.text)

    features = events_dict['events']['features']
    return features

    # parkrun_events = []
    # for entry in features:

    #     df = pd.DataFrame({
    #         "id": entry['id'],
    #         "type": entry['type'],
    #         "geometry_type": entry["geometry"]["type"],
    #         "lat": entry["geometry"]["coordinates"][0],
    #         "long": entry["geometry"]["coordinates"][1],
    #     }, index = [0])

    #     other_cols = pd.DataFrame(entry['properties'], index=[0])

    #     row = pd.concat([df, other_cols], axis=1)
    #     parkrun_events.append(row)

    # return pd.concat(parkrun_events, axis=0)