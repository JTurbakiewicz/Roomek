from RatingEngine.scraped_ranker import initial_rating
import Databases.mysql_connection as db


class MySQL_OLXOffer_RatePipeline(object):
    def process_item(self, item, spider):
        item = initial_rating(item)
        return item


class MySQL_OLXOffer_SQLPipeline(object):
    def process_item(self, item, spider):
        db.create_offer(item)
        return item
