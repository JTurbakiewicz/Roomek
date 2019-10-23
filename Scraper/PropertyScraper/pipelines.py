from RatingEngine.scraped_ranker import initial_rating
import Databases.mysql_connection as db
from OfferParser.regex_parser import parse_offer
from Bot import geolocate
import logging


class Parse_Offer_Pipeline(object):
    def process_item(self, item, spider):
        try:
            item = parse_offer(item)
        except KeyError:
            pass
        return item


class Get_Location_Pipeline(object):
    def process_item(self, item, spider):
        lowest_location_level = ''
        try:
            city = item['city'][0]
        except KeyError:
            logging.ERROR('No city info in the offer')
        try:
            lowest_location_level = item['street'][0] if item['street'][0] is not None else ''
        except KeyError:
            pass
        if lowest_location_level:
            geolocate_data = geolocate.recognize_location(location=lowest_location_level, city=city)
            try:
                if not item['location_latitude']:
                    item['location_latitude'] = [float(geolocate_data['lat'])]
                if not item['location_longitude']:
                    item['location_longitude'] = [float(geolocate_data['lon'])]
            except KeyError:
                item['location_latitude'] = [float(geolocate_data['lat'])]
                item['location_longitude'] = [float(geolocate_data['lon'])]
        return item


class MySQL_Offer_RatePipeline(object):
    def process_item(self, item, spider):
        item = initial_rating(item)
        return item


class MySQL_Offer_SQLPipeline(object):
    def process_item(self, item, spider):
        db.create_offer(item)
        return item
