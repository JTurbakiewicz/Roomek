import scrapy
from scrapy.item import BaseItem
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

class OLXOfferItem(dict, BaseItem):
    offer_name = scrapy.Field()
    price = scrapy.Field()
    offer_location = scrapy.Field()
    date_of_the_offer = scrapy.Field()
    offer_id = scrapy.Field()
    offer_text = scrapy.Field()
