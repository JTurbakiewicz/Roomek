#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
import re
from Bot.cognition import recognize_sticker, replace_emojis
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

        info = get_user_info(facebook_id)
        for n in info.keys():
            try:
                setattr(self, n, info[n])
            except KeyError:
                logging.warning(f"User {facebook_id} has no parameter {n}.")

        if not db.user_exists(self.facebook_id):
            db.push_user(user_obj=self, update=False)

    def increment(self):
        # TODO fix bug:     self.interactions += 1
        pass

    def set_param(self, name, value):
        if name == "price_limit":
            self.set_price_limit(value)
        else:
            setattr(self, name, value)
        logging.info(f"[User info] {name} set to {value}")
        db.update_user(self.facebook_id, field_to_update=name, field_value=value)

    def set_price_limit(self, price_limit):
        try:
            # workaround for witai returning date instead of price:
            if "-" in str(price_limit) and ":" in str(price_limit):
                price_limit = price_limit[0:5]
            clean = re.sub("[^0-9]", "", str(price_limit))
            self.price_limit = int(clean)
            db.update_user(self.facebook_id, field_to_update="price_limit", field_value=self.price_limit)
            logging.info(f"[User info] price_limit set to {str(self.price_limit)}")
        except:
            logging.warning(
                f"Couldn't set the price limit using: '{price_limit}', so it remains at {self.price_limit}.")

    # TODO narazie nadpisuje, a powinno dodawać bo przecież może chcieć Mokotów Wolę i Pragę
    def add_location(self, location="", lat=0, long=0):

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

        self.latitude = float(loc['lat'])
        self.longitude = float(loc['lon'])
        self.country = loc['country']
        self.city = loc['city']
        self.street = loc['street']
        # self.state = loc['state']
        # self.county = loc['county']

        db.update_user(self.facebook_id, field_to_update="city", field_value=self.city)
        db.update_user(self.facebook_id, field_to_update="latitude", field_value=self.latitude)
        db.update_user(self.facebook_id, field_to_update="longitude", field_value=self.longitude)
        if self.context != "ask_for_city":
            db.update_user(self.facebook_id, field_to_update="street", field_value=self.street)
        db.update_user(self.facebook_id, field_to_update="country", field_value=self.country)

        logging.info(f"User({self.facebook_id[0:5]})'s location changed to: latitude={self.latitude}, longitude={self.longitude}, city={self.city}, street={self.street}, country={self.country}")

    def add_feature(self, feature):
        feature = replace_emojis(feature)
        if not self.features:
            self.features = ""
        if feature not in self.features:
            self.features += "&" + str(feature)
            logging.info(f"[User info] added feature: {feature}. Now features are: {str(self.features)}")
            current = db.get_user(self.facebook_id).features
            appended = str(current) + "&" + str(feature)
            db.update_user(self.facebook_id, field_to_update="features", field_value=appended)
        else:
            logging.info(f"[User info] Feature: {feature} was already in the object.")

    def restart(self, restart):
        if restart:
            logging.info(f"[User info] User has been restarted.")
            db.drop_user(self.facebook_id)
            self = User(facebook_id=self.facebook_id)
