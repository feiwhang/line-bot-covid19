import json
import numpy as np
import pandas as pd
from dateutil import tz
from datetime import datetime
from urllib.request import Request, urlopen

from flask import Flask


app = Flask(__name__)


def get_data():
    url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Z7biAeD8PAkqgmWhxG2A/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true'

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    # open up connection, grap the page
    uClient = urlopen(req)
    page_html = uClient.read()
    uClient.close()  # close connection

    # load data to json format for easy accessing
    page = json.loads(page_html)

    # create a data list for numpy array
    data = []
    # Cumulative Total Count
    total_confirmed = 0
    total_death = 0
    total_recoverd = 0

    for feature in page['features']:
        country = feature['attributes']['Country_Region']
        confirmed = feature['attributes']['Confirmed']
        deaths = feature['attributes']['Deaths']
        recovered = feature['attributes']['Recovered']
        active = feature['attributes']['Active']
        # in Unix Timestamp 17 digits, in UTC
        lastupdate = feature['attributes']['Last_Update']
        # convert to normal datetime && to UTC+7
        date = datetime.fromtimestamp(lastupdate/1000)
        utc_zone = tz.gettz('UTC')
        th_zone = tz.gettz('Asia/Bangkok')
        date = date.replace(tzinfo=utc_zone)
        date = date.astimezone(th_zone)
        date = date.strftime("%d/%m/%Y, %H:%M")  # format for Thais

        total_confirmed += int(confirmed)
        total_death += int(deaths)
        total_recoverd += int(recovered)

        # crate new row & add to data list
        row = [country, confirmed, deaths, recovered, active, date]
        data.append(row)

    return data


def get_df():
    data = get_data()
    # create a dataframe
    data_head = ['Country', 'Confirmed', 'Deaths',
                 'Recovered', 'Active', 'Lastest Update']
    df = pd.DataFrame(np.array(data),
                      columns=data_head)
    df.index += 1
    df.index.name = 'Rank'
    return df


def get_html():
    df = get_df()
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black'})

    return df.render()
