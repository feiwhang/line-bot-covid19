import csv
import json
import base64
import numpy as np
import pandas as pd
from io import BytesIO
from string import capwords
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from urllib.request import Request, urlopen


def parser(url):

    headers = {'User-Agent': 'Mozilla/5.0',
               'Referer': 'https://covid19.workpointnews.com/?to=THAILAND'}
    req = Request(url, headers=headers)

    # open up connection, grap the page
    uClient = urlopen(req)
    page_html = uClient.read()
    uClient.close()  # close connection

    # load data to json format for easy accessing
    page_json = json.loads(page_html)
    return page_json


def getCasesData():
    url = "https://covid19.workpointnews.com/api/cases"

    json = parser(url)

    data = {'Number': [], 'Age': [], 'Gender': [],
            'Job': [], 'Origin': [], 'Type': [],
            'Status': [], 'Date': []}

    for case in json:
        data['Number'].append(case['number'])
        data['Age'].append(case['age'])
        data['Gender'].append(case['gender'])
        data['Job'].append(case['job'])
        data['Origin'].append(case['origin'])
        data['Type'].append(case['type'])
        data['Status'].append(case['status'])
        data['Date'].append(case['statementDate'])

    df = pd.DataFrame(data)  # convert to a dataframe
    # convert float to int + fill age with 0 for None
    df.iloc[:, [1]] = df.iloc[:, [1]].fillna(0).astype(int)

    return df


def getWorldData():
    url = "https://covid19.workpointnews.com/api/world"

    json = parser(url)

    data = {'Country': [], 'Confirmed': [], 'Recovered': [],
            'Death': [], 'Travel': []}

    for country in json['statistics']:
        if len(country['name']) > 15:  # length control
            continue
        data['Country'].append(country['name'])
        data['Confirmed'].append(country['confirmed'])
        data['Recovered'].append(country['recovered'])
        data['Death'].append(country['deaths'])
        data['Travel'].append(country['travel'])

    df = pd.DataFrame(data)  # convert to a dataframe
    # set Country as an index
    df.set_index('Country', inplace=True)
    # remove Country with no data
    df.dropna(axis=0, how='all', inplace=True)
    # Set index back to place
    df.reset_index(inplace=True)
    # convert float to int
    df.iloc[:, [1, 2, 3]] = df.iloc[:, [1, 2, 3]].astype(int)

    return df


def writeCSV(mode):
    if mode == 'cases':
        df = getCasesData()
    elif mode == 'world':
        df = getWorldData()
    else:
        print("Wrong Mode")
        raise Exception

    # write to csv file
    csv = df.to_csv(index=False)
    with open('files/' + mode + '.csv', 'w') as fp:
        fp.write(csv)

    # write a timestamp of the file created
    with open('files/' + mode + 'LastUpdate.txt', 'w') as fp:
        fp.write(str(datetime.utcnow()))


def getWorldHTML():
    # write a timestamp of last get data
    with open('files/worldLastUpdate.txt', 'r') as fp:
        timestamp = fp.read()

    now = datetime.utcnow()
    lastUpdate = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    differ = now - lastUpdate

    # write new dataframe when more than 15 mins
    if differ.seconds > 15 * 60:
        writeCSV('world')

    # read csv to get data
    try:
        df = pd.read_csv('files/world.csv', index_col=False)
    except FileNotFoundError:  # write again if not found
        writeCSV('world')
        df = pd.read_csv('files/world.csv', index_col=False)

    df = df.fillna('')  # fill na with blank instead
    # Sort by Confirmed Cases
    df.sort_values(by='Confirmed', ascending=False,
                   inplace=True, ignore_index=True)

    # make index start at 1
    df.index += 1
    df.index.name = 'Rank'
    df.reset_index(level=0, inplace=True)  # make Rank as one of the columns

    # set style
    fontSize = '24pt'
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': fontSize,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', fontSize)]}])\
        .background_gradient(cmap='Reds')

    return '<meta charset="UTF-8">' + df.hide_index().render()


def getCasesHTML():
    # write a timestamp of last get data
    with open('files/casesLastUpdate.txt', 'r') as fp:
        timestamp = fp.read()

    now = datetime.utcnow()
    lastUpdate = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    differ = now - lastUpdate

    # write new dataframe when more than 15 mins
    if differ.seconds > 15 * 60:
        writeCSV('cases')

    # read csv to get data
    try:
        df = pd.read_csv('files/cases.csv', index_col=False)
    except FileNotFoundError:  # write again if not found
        writeCSV('cases')
        df = pd.read_csv('files/cases.csv', index_col=False)

    df = df.fillna('-')  # fill na with blank instead
    # Sort by Confirmed Cases
    df.sort_values(by='Number', ascending=False,
                   inplace=True, ignore_index=True)

    # Summary of Thailand
    thai_json = parser("https://covid19.workpointnews.com/api/constants")
    recovered = thai_json['หายแล้ว']
    death = thai_json['เสียชีวิต']
    added = thai_json['เพิ่มวันนี้']
    hospitolized = thai_json['กำลังรักษา']
    confirmed = thai_json['ผู้ติดเชื้อ']
    update = thai_json['เพิ่มวันที่']
    summaryThai = '<h1> ผู้ติดเชื้อ: ' + confirmed + \
        ' ,   กำลังรักษา: ' + hospitolized + ' ,   หายแล้ว: ' + \
        recovered + ' ,   เสียชีวิต: ' + death + ' ,   อัพเดท: ' + update + '</h1>'

    # set style
    fontSize = '20pt'
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'green',
                                    'font-size': fontSize,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', fontSize)]}])\
        .background_gradient(cmap='Reds')

    return '<meta charset="UTF-8">' + summaryThai + df.hide_index().render()


def writeTimeSeries():
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)

    # open up connection, grap the page
    uClient = urlopen(req)
    page_csv = uClient.read().decode('utf-8').replace('Korea, South',
                                                      'South Korea').replace('Taiwan*', 'Taiwan')
    uClient.close()  # close connection

    now = datetime.utcnow()

    # try to get timestamp of the last update
    try:
        # write a timestamp of last get data
        with open('files/timeSeriesLastUpdate.txt', 'r') as fp:
            timestamp = fp.read()
        with open('files/timeseries.csv', 'r') as fp:
            pass
    except FileNotFoundError:  # never init any timeSeries file
        with open('files/timeSeriesLastUpdate.txt', 'w') as fp:
            fp.write(str(now))
            timestamp = str(now)
        with open('files/timeseries.csv', 'w') as fp:
            fp.write(page_csv)

    lastUpdate = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    differ = now - lastUpdate

    # write new dataframe when more than 1 hour
    if differ.seconds > 60 * 60 * 1:
        with open('files/timeseries.csv', 'w') as fp:
            fp.write(page_csv)
        with open('files/timeSeriesLastUpdate.txt', 'w') as fp:
            fp.write(str(now))


def getTimeSeriesPlot(country):
    # Caplitalize country params from url
    country = capwords(country)
    try:
        df = pd.read_csv('files/timeseries.csv', index_col=1)
    except FileNotFoundError:
        writeTimeSeries()
        df = pd.read_csv('files/timeseries.csv', index_col=1)

    df = df.drop(columns=['Province/State', 'Lat', 'Long'])

    try:  # country appear only 1 in df
        ct = df.loc[country, :].to_frame()
        ct.index.name = 'Date'
        ct = ct.reset_index()
        ct['Date'] = pd.to_datetime(ct['Date'])
        date = ct['Date'].to_list()
        case = ct[country].to_list()

    except AttributeError:  # appear more than 1
        ct = df.loc[country, :]
        ct = ct.reset_index()

        aggregation_functions = {}
        for col in ct.columns[1:]:
            aggregation_functions[col] = 'sum'
        ct = ct.groupby(ct['Country/Region']).aggregate(aggregation_functions)

        date = pd.to_datetime(ct.columns)
        case = ct.loc[country, :].to_list()

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(date, case, linewidth=5)
    ax.set_ylabel('Cases', fontsize=25, labelpad=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=20)

    # format the Date axis
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # save to html
    tmp = BytesIO()
    plt.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')

    return encoded


def getCountryPage(country):
    try:
        allDF = pd.read_csv('files/world.csv', index_col=0)
    except FileNotFoundError:
        writeCSV('world')
        allDF = pd.read_csv('files/world.csv', index_col=0)

    country = capwords(country)

    df = allDF.loc[country, :].to_frame()
    # remove travel row if NaN
    df.dropna(axis=0, how='any', inplace=True)

    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': 110,
                                    'background-color': 'lightblue',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', 110)]}])\
        .background_gradient(cmap='Blues')

    # add time series plot
    page_html = df.render()
    page_html += "<img src=\'data:image/png;base64,{}\'> ".format(
        getTimeSeriesPlot(country))
    return '<meta charset="UTF-8">' + page_html
