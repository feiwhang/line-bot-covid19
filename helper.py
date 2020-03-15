from scraper import scraper


def statePage():
    stateScraper = scraper('state')
    html = stateScraper.getHTML()
    return html


def countryPage():
    countryScraper = scraper('country')
    html = countryScraper.getHTML()
    return html


def getPlaces():
    stateScraper = scraper('state')
    states = list(filter(None, stateScraper.getData()['State']))

    countryScraper = scraper('country')
    countries = countryScraper.getData()['Country']

    places = states + countries
    return sorted(places)
