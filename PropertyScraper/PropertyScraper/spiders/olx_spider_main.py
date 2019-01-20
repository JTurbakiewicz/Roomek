import scrapy
from PropertyScraper.itemloaders import OlxOfferLoader
from PropertyScraper.items import OLXOfferItem
from scrapy.linkextractors import LinkExtractor

OLX_extractor_subpage = LinkExtractor(allow=('olx.pl/oferta'), deny=(';promoted'), unique=True)
OLX_extractor_otodom = LinkExtractor(allow=('otodom'), unique=True)
OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=23|page=33'), unique=True,
                                    restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
                                                      '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a']))
# OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=2|page=3'), unique=True,
#                                     restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a']))
links_to_main_page = set()
links_to_olx_offers = set()

class OlxSpiderMain(scrapy.Spider):
    name = "olx_spider_main"
    urls = []

    def __init__(self, category=None, *args, **kwargs):
        super(OlxSpiderMain, self).__init__(*args, **kwargs)
        try:
            self.urls = kwargs['urls_to_scrape']
        except:
            pass

    def start_requests(self):
        print (self.urls)
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_initial_page)

    def parse_initial_page(self, response):
        next_page_links = OLX_main_page_extractor_next_page.extract_links(response)
        for link in next_page_links:
            links_to_main_page.add(link.url)
            if link is not None and link.url:
                print (link.url)
                yield scrapy.Request(link.url, callback=self.parse_main_pages)

        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            links_to_olx_offers.add(link.url)
            if link is not None:
                yield scrapy.Request(link.url, callback=self.parse_olx_offer)

    def parse_main_pages(self, response):
        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            links_to_olx_offers.add(link.url)
            if link is not None:
                yield scrapy.Request(link.url, callback=self.parse_olx_offer)

    def parse_olx_offer(self, response):
        loader = OlxOfferLoader(item=OLXOfferItem(), response=response)
        loader.add_xpath('offer_name', '//*[@id="offerdescription"]/div[3]/table/tr[1]/td[1]/table/tr/td/strong/a/text()')
        loader.add_xpath('price', '//*[@id="offeractions"]/div[1]/strong/text()')
        loader.add_xpath('offer_location', '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()')
        loader.add_xpath('date_of_the_offer', '//*[@id="offerdescription"]/div[2]/div[1]/em/text()')
        loader.add_xpath('offer_id', '//*[@id="offerdescription"]/div[2]/div[1]/em/small/text()')
        loader.add_xpath('offer_text', '//*[@id="textContent"]/text()')
        item = loader.load_item()
        print (item)
        yield item