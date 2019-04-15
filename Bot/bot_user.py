#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
import re
from Dispatcher_app import use_local_tokens, use_database
from Bot.bot_cognition import recognize_sticker, recognize_location
if use_local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
# TODO if use_database: from Databases.... import update_user

# in the future fetch user ids from the DB:
users = {}  # { userID : User() }
if use_database:
    users_in_db = db.get_all(table_name='users', fields_to_get='facebook_id')
    for user_in_db in users_in_db:
        users[user['facebook_id']] = user_in_db


class User:
    """ All user info that we also store in db """

    def __init__(self, facebook_id):
        self.facebook_id = facebook_id
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.business_type = None
        self.housing_type = None
        self.price_limit = None
        self.city = None
        self.country = None
        self.location = None
        self.features = []  # ["dla studenta", "nieprzechodni", "niepalacy"]
        self.add_more = True
        self.shown_input = False
        self.confirmed_data = False
        if facebook_id not in users:
            users[facebook_id] = self

        # if facebook_id not in BAZA:
        #     create_user(facebook_id)

    # TODO universal setter
    # def set_field(self, field_name, filed_value):
    # self.FIELD_NAME = FIELD.VALUE

    def set_facebook_id(self, facebook_id):
        self.facebook_id = str(facebook_id)
        logging.info("facebook_id set to {0}".format(facebook_id))
        # update_user(self.facebook_id, "facebook_id", facebook_id)

    def set_first_name(self, first_name):
        self.first_name = str(first_name)
        logging.info("first_name set to {0}".format(first_name))
        # update_user(self.facebook_id, "first_name", first_name)

    def set_last_name(self, last_name):
        self.last_name = str(last_name)
        logging.info("last_name set to {0}".format(last_name))
        # update_user(self.facebook_id, "last_name", last_name)

    def set_gender(self, gender):
        self.gender = str(gender)
        logging.info("gender set to {0}".format(gender))
        # update_user(self.facebook_id, "gender", gender)

    def set_business_type(self, business_type):
        self.business_type = str(business_type)
        logging.info("business_type set to {0}".format(business_type))
        # update_user(self.facebook_id, "business_type", business_type)

    def set_housing_type(self, housing_type):
        self.housing_type = str(housing_type)
        logging.info("housing_type set to {0}".format(housing_type))
        # update_user(self.facebook_id, "housing_type", housing_type)

    def set_price_limit(self, price_limit):
        try:
            clean = re.sub("[^0-9]", "", str(price_limit))
            self.price_limit = int(clean)
            logging.info("price_limit set to {0}".format(clean))
        except:
            logging.warning("Couldn't set the price limit using: '{0}'".format(price_limit))
        # update_user(self.facebook_id, "price_limit", int(price_limit))

    def set_city(self, city):
        self.city = str(city)
        logging.info("city set to {0}".format(city))
        # update_user(self.facebook_id, "city", city)

    def set_country(self, country):
        self.country = str(country)
        logging.info("country set to {0}".format(country))
        # update_user(self.facebook_id, "country", country)

    def set_location(self, location, lat=0, long=0):
        if lat != 0 and long !=0:
            self.location = [float(lat), float(long)]
            logging.info("Location changed: latitude={0}, longitude={1}".format(lat, long))
        else:
            loc = recognize_location(location)
            if hasattr(loc, 'latitude'):
                self.location = [float(loc.latitude), float(loc.longitude)]
                logging.info("Location changed: latitude={0}, longitude={1}".format(loc.latitude, loc.longitude))
            if hasattr(loc, 'city'):
                self.city = loc.city
                logging.info("Location changed: city={0}".format(loc.city))
            if hasattr(loc, 'road'):
                self.street = loc.road
                logging.info("Location changed: street={0}".format(loc.road))
        # update_user(self.facebook_id, "location_latitude", float(x))
        # update_user(self.facebook_id, "location_longitude", float(y))

    # TODO debug me
    def add_feature(self, feature):
        self.features.append(feature)
        logging.info("added feature: {0}".format(feature))
        # current = get_user(self.facebook_id)[0]["features"]
        # appended = str(current)+"&"+str(feature)
        # update_user(self.facebook_id, "feature", appended)

    def set_add_more(self, add_more):
        self.add_more = add_more
        logging.info("add_more set to: {0}".format(add_more))
        # update_user(self.facebook_id, "add_more", add_more)

    def set_confirmed_data(self, confirmed_data):
        self.confirmed_data = confirmed_data
        logging.info("confirmed_data set to: {0}".format(confirmed_data))
        # update_user(self.facebook_id, "confirmed_data", confirmed_data)
