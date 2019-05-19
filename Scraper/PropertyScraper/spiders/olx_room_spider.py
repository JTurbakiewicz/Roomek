import scrapy
from items import OfferRoomItem
from items import OfferFeaturesItem
from itemloaders import OlxRoomLoader, OtodomOfferLoader
from scrapy.linkextractors import LinkExtractor
import Databases.mysql_connection as db

already_scraped_urls_dicts = db.get_all(table_name = 'offers', fields_to_get = 'offer_url')
already_scraped_urls = []
for url in already_scraped_urls_dicts:
    already_scraped_urls.append(url['offer_url'])

OLX_extractor_subpage = LinkExtractor(allow=('olx.pl/oferta/'), deny=(';promoted'), unique=True)
OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=23|page=33'), unique=True,
                                    restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
                                                      '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a']))
links_to_main_page = set()
links_to_olx_offers = set()


class OlxRoomSpider(scrapy.Spider):
    name = "olx_room_spider"
    urls = []

    def __init__(self, category=None, *args, **kwargs):
        super(OlxRoomSpider, self).__init__(*args, **kwargs)
        try:
            self.urls = kwargs['urls_to_scrape']
        except:
            pass

    def start_requests(self):
        for url in self.urls:
            request = scrapy.Request(url=url, callback=self.parse_initial_page)
            request.meta['housing_type'] = url.split('/')[-3]
            request.meta['city'] = url.split('/')[-2]
            yield request

    def parse_initial_page(self, response):
        next_page_links = OLX_main_page_extractor_next_page.extract_links(response)
        for link in next_page_links:
            links_to_main_page.add(link.url)
            if link is not None and link.url:
                request = scrapy.Request(link.url, callback=self.parse_main_pages)
                request.meta['housing_type'] = response.meta['housing_type']
                request.meta['city'] = response.meta['city']
                yield request

        olx_offer_links = OLX_extractor_subpage.extract_links(response)

        for link in olx_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_olx_offers:
                links_to_olx_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                    request.meta['housing_type'] = response.meta['housing_type']
                    request.meta['city'] = response.meta['city']
                    yield request

    def parse_olx_offer(self, response):
        OfferRI_loader = OlxRoomLoader(item=OfferRoomItem(), response=response)
        OfferFeaturesItem_loader = OtodomOfferLoader(item=OfferFeaturesItem(), response=response)
        OfferFeaturesItem_loader.add_value('offer_url', response)
        OfferRI_loader.add_value('city', response.meta['city'])
        OfferRI_loader.add_value('housing_type', response.meta['housing_type'])
        OfferRI_loader.add_value('offer_url', response)
        OfferRI_loader.add_value('business_type', 'wynajem')
        OfferRI_loader.add_xpath('offer_thumbnail_url', '//*[@id="photo-gallery-opener"]/img')
        OfferRI_loader.add_xpath('offer_name', '//*[@id="offerdescription"]/div[2]/h1/text()')
        OfferRI_loader.add_xpath('price', '//*[@id="offeractions"]/div[1]/strong/text()')
        OfferRI_loader.add_xpath('district', '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()')
        OfferRI_loader.add_xpath('date_of_the_offer', '//*[@id="offerdescription"]/div[2]/div[1]/em')
        OfferRI_loader.add_xpath('offer_id', '//*[@id="offerdescription"]/div[2]/div[1]/em/small/text()')
        OfferRI_loader.add_xpath('offer_text', '//*[@id="textContent"]')

        ###OLXtable

        OLX_table_fields = {
            'Oferta od': 'offer_from',
            'Umeblowane': 'furniture',
            'Rodzaj pokoju': 'type_of_room',
            'Preferowani': 'preferred_locator',
        }

        for column in range (1,5):
            for row in range (1,3):
                field_name = response.xpath(r'//*[@id="offerdescription"]/div[3]/table/tr[{}]/td[{}]/table/tr/th/text()'.format(column,row)).extract_first()
                if field_name is not None:
                    OfferRI_loader.add_xpath(OLX_table_fields[field_name], r'//*[@id="offerdescription"]/div[3]/table/tr[{}]/td[{}]/table/tr/td/strong'.format(column,row))

        OfferRI_item = OfferRI_loader.load_item()
        OfferFeaturesItem_item = OfferFeaturesItem_loader.load_item()

        yield OfferRI_item
        yield OfferFeaturesItem_item
