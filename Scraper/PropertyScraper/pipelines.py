from RatingEngine.scraped_ranker import initial_rating
import Databases.mysql_connection as db
from OfferParser.regex_parser import parse_offer


class Parse_Offer_Pipeline(object):
    def process_item(self, item, spider):
        try:
            item = parse_offer(item)
        except KeyError:
            pass
        return item


class MySQL_Offer_RatePipeline(object):
    def process_item(self, item, spider):
        item = initial_rating(item)
        return item


class MySQL_Offer_SQLPipeline(object):
    def process_item(self, item, spider):
        db.create_offer(item)
        return item
