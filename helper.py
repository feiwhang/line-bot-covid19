from scraper import scraper


def getPage(mode):
    sc = scraper(mode)
    return sc.getHTML()
