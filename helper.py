import json
import pandas as pd
from scraper import scraper
from string import capwords


def getPage(mode):
    sc = scraper(mode)
    return sc.getHTML()


def getCountryPage(country):
    allDF = pd.read_csv('files/country.csv', index_col=0)

    df = allDF.loc[capwords(country), :].to_frame()
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': 110,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', 110)]}])\
        .background_gradient(cmap='Blues')
    return df.render()


def getStatePage(state):
    allDF = pd.read_csv('files/state.csv', index_col=0)
    del allDF['Country']
    df = allDF.loc[capwords(state), :].to_frame()
    df = df.style.set_properties(**{'text-align': 'center',
                                    'border-color': 'black',
                                    'font-size': 110,
                                    'background-color': 'lightyellow',
                                    'color': 'black'})\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', 110)]}])\
        .background_gradient(cmap='Blues')
    return df.render()
