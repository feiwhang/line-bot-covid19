import codecs
from scraper import scraper
from datetime import datetime


def writePage(mode):
    sc = scraper(mode)
    html = sc.getHTML()
    now = datetime.utcnow()
    # add time stamp at the end
    page = html + str(datetime.utcnow())

    with open('pages/' + mode + '.html', 'w') as fp:
        fp.write(page)


def getPage(mode):
    while True:
        try:
            now = datetime.utcnow()

            html = codecs.open('pages/' + mode + '.html', 'r').read()
            htmlTime = datetime.strptime(html[-26:], "%Y-%m-%d %H:%M:%S.%f")
            differ = now - htmlTime
            # throw exception when more than 15 mins
            if differ.seconds > 15 * 60:
                raise Exception

            return "Last Update = " + str(differ.seconds) + ' seconds ago' + html

        except NameError:
            return "Something's wrong with the name"
            break
        except IOError:
            print("file not found")
            writePage(mode)
            continue
        except Exception:
            writePage(mode)
            continue

        break


def getPlaces():
    stateScraper = scraper('state')
    states = list(filter(None, stateScraper.getData()['State']))

    countryScraper = scraper('country')
    countries = countryScraper.getData()['Country']

    places = states + countries
    return sorted(places)
