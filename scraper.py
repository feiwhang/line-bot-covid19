import json
import matplotlib
import numpy as np
import pandas as pd
from datetime import datetime
from urllib.request import Request, urlopen


class scraper:
    def __init__(self, mode):
        self.mode = mode
        if self.mode == 'country':
            self.data = {'Country': [], 'Confirmed': [], 'Deaths': [],
                         'Recovered': [], 'Active': []}
            self.url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Z7biAeD8PAkqgmWhxG2A/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true'
        elif self.mode == 'state':
            self.data = {'State': [], 'Country': [], 'Confirmed': [], 'Deaths': [],
                         'Recovered': [], 'Active': []}
            self.url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Z7biAeD8PAkqgmWhxG2A/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)%20AND%20(Recovered%3C%3E0)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Recovered%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&resultOffset=0&resultRecordCount=250&cacheHint=true'

        else:
            raise Exception

    def parser(self):
        headers = {'User-Agent': 'Mozilla/5.0',
                   'Origin': 'https://www.arcgis.com',
                   'Referer': 'https://www.arcgis.com/apps/opsdashboard/index.html'}
        req = Request(self.url, headers=headers)

        # open up connection, grap the page
        uClient = urlopen(req)
        page_html = uClient.read()
        uClient.close()  # close connection

        # load data to json format for easy accessing
        page = json.loads(page_html)
        return page

    def getData(self):

        page = self.parser()  # select mode country

        data = self.data

        for feature in page['features']:
            country = feature['attributes']['Country_Region']
            # some special cases
            if country == 'Korea, South':
                country = 'South Korea'
            if country == 'Taiwan*':
                country = 'Taiwan'
            confirmed = feature['attributes']['Confirmed']
            deaths = feature['attributes']['Deaths']
            recovered = feature['attributes']['Recovered']
            active = feature['attributes']['Active']

            # crate new row & add to data list
            data['Country'].append(country)
            data['Confirmed'].append(confirmed)
            data['Deaths'].append(deaths)
            data['Recovered'].append(recovered)
            data['Active'].append(active)

            # for state mode
            if self.mode == 'state':
                state = feature['attributes']['Province_State']
                if state == None:
                    state = ''
                data['State'].append(state)
        return data

    def writeDF(self):
        # write a timestamp of last get data
        with open('files/lastUpdate.txt', 'w') as fp:
            fp.write(str(datetime.utcnow()))

        data = self.getData()
        df = pd.DataFrame(data=data)

        # write to csv
        df.to_csv('files/' + self.mode + '.csv', index=False)

    def getHTML(self):
        # write a timestamp of last get data
        with open('files/lastUpdate.txt', 'r') as fp:
            timestamp = fp.read()

        now = datetime.utcnow()
        lastUpdate = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        differ = now - lastUpdate

        # write new dataframe when more than 15 mins
        if differ.seconds > 15 * 60:
            self.writeDF()

        # read csv to get data
        try:
            df = pd.read_csv('files/' + self.mode+'.csv', index_col=False)
        except FileNotFoundError:
            self.writeDF()
            df = pd.read_csv('files/' + self.mode+'.csv', index_col=False)

        # make index start at 1
        df.index += 1
        df.index.name = 'Rank'
        df = df.fillna('')  # fill with blank instead

        # adjust font for each mode
        if self.mode == 'state':
            fontSize = '22pt'
        else:
            fontSize = '24pt'

        # set style
        df = df.style.set_properties(**{'text-align': 'center',
                                        'border-color': 'black',
                                        'font-size': fontSize,
                                        'background-color': 'lightyellow',
                                        'color': 'black'})\
            .set_table_styles([{'selector': 'th', 'props': [('font-size', fontSize)]}])\
            .background_gradient(cmap='Reds')
        return df.render()
