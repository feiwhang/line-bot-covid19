import codecs
from scraper import scraper
from datetime import datetime


def writePage(mode):
    sc = scraper(mode)
    html = sc.getHTML()
    now = datetime.utcnow()
    page = html + str(datetime.utcnow())

    with open('pages/' + mode + '.html', 'w') as fp:
        fp.write(page)


def getPlaces():
    stateScraper = scraper('state')
    states = list(filter(None, stateScraper.getData()['State']))

    countryScraper = scraper('country')
    countries = countryScraper.getData()['Country']

    places = states + countries
    return sorted(places)
