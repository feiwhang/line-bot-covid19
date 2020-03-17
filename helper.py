import json
import pandas as pd
from scraper import scraper


def getPage(mode):
    sc = scraper(mode)
    return sc.getHTML()


def writeJSON(mode):

    places = ['Thailand', 'China', 'Italy', 'Iran', 'Spain', 'South Korea', 'Germany', 'France',
              'US', 'Switzerland', 'United Kingdom', 'Japan', 'Malaysia', 'Canada', 'Australia',
              'Singapore',  'Philippines', 'Indonesia', 'India',
              'Russia', 'Taiwan', 'Vietnam', 'Cambodia', 'New Zealand']

    print(len(places))
    mainJSON = {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "Choose Country",
                    "size": "xxl",
                    "margin": "none",
                    "style": "normal",
                    "position": "relative",
                    "align": "center",
                    "gravity": "top",
                    "wrap": True,
                    "color": "#4D85F5"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": []
        }
    }
    for place in places:
        mainJSON['body']['contents'].append({
            "type": "button",
            "action": {
                "type": "message",
                "label": place,
                "text": place
            },
            "position": "relative",
            "style": "primary",
            "gravity": "center",
            "height": "sm",
            "margin": "xs"
        })

    with open('files/' + mode + '.json', 'w') as fp:
        json.dump(mainJSON, fp)


def getPic(place):
    pass


writeJSON('country')
