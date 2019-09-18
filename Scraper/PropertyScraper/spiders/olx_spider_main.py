import scrapy
from Scraper.PropertyScraper.itemloaders import OlxOfferLoader, OtodomOfferLoader
from Scraper.PropertyScraper.items import OfferItem, OfferFeaturesItem
from scrapy.linkextractors import LinkExtractor
import Databases.mysql_connection as db
from schemas import offer_scheme

def prepare_metadata(request, response):
    request.meta['housing_type'] = response.meta['housing_type']
    request.meta['city'] = response.meta['city']
    request.meta['business_type'] = response.meta['business_type']
    return request

already_scraped_urls_dicts = db.get_all(table_name = 'offers', fields_to_get = 'offer_url')
already_scraped_urls = [url['offer_url'] for url in already_scraped_urls_dicts]

OLX_extractor_subpage = LinkExtractor(allow=('olx.pl/oferta/'), deny=(';promoted'), unique=True)
OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=23|page=33'), unique=True,
                                    restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
                                                      '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a']))
# OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=2|page=3|page=4|page=5'), unique=True,
#                                     restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[5]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[6]/a']))

links_to_main_page = set()
links_to_olx_offers = set()

class OlxSpiderMain(scrapy.Spider):
    name = "olx_spider_main"
    urls = []

    def __init__(self, *args, **kwargs):
        super(OlxSpiderMain, self).__init__(*args, **kwargs)
        try:
            self.urls = kwargs['urls_to_scrape']
        except:
            pass

    def start_requests(self):
        for url in self.urls:
            request = scrapy.Request(url=url, callback=self.parse_initial_page)
            request.meta['housing_type'] = url.split('/')[-4]
            request.meta['business_type'] = url.split('/')[-3]
            request.meta['city'] = url.split('/')[-2]
            yield request

    def parse_initial_page(self, response):
        next_page_links = OLX_main_page_extractor_next_page.extract_links(response)
        for link in next_page_links:
            links_to_main_page.add(link.url)
            if link is not None:
                request = scrapy.Request(link.url, callback=self.parse_main_pages)
                yield prepare_metadata(request, response)

        olx_offer_links = OLX_extractor_subpage.extract_links(response)

        for link in olx_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_olx_offers:
                links_to_olx_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                    yield prepare_metadata(request, response)

    def parse_main_pages(self, response):
        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_olx_offers:
                links_to_olx_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                    yield prepare_metadata(request, response)

    def parse_olx_offer(self, response):
        OfferItem_loader = OlxOfferLoader(item=OfferItem(), response=response)
        OfferFeaturesItem_loader = OtodomOfferLoader(item=OfferFeaturesItem(), response=response)
        OfferFeaturesItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_value('city', response.meta['city'])
        OfferItem_loader.add_value('business_type', response.meta['business_type'])
        OfferItem_loader.add_value('housing_type', response.meta['housing_type'])
        OfferItem_loader.add_value('offer_url', response)

        for field_name, field_value in offer_scheme.items():
            dict_value = field_value['scraping_path_olx']
            if dict_value != '':
                OfferItem_loader.add_xpath(field_name, field_value['scraping_path_olx'])

        for column in range (1,5):
            for row in range (1,3):
                field = response.xpath(f'//*[@id="offerdescription"]/div[3]/table/tr[{column}]/td[{row}]/table/tr/th/text()').extract_first()
                if field is not None:
                    for field_name, field_value in offer_scheme.items():
                        if field in field_value['misc']:
                            OfferItem_loader.add_xpath(field_name, f'//*[@id="offerdescription"]/div[3]/table/tr[{column}]/td[{row}]/table/tr/td/strong')

        yield OfferItem_loader.load_item()
        yield OfferFeaturesItem_loader.load_item()
