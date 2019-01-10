import olx_spider_main
import olx_spider_subpage
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
try:
    import cpickle as pickle
except:
    import pickle

urls = [
    'https://www.olx.pl/nieruchomosci/mieszkania/poznan/',
]

with open('urls_to_scrape.pickle', 'wb') as f:
    pickle.dump(urls, f)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(olx_spider_main.OlxSpiderMain)
    yield runner.crawl(olx_spider_subpage.OlxSpiderSub)
    reactor.stop()


crawl()
reactor.run()  # the script will block here until the last crawl call is finished
