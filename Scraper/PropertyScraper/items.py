import scrapy
from scrapy.item import BaseItem
from schemas import offer_scheme

OfferItem = type('OfferItem', (dict, BaseItem), dict([(x,scrapy.Field()) for x in offer_scheme.keys()]))
OfferRoomItem = type('OfferRoomItem', (dict, BaseItem), dict([(x,scrapy.Field()) for x in offer_scheme.keys()]))