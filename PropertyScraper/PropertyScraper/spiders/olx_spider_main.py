import scrapy
import re
from itemloaders import OlxOfferLoader, OtodomOfferLoader
from items import OfferItem
from items import OfferFeaturesItem
from scrapy.linkextractors import LinkExtractor
import PropertyScraper_mysql_connection as db
from util import offer_features, offer_data


already_scraped_urls_dicts = db.get_all('offer_url')
already_scraped_urls = []
for url in already_scraped_urls_dicts:
    already_scraped_urls.append(url['offer_url'])

OLX_extractor_subpage = LinkExtractor(allow=('olx.pl/oferta/'), deny=(';promoted'), unique=True)
OLX_extractor_otodom = LinkExtractor(allow=('otodom'), deny=(';promoted'), unique=True)
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
links_to_otodom_offers = set()

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
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_olx_offers:
                links_to_olx_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                    request.meta['offer_type'] = response.meta['offer_type']
                    request.meta['city'] = response.meta['city']
                    yield request

        otodom_offer_links = OLX_extractor_otodom.extract_links(response)
        for link in otodom_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_otodom_offers:
                links_to_otodom_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_otodom_offer)
                    request.meta['offer_type'] = response.meta['offer_type']
                    request.meta['city'] = response.meta['city']
                    yield request

    def parse_main_pages(self, response):
        olx_offer_links = OLX_extractor_subpage.extract_links(response)
        for link in olx_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_olx_offers:
                links_to_olx_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_olx_offer)
                    request.meta['offer_type'] = response.meta['offer_type']
                    request.meta['city'] = response.meta['city']
                    yield request

        otodom_offer_links = OLX_extractor_otodom.extract_links(response)
        for link in otodom_offer_links:
            if link.url.split('#')[0] not in already_scraped_urls and link.url.split('#')[0] not in links_to_otodom_offers:
                links_to_otodom_offers.add(link.url)
                if link is not None:
                    request = scrapy.Request(link.url, callback=self.parse_otodom_offer)
                    request.meta['offer_type'] = response.meta['offer_type']
                    request.meta['city'] = response.meta['city']
                    yield request

    def parse_olx_offer(self, response):
        OfferItem_loader = OlxOfferLoader(item=OfferItem(), response=response)
        OfferFeaturesItem_loader = OtodomOfferLoader(item=OfferFeaturesItem(), response=response)
        OfferFeaturesItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_value('city', response.meta['city'])
        OfferItem_loader.add_value('offer_type', response.meta['offer_type'])
        OfferItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_xpath('offer_thumbnail_url', '//*[@id="photo-gallery-opener"]/img')
        OfferItem_loader.add_xpath('offer_name', '//*[@id="offerdescription"]/div[2]/h1/text()')
        OfferItem_loader.add_xpath('price', '//*[@id="offeractions"]/div[1]/strong/text()')
        OfferItem_loader.add_xpath('district', '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()')
        OfferItem_loader.add_xpath('date_of_the_offer', '//*[@id="offerdescription"]/div[2]/div[1]/em')
        OfferItem_loader.add_xpath('offer_id', '//*[@id="offerdescription"]/div[2]/div[1]/em/small/text()')
        OfferItem_loader.add_xpath('offer_text', '//*[@id="textContent"]')

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
                    OfferItem_loader.add_xpath(OLX_table_fields[field_name], r'//*[@id="offerdescription"]/div[3]/table/tr[{}]/td[{}]/table/tr/td/strong'.format(column,row))
        ###/OLXtable

        OfferItem_item = OfferItem_loader.load_item()
        OfferFeaturesItem_item = OfferFeaturesItem_loader.load_item()
        yield OfferItem_item
        yield OfferFeaturesItem_item

    def parse_otodom_offer(self, response):
        OfferItem_loader = OtodomOfferLoader(item=OfferItem(), response=response)
        OfferFeaturesItem_loader = OtodomOfferLoader(item=OfferFeaturesItem(), response=response)
        OfferFeaturesItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_value('city', response.meta['city'])
        OfferItem_loader.add_value('offer_type', response.meta['offer_type'])
        OfferItem_loader.add_value('offer_url', response)
        OfferItem_loader.add_xpath('offer_name', '//*[@id="root"]/div/article/header/div[1]/h1/text()')
        OfferItem_loader.add_xpath('offer_thumbnail_url', '//*[@id="root"]/div/article/section/div[1]/div/div[1]/div/div[2]/div/div[2]/div/picture/img')
        OfferItem_loader.add_xpath('price', '//*[@id="root"]/div/article/header/div[3]/div[1]/text()')
        OfferItem_loader.add_xpath('date_of_the_offer', '//*[@id="root"]/div/article/div[2]/div[1]/div[2]/div/div[2]/text()[2]')
        OfferItem_loader.add_xpath('offer_id', '//*[@id="root"]/div/article/div[2]/div[1]/div[2]/div/div[1]/text()[1]')
        OfferItem_loader.add_xpath('offer_text', '//*[@id="root"]/div/article/div[2]/div[1]/section[2]/div/div[1]')
        OfferItem_loader.add_xpath('price_per_m2', '//*[@id="root"]/div/article/header/div[3]/div[2]/text()')
        OfferItem_loader.add_xpath('area', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[2]/span/strong/text()')
        OfferItem_loader.add_xpath('amount_of_rooms', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[3]/span/strong/text()')
        OfferItem_loader.add_xpath('apartment_level', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[4]/span/strong/text()')
        OfferItem_loader.add_xpath('district', '//*[@id="root"]/div/article/header/div[1]/div/a/text()')

        ###Otodometable

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

        Otodom_table1 = response.xpath(r'//*[@id="root"]/div/article/div[2]/div[1]/section[1]/div/ul/li').getall()
        for line in Otodom_table1:
            line = re.sub(r'<.*?>', '', line).split(':')
            OfferItem_loader.add_value(Otodom_table_fields[line[0]], line[1][1:])

        Otodom_table2 = response.xpath(r'//*[@id="root"]/div/article/div[2]/div[1]/section[3]/div/ul/li').getall()

        for line in Otodom_table2:
            line = re.sub(r'<.*?>', '', line).split(':')[0].lower()
            if line == 'meble':
                OfferItem_loader.add_value('furniture', 'Tak')
            elif line == 'wynajmę również studentom':
                OfferItem_loader.add_value('rental_for_students', 'Tak')
            elif line in offer_features:
                OfferFeaturesItem_loader.add_value(offer_features[line], True)
            else:
                print ('DODAC ' + line)

        OfferItem_item = OfferItem_loader.load_item()
        OfferFeaturesItem_item = OfferFeaturesItem_loader.load_item()

        yield OfferItem_item
        yield OfferFeaturesItem_item

