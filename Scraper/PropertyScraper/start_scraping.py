from spiders import olx_spider_main
from spiders import olx_room_spider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

base_string = 'https://www.olx.pl/nieruchomosci'
offer_types = ['mieszkania', 'stancje-pokoje']
#cities = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']
cities = ['warszawa']
urls_flats_OLX = []
urls_rooms_OLX = []

for type in offer_types:
    for city in cities:
        if type == 'mieszkania':
            urls_flats_OLX.append('/'.join([base_string,type,city,'']))
        elif type == 'stancje-pokoje':
            urls_rooms_OLX.append('/'.join([base_string, type, city, '']))

s = get_project_settings()
configure_logging()
runner = CrawlerRunner(s)

@defer.inlineCallbacks
def crawl():
    #yield runner.crawl(olx_room_spider.OlxRoomSpider, urls_to_scrape=urls_rooms_OLX)
    yield runner.crawl(olx_spider_main.OlxSpiderMain, urls_to_scrape = urls_flats_OLX)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished
