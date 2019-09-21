from RatingEngine.scraped_ranker import initial_rating
import Databases.mysql_connection as db
from Witai import witai_connection as wit


class Parse_Offer_Pipeline(object):
    def process_item(self, item, spider):
        try:
            offer_text = item['offer_text']
            offer_name = item['offer_name']
            wit_response = wit.send_message(message=offer_name)
            print(wit_response.json())
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
