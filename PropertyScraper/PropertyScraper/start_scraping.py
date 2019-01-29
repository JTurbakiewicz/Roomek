from spiders import olx_spider_main
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

urls_OLX = [
    'https://www.olx.pl/nieruchomosci/mieszkania/poznan/',
]
s = get_project_settings()
configure_logging()
runner = CrawlerRunner(s)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(olx_spider_main.OlxSpiderMain, urls_to_scrape = urls_OLX)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished
