import json
import base64
import pandas as pd
from io import BytesIO
from scraper import scraper
from string import capwords
import matplotlib.pyplot as plt


def getPage(mode):
    sc = scraper(mode)
    return sc.getHTML()


def getTimeSeriesPlot(country):
    if country == 'us':
        country = 'US'
    if not country.isupper():
        country = capwords(country)

    sc = scraper('country')
    sc.writeTimeSeries()
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

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(date, case, linewidth=5)
    ax.set_xlabel('Date', fontsize=25)
    ax.set_ylabel('Cases', fontsize=25)
    plt.yticks(fontsize=18)

    # save to html
    tmp = BytesIO()
    plt.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')

    return encoded


def getCountryPage(country):
    allDF = pd.read_csv('files/country.csv', index_col=0)

    if country == 'us':
        country = 'US'
    if not country.isupper():
        country = capwords(country)

    df = allDF.loc[country, :].to_frame()
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': 110,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', 110)]}])\
        .background_gradient(cmap='Blues')
    # add plot
    page_html = df.render()
    page_html += "<img src=\'data:image/png;base64,{}\'> ".format(
        getTimeSeriesPlot(country))
    return page_html


def getStatePage(state):
    allDF = pd.read_csv('files/state.csv', index_col=0)
    del allDF['Country']

    if not state.isupper():
        state = capwords(state)

    df = allDF.loc[state, :].to_frame()
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': 110,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', 110)]}])\
        .background_gradient(cmap='Blues')
    return df.render()
