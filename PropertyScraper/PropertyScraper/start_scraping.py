from spiders import olx_spider_main
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

base_string = 'https://www.olx.pl/nieruchomosci'
offer_types = ['mieszkania']
cities = ['poznan', 'warszawa', 'leszno', 'plewiska', 'lodz']

urls_OLX = []

for type in offer_types:
    for city in cities:
        urls_OLX.append('/'.join([base_string,type,city,'']))

# urls_OLX = [
#     'https://www.olx.pl/nieruchomosci/mieszkania/poznan/',
#     'https://www.olx.pl/nieruchomosci/mieszkania/warszawa/',
# ]
s = get_project_settings()
configure_logging()
runner = CrawlerRunner(s)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(olx_spider_main.OlxSpiderMain, urls_to_scrape = urls_OLX)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished
