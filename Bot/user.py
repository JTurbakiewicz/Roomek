#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
import re
from Dispatcher_app import use_database
from Bot.cognition import recognize_sticker, replace_emojis
from Bot.geoinfo import recognize_location
from OfferParser.translator import translate

import tokens
# TODO if use_database: from Databases.... import update_user

# in the future fetch user ids from the DB:
users = {}  # { userID : User() }
if use_database:
    users_in_db = db.get_all(table_name='users', fields_to_get='facebook_id')
    for user_in_db in users_in_db:
        users[user['facebook_id']] = user_in_db


class User:
    """ All user info that we also store in db """

    # TODO zamiana logów na observer pattern - loguj jak zmiana usera

    def __init__(self, facebook_id):
        self.facebook_id = facebook_id
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.business_type = None
        self.housing_type = None
        self.price_limit = None
        self.city = None
        self.street = None
        self.country = None
        self.location = []
        self.latitude = []
        self.longitude = []
        self.features = []  # ["dla studenta", "nieprzechodni", "niepalacy"]
        self.shown_input = False
        self.asked_for_features = False
        self.wants_more_features = True
        self.wants_more_locations = True
        self.confirmed_data = False
        if facebook_id not in users:
            users[facebook_id] = self

        # if facebook_id not in BAZA:
        #     create_user(facebook_id)

    # TODO universal setter?
    # def set_field(self, field_name, filed_value):
    # self.FIELD_NAME = FIELD.VALUE

    def set_facebook_id(self, facebook_id):
        self.facebook_id = str(facebook_id)
        logging.info("[User info] facebook_id set to {0}".format(facebook_id))

    def set_first_name(self, first_name):
        self.first_name = str(first_name)
        logging.info("[User info] first_name set to {0}".format(first_name))

    def set_last_name(self, last_name):
        self.last_name = str(last_name)
        logging.info("[User info] last_name set to {0}".format(last_name))

    def set_gender(self, gender):
        self.gender = str(gender)
        logging.info("[User info] gender set to {0}".format(gender))

    def set_business_type(self, business_type):
        business_type = translate(business_type, "Q") # TODO Skasuj mnie jak Kuba poprawi w bazie.
        self.business_type = str(business_type)
        logging.info("[User info] business_type set to {0}".format(business_type))

    def set_housing_type(self, housing_type):
        housing_type = translate(housing_type, "Q")  # TODO Skasuj mnie jak Kuba poprawi w bazie.
        self.housing_type = str(housing_type)
        logging.info("[User info] housing_type set to {0}".format(housing_type))

    def set_price_limit(self, price_limit):
        try:
            # workaround for witai returning date instead of price:
            if "-" in str(price_limit) and ":" in str(price_limit):
                price_limit = price_limit[0:5]
            clean = re.sub("[^0-9]", "", str(price_limit))
            self.price_limit = int(clean)
            logging.info("[User info] price_limit set to {0}".format(str(self.price_limit)))
        except:
            logging.warning("Couldn't set the price limit using: '{0}', so it remains at {1}.".format(price_limit, self.price_limit))

    def set_city(self, city):
        self.city = str(city)
        logging.info("[User info] city set to {0}".format(city))

    def set_country(self, country):
        self.country = str(country)
        logging.info("[User info] country set to {0}".format(country))

    # TODO powinno być "add" bo przecież może chcieć Mokotów Wolę i Pragę
    def add_location(self, location="", lat=0, long=0):
        if lat != 0 and long != 0:
            self.latitude.append(float(lat))
            self.longitude.append(float(long))
            loc = recognize_location(lat=lat, long=long)
            if hasattr(loc, 'display_name'):
                self.location.append(loc.display_name)
            else:
                logging.warning('location missing!')
        elif "entrum" in str(location):
            if hasattr(self, 'city'):
                loc = recognize_location(location="centrum", city=self.city)
            else:
                loc = recognize_location(location=str(location))
        else:
            loc = recognize_location(location=str(location))

        if not self.latitude and hasattr(loc, 'latitude'):
            self.latitude.append(float(loc.latitude))
            self.longitude.append(float(loc.longitude))
        if not self.city and hasattr(loc, 'city'):
            self.city = loc.city
        if not self.street and hasattr(loc, 'road'):
            self.street = loc.address.road
        if not self.location:
            self.location.append(loc)
            # TODO teraz daje pelny adres a moze samą dzielnicę
        else:
            logging.warning('location missing!')
        if not (hasattr(loc, 'latitude') or hasattr(loc, 'city') or hasattr(loc, 'road')):
            logging.warning("Unable to discover location!")

        logging.info("User({0})'s location changed to: latitude={1}, longitude={2}, city={3}, street={4}, location={5}".format(
            self.facebook_id[0:5], self.latitude, self.longitude, self.city, self.street, self.location))

    def add_feature(self, feature):
        feature = replace_emojis(feature)
        print("TEMP trying to add feature '{0}'".format(feature))
        self.features.append(str(feature))
        logging.info("[User info] added feature: {0}".format(feature))
        print("now features are: "+ str(self.features))
        # TODO powinien sprawdzać czy coś juz jest w zbiorze
        # current = get_user(self.facebook_id)[0]["features"]
        # appended = str(current)+"&"+str(feature)

    def set_confirmed_data(self, confirmed_data):
        self.confirmed_data = confirmed_data
        logging.info("[User info] confirmed_data set to: {0}".format(confirmed_data))
