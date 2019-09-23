import scrapy
import re
from Scraper.PropertyScraper.itemloaders import OtodomOfferLoader
from Scraper.PropertyScraper.items import OfferItem, OfferFeaturesItem
from Scraper.PropertyScraper.util import offer_features
from scrapy.linkextractors import LinkExtractor
import Databases.mysql_connection as db
from schemas import offer_scheme


def prepare_metadata(request, response):
    request.meta['housing_type'] = response.meta['housing_type']
    request.meta['city'] = response.meta['city']
    request.meta['business_type'] = response.meta['business_type']
    return request


already_scraped_urls_dicts = db.get_all(table_name='offers', fields_to_get='offer_url')
already_scraped_urls = [url['offer_url'] for url in already_scraped_urls_dicts]

OLX_extractor_otodom = LinkExtractor(allow=('otodom'), deny=(';promoted'), unique=True)
OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=23|page=33'), unique=True,
                                                  restrict_xpaths=(
                                                      ['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a']))
# OLX_main_page_extractor_next_page = LinkExtractor(allow=(r'page=2|page=3|page=4|page=5'), unique=True,
#                                     restrict_xpaths=(['//*[@id="body-container"]/div[3]/div/div[8]/span[3]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[4]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[5]/a',
#                                                       '//*[@id="body-container"]/div[3]/div/div[8]/span[6]/a']))

links_to_main_page = set()
links_to_otodom_offers = set()


class OtodomSpiderMain(scrapy.Spider):
    name = "otodom_spider_main"
    urls = []

    def __init__(self, *args, **kwargs):
        super(OtodomSpiderMain, self).__init__(*args, **kwargs)
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

        otodom_offer_links = OLX_extractor_otodom.extract_links(response)

        for link in otodom_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[
                0] not in links_to_otodom_offers:
                links_to_otodom_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_otodom_offer)
                    yield prepare_metadata(request, response)

    def parse_main_pages(self, response):
        otodom_offer_links = OLX_extractor_otodom.extract_links(response)
        for link in otodom_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[
                0] not in links_to_otodom_offers:
                links_to_otodom_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_otodom_offer)
                    yield prepare_metadata(request, response)

    def parse_otodom_offer(self, response):
        OfferItem_loader = OtodomOfferLoader(item=OfferItem(), response=response)
        OfferFeaturesItem_loader = OtodomOfferLoader(item=OfferFeaturesItem(), response=response)
        OfferFeaturesItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_value('city', response.meta['city'])
        OfferItem_loader.add_value('housing_type', response.meta['housing_type'])
        OfferItem_loader.add_value('business_type', response.meta['business_type'])
        OfferItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_value('date_of_the_offer', response.body)
        OfferItem_loader.add_value('location_latitude', response.body)
        OfferItem_loader.add_value('location_longitude', response.body)

        for field_name, field_value in offer_scheme.items():
            dict_value = field_value['scraping_path_otodom']
            if dict_value != '':
                OfferItem_loader.add_xpath(field_name, field_value['scraping_path_otodom'])

        Otodom_table_fields = {
            'Czynsz - dodatkowo': 'additional_rent',
            'Kaucja': 'security_deposit',
            'Rodzaj zabudowy': 'type_of_building',
            'Materiał budynku': 'building_material',
            'Okna': 'windows',
            'Ogrzewanie': 'heating',
            'Rok budowy': 'building_year',
            'Stan wykończenia': 'fit_out',
            'Dostępne od': 'ready_from',
            'Czynsz': 'additional_rent',
            'Forma własności': 'type_of_ownership',
            'Wynajmę również studentom': 'rental_for_students',
            'Rynek': 'type_of_market',
            'Wyposażenie': 'media',
            'Zabezpieczenia': 'security_measures',
            'Media': 'additonal_equipment',
            'Informacje dodatkowe': 'additional_information',
            'Powierzchnia': 'area',
            'Liczba pokoi': 'amount_of_rooms',
            'Piętro': 'apartment_level',
            'Liczba pięter': 'apartment_level',
        }

        Otodom_table1 = response.xpath(r'//*[@id="root"]/article/div[3]/div[1]/section[1]/div/ul/li').getall()
        for line in Otodom_table1:
            line = re.sub(r'<.*?>', '', line).split(':')
            OfferItem_loader.add_value(Otodom_table_fields[line[0]], line[1][1:])

        if response.xpath(r'//*[@id="root"]/div/article/div[3]/div[1]/section[4]/div/ul/li').getall():
            Otodom_table2 = response.xpath(r'//*[@id="root"]/div/article/div[3]/div[1]/section[4]/div/ul/li').getall()
        else:
            Otodom_table2 = response.xpath(r'//*[@id="root"]/div/article/div[3]/div[1]/section[3]/div/ul/li').getall()
        for line in Otodom_table2:
            line = re.sub(r'<.*?>', '', line).split(':')[0].lower()
            if line == 'meble':
                OfferItem_loader.add_value('furniture', 'Tak')
            elif line == 'wynajmę również studentom':
                OfferItem_loader.add_value('rental_for_students', True)
            elif line in offer_features:
                OfferFeaturesItem_loader.add_value(offer_features[line], True)
            else:
                print('DODAC ' + line)

        yield OfferItem_loader.load_item()
        yield OfferFeaturesItem_loader.load_item()
