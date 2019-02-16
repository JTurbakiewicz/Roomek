import scrapy
from scrapy.item import BaseItem
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

class OfferItem(dict, BaseItem):
    city = scrapy.Field()
    offer_type = scrapy.Field()
    offer_url = scrapy.Field()
    offer_thumbnail_url = scrapy.Field()
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

    security_deposit = scrapy.Field()
    building_material = scrapy.Field()
    windows = scrapy.Field()
    heating = scrapy.Field()
    building_year = scrapy.Field()
    fit_out = scrapy.Field()
    ready_from = scrapy.Field()
    type_of_ownership = scrapy.Field()
    rental_for_students = scrapy.Field()

    media = scrapy.Field()
    security_measures = scrapy.Field()
    additonal_equipment = scrapy.Field()
    additional_information = scrapy.Field()