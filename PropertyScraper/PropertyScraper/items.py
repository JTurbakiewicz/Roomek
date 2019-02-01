import scrapy
from scrapy.item import BaseItem
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

class OLXOfferItem(dict, BaseItem):
    city = scrapy.Field()
    offer_type = scrapy.Field()
    offer_url = scrapy.Field()
    offer_name = scrapy.Field()
    price = scrapy.Field()
    offer_location = scrapy.Field()
    date_of_the_offer = scrapy.Field()
    offer_id = scrapy.Field()
    offer_text = scrapy.Field()
    offer_from = scrapy.Field()
    apartment_level = scrapy.Field()
    furniture = scrapy.Field()
    type_of_building = scrapy.Field()
    area = scrapy.Field()
    amount_of_rooms = scrapy.Field()
    additional_rent = scrapy.Field()
    price_per_m2 = scrapy.Field()
    type_of_market = scrapy.Field()
