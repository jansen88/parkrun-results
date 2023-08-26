"""Functions to fetch data"""
import requests
import json
import pandas as pd

from parkrun.constants import events_url

def scrape_url(url):
    """Scrape target URL - return all"""
    return(
        requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'
            }
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