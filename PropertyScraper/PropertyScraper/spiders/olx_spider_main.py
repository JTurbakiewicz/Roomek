import scrapy
import re
from itemloaders import OlxOfferLoader, OtodomOfferLoader
from items import OfferItem
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
        loader = OlxOfferLoader(item=OfferItem(), response=response)
        loader.add_value('city', response.meta['city'])
        loader.add_value('offer_type', response.meta['offer_type'])
        loader.add_value('offer_url', response)
        loader.add_xpath('offer_thumbnail_url', '//*[@id="photo-gallery-opener"]/img')
        loader.add_xpath('offer_name', '//*[@id="offerdescription"]/div[2]/h1/text()')
        loader.add_xpath('price', '//*[@id="offeractions"]/div[1]/strong/text()')
        loader.add_xpath('district', '//*[@id="offerdescription"]/div[2]/div[1]/a/strong/text()')
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
        yield item

    def parse_otodom_offer(self, response):
        loader = OtodomOfferLoader(item=OfferItem(), response=response)
        loader.add_value('city', response.meta['city'])
        loader.add_value('offer_type', response.meta['offer_type'])
        loader.add_value('offer_url', response)
        loader.add_xpath('offer_name', '/html/body/div[1]/section[2]/div/div/header/h1/text()')
        loader.add_xpath('offer_thumbnail_url', '/html/body/div[1]/section[3]/div/div/div/div[2]')
        loader.add_xpath('price', '/html/body/div[1]/section[2]/div/div/div/div[1]/strong/text()')
        loader.add_xpath('date_of_the_offer', '/html/body/div[1]/section[11]/div/div/div/div/div[2]/p[2]/text()')
        loader.add_xpath('offer_id', '/html/body/div[1]/section[11]/div/div/div/div/div[1]/p[1]/text()')
        loader.add_xpath('offer_text', '/html/body/div[1]/section[7]/div/div/div/div/div/div[1]')
        loader.add_xpath('price_per_m2', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[1]/text()[2]')
        loader.add_xpath('area', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[2]/span/strong/text()')
        loader.add_xpath('amount_of_rooms', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[3]/span/strong/text()')
        loader.add_xpath('apartment_level', '/html/body/div[1]/section[6]/div/div/div/ul/li[1]/ul[1]/li[4]/span/strong/text()')

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
        }

        Otodom_table1 = response.xpath(r'/html[1]/body[1]/div[1]/section[6]/div[1]/div[1]/div[1]/ul[1]/li[1]/ul[2]/li').getall()
        for line in Otodom_table1:
            line = re.sub(r'<.*?>', '', line).split(':')
            loader.add_value(Otodom_table_fields[line[0]], line[1][1:])

        Otodom_table2 = response.xpath(r'/html/body/div[1]/section[6]/div/div/div/ul/li').getall()
        for ln in range(1,len(Otodom_table2)-1):
            line = re.sub(r'</ul>|</li>|<h4>|</h4>| <ul class="dotted-list">|\n', '', Otodom_table2[ln])
            line = re.sub(r' {2,}', ' ', line).split('<li>')
            loader.add_value(Otodom_table_fields[line[1].strip()], str(line[2:]))

        offer_location_response = response.xpath(r'/html/body/div[1]/section[2]/div/div/header/address/p[1]/a/text()').getall()
        loader.add_value('district', offer_location_response[3])
        if len(offer_location_response) == 5:
            loader.add_value('street', offer_location_response[4])

        item = loader.load_item()
        yield item

