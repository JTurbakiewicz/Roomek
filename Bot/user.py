#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
import datetime
import re
from Bot.cognition import replace_emojis
from Bot.geolocate import recognize_location
from OfferParser.translator import translate
from Databases import mysql_connection as db
from Bot.facebook_webhooks import get_user_info
from schemas import user_scheme

UserTemplate = type('UserTemplate', (object,), dict([(x, y["init"]) for x, y in user_scheme.items()]))


class User(UserTemplate):
    """ All user info that we also store in db """

    def __init__(self, facebook_id):

        self.facebook_id = facebook_id

        if not db.user_exists(self.facebook_id):
            info = get_user_info(facebook_id)
            logging.debug("User data gathered from facebook: " + str(info))
            for n in info.keys():
                try:
                    setattr(self, n, info[n])
                except KeyError:
                    logging.warning(f"User {facebook_id} has no parameter {n}.")
            db.push_user(user_obj=self, update=False)
            db.create_query(facebook_id=facebook_id)

    def set_param(self, name, value):

        if name == "price":
            self.set_price(value)
        elif name in user_scheme.keys():
            setattr(self, name, value)
            db.update_user(self.facebook_id, field_to_update=name, field_value=value)
        else:
            db.update_query(facebook_id=self.facebook_id, field_name=name, field_value=value)

    def set_price(self, price):
        try:
            # workaround for witai returning date instead of price:
            if "-" in str(price) and ":" in str(price):
                price = price[0:5]
            clean = re.sub("[^0-9]", "", str(price))
            db.update_query(facebook_id=self.facebook_id, field_name='price', field_value=int(clean))
        except:
            logging.warning(
                f"Couldn't set the price limit using: '{price}', so it remains at {self.price}.")

    # TODO narazie nadpisuje, a powinno dodawać bo przecież może chcieć Mokotów Wolę i Pragę
    def add_location(self, location="", lat=0, long=0, city_known=False):

        if lat != 0 and long != 0:
            loc = recognize_location(lat=lat, long=long)
        # TODO
        elif "entrum" in str(location):
            if hasattr(self, 'city'):
                loc = recognize_location(location="centrum", city=self.city)
            else:
                loc = recognize_location(location=str(location))
        else:
            loc = recognize_location(location=str(location))
        try:
            db.update_query(facebook_id=self.facebook_id, field_name='latitude', field_value=float(loc['lat']))
            db.update_query(facebook_id=self.facebook_id, field_name='longitude', field_value=float(loc['lon']))
            db.update_query(facebook_id=self.facebook_id, field_name='country', field_value=loc['country'])
            db.update_query(facebook_id=self.facebook_id, field_name='city', field_value=loc['city'])
            db.update_query(facebook_id=self.facebook_id, field_name='district', field_value=loc['district'])
            db.update_query(facebook_id=self.facebook_id, field_name='street', field_value=loc['street'])
        except TypeError:
            logging.warning("Probably item was misinterpeted as location by wit")

    def add_feature(self, entity, value=None):
        feature = replace_emojis(entity['role'])
        value = entity['value']
        if feature == 'ready_from':
            value = datetime.datetime.today()
        elif feature in ['furniture', 'connecting_room', 'pet_friendly', 'balcony', 'non_smokers_only',
                         'parking_space']:
            value = True if value == 'True' else False
        elif feature in ['apartment_level', 'amount_of_rooms']:
            value = int(value)
        try:
            db.update_query(facebook_id=self.facebook_id, field_name=feature, field_value=value)
        except:
            logging.error(
                f'Received feature {feature} could not be saved in DB. Probably formatting needs to be adjusted')

    def restart(self, restart):
        if restart:
            logging.info(f"[User info] User has been restarted.")
            db.drop_user(self.facebook_id)
            self = User(facebook_id=self.facebook_id)
