import scrapy
from scrapy.item import BaseItem
from schemas import offer_scheme, offer_features_scheme

OfferItem = type('OfferItem', (dict, BaseItem), dict([(x,scrapy.Field()) for x in offer_scheme.keys()]))
OfferFeaturesItem = type('OfferFeaturesItem', (dict, BaseItem), dict([(x,scrapy.Field()) for x in offer_features_scheme.keys()]))
OfferRoomItem = type('OfferRoomItem', (dict, BaseItem), dict([(x,scrapy.Field()) for x in offer_scheme.keys()]))