import scrapy
from itemloaders import OlxOfferLoader
from items import OLXOfferItem
from scrapy.linkextractors import LinkExtractor
import PropertyScraper_mysql_connection as db


already_scraped_urls = db.get_all('offer_url')
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
            request = scrapy.Request(url=url, callback=self.parse_initial_page)
            request.meta['offer_type'] = url.split('/')[-3]
            request.meta['city'] = url.split('/')[-2]
            yield request

    def parse_initial_page(self, response):
        next_page_links = OLX_main_page_extractor_next_page.extract_links(response)
        for link in next_page_links:
            links_to_main_page.add(link.url)
            if link is not None and link.url:
                request = scrapy.Request(link.url, callback=self.parse_main_pages)
                request.meta['offer_type'] = response.meta['offer_type']
                request.meta['city'] = response.meta['city']
                yield request

        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            links_to_olx_offers.add(link.url)
            if link is not None:
                request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                request.meta['offer_type'] = response.meta['offer_type']
                request.meta['city'] = response.meta['city']
                yield request

    def parse_main_pages(self, response):
        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            links_to_olx_offers.add(link.url)
            if link is not None:
                request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                request.meta['offer_type'] = response.meta['offer_type']
                request.meta['city'] = response.meta['city']
                yield request

    def parse_olx_offer(self, response):
        if response.url not in already_scraped_urls:
            loader = OlxOfferLoader(item=OLXOfferItem(), response=response)
            loader.add_value('city', response.meta['city'])
            loader.add_value('offer_type', response.meta['offer_type'])
            loader.add_value('offer_url', response)
            loader.add_xpath('offer_name', '//*[@id="offerdescription"]/div[2]/h1/text()')
            loader.add_xpath('price', '//*[@id="offeractions"]/div[1]/strong/text()')
            loader.add_xpath('offer_location', '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()')
            loader.add_xpath('date_of_the_offer', '//*[@id="offerdescription"]/div[2]/div[1]/em')
            loader.add_xpath('offer_id', '//*[@id="offerdescription"]/div[2]/div[1]/em/small/text()')
            loader.add_xpath('offer_text', '//*[@id="textContent"]')

            ###OLXtable

            OLX_table_fields = {
                'Oferta od': 'offer_from',
                'Poziom': 'apartment_level',
                'Umeblowane': 'furniture',
                'Rodzaj zabudowy': 'type_of_building',
                'Powierzchnia': 'area',
                'Liczba pokoi': 'amount_of_rooms',
                'Czynsz (dodatkowo)': 'additional_rent',
                'Cena za m²': 'price_per_m2',
                'Rynek': 'type_of_market',
            }
            for column in range (1,5):
                for row in range (1,3):
                    field_name = response.xpath(r'//*[@id="offerdescription"]/div[3]/table/tr[{}]/td[{}]/table/tr/th/text()'.format(column,row)).extract_first()
                    if field_name is not None:
                        loader.add_xpath(OLX_table_fields[field_name], r'//*[@id="offerdescription"]/div[3]/table/tr[{}]/td[{}]/table/tr/td/strong'.format(column,row))
            ###/OLXtable

            item = loader.load_item()
            # print (item)
            yield item
