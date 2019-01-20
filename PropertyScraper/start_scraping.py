from PropertyScraper.spiders import olx_spider_main
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

urls_OLX = [
    'https://www.olx.pl/nieruchomosci/mieszkania/poznan/',
]

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(olx_spider_main.OlxSpiderMain, urls_to_scrape = urls_OLX)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished
