#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
import re
from Bot.cognition import recognize_sticker, replace_emojis
from Bot.geoinfo import recognize_location
from OfferParser.translator import translate
from Databases import mysql_connection as db


class User:
    """ All user info that we also store in db """

    def __init__(self, facebook_id):

        # permanent:
        self.facebook_id = facebook_id
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.language = None
        # query parameters:
        self.business_type = None
        self.housing_type = None
        self.price_limit = None
        self.features = []  # ["dla studenta", "nieprzechodni", "niepalacy"]
        # address:
        self.country = None
        self.city = None
        self.street = None
        self.latitude = 0
        self.longitude = 0
        # dialogue parameters:
        self.context = "initialization"
        self.interactions = 0
        self.shown_input = False
        self.asked_for_features = False
        self.wants_more_features = True
        self.wants_more_locations = True
        self.confirmed_data = False
        self.add_more = True    # TEMP

        if not db.user_exists(self.facebook_id):
            db.push_user(user_obj=self, update=False)

    # TODO universal setter?
    # def set_field(self, field_name, filed_value):
    # self.FIELD_NAME = FIELD.VALUE

    def increment(self):
        # TODO fix bug:     self.interactions += 1
        pass

    def set_facebook_id(self, facebook_id):
        self.facebook_id = str(facebook_id)
        logging.info("[User info] facebook_id set to {0}".format(facebook_id))
        db.update_user(self.facebook_id, field_to_update="facebook_id", field_value=self.facebook_id)

    def set_first_name(self, first_name):
        self.first_name = str(first_name)
        logging.info("[User info] first_name set to {0}".format(first_name))
        db.update_user(self.facebook_id, field_to_update="first_name", field_value=self.first_name)

    def set_last_name(self, last_name):
        self.last_name = str(last_name)
        logging.info("[User info] last_name set to {0}".format(last_name))
        db.update_user(self.facebook_id, field_to_update="last_name", field_value=self.last_name)

    def set_gender(self, gender):
        self.gender = str(gender)
        logging.info("[User info] gender set to {0}".format(gender))
        db.update_user(self.facebook_id, field_to_update="gender", field_value=self.gender)

    def set_context(self, context):
        self.context = str(context)
        logging.info("[User info] context set to {0}".format(context))
        db.update_user(self.facebook_id, field_to_update="context", field_value=self.context)

    def set_business_type(self, business_type):
        business_type = translate(business_type, "Q") # TODO Skasuj mnie jak Kuba poprawi w bazie.
        self.business_type = str(business_type)
        logging.info("[User info] business_type set to {0}".format(business_type))
        db.update_user(self.facebook_id, field_to_update="business_type", field_value=self.business_type)

    def set_housing_type(self, housing_type):
        housing_type = translate(housing_type, "Q")  # TODO Skasuj mnie jak Kuba poprawi w bazie.
        self.housing_type = str(housing_type)
        logging.info("[User info] housing_type set to {0}".format(housing_type))
        db.update_user(self.facebook_id, field_to_update="housing_type", field_value=self.housing_type)

    def set_price_limit(self, price_limit):
        try:
            # workaround for witai returning date instead of price:
            if "-" in str(price_limit) and ":" in str(price_limit):
                price_limit = price_limit[0:5]
            clean = re.sub("[^0-9]", "", str(price_limit))
            self.price_limit = int(clean)
            db.update_user(self.facebook_id, field_to_update="price_limit", field_value=self.price_limit)
            logging.info("[User info] price_limit set to {0}".format(str(self.price_limit)))

        except:
            logging.warning("Couldn't set the price limit using: '{0}', so it remains at {1}.".format(price_limit, self.price_limit))

    def set_city(self, city):
        self.city = str(city)
        logging.info("[User info] city set to {0}".format(city))
        db.update_user(self.facebook_id, field_to_update="city", field_value=self.city)

    def set_country(self, country):
        self.country = str(country)
        logging.info("[User info] country set to {0}".format(country))
        db.update_user(self.facebook_id, field_to_update="country", field_value=self.country)

    # TODO narazie nadpisuje, a powinno dodawać bo przecież może chcieć Mokotów Wolę i Pragę
    def add_location(self, location="", lat=0, long=0):
        if lat != 0 and long != 0:
            self.latitude = float(lat)
            self.longitude = float(long)
            loc = recognize_location(lat=lat, long=long)
            if hasattr(loc, 'display_name'):
                logging.info("LOCATION OBJECT: " + loc.display_name)
            else:
                logging.warning('Location missing!')

        # elif "entrum" in str(location):
        #     if hasattr(self, 'city'):
        #         loc = recognize_location(location="centrum", city=self.city)
        #     else:
        #         loc = recognize_location(location=str(location))
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
        db.update_user(self.facebook_id, field_to_update="latitude", field_value=self.latitude)
        db.update_user(self.facebook_id, field_to_update="longitude", field_value=self.longitude)
        db.update_user(self.facebook_id, field_to_update="city", field_value=self.city)
        db.update_user(self.facebook_id, field_to_update="street", field_value=self.street)
        db.update_user(self.facebook_id, field_to_update="location", field_value=self.location)
        logging.info("User({0})'s location changed to: latitude={1}, longitude={2}, city={3}, street={4}, location={5}".format(
            self.facebook_id[0:5], self.latitude, self.longitude, self.city, self.street, self.location))

    def add_feature(self, feature):
        feature = replace_emojis(feature)
        if feature not in self.features:
            self.features.append(str(feature))
            logging.info("[User info] added feature: {0}. Now features are: {1}".format(feature, str(self.features)))
            current = db.get_user(self.facebook_id).features
            appended = str(current)+"&"+str(feature)
            db.update_user(self.facebook_id, field_to_update="feature", field_value=appended)
        else:
            logging.info("[User info] Feature: {0} was already in the object.".format(feature))

    def set_confirmed_data(self, confirmed_data):
        self.confirmed_data = confirmed_data
        logging.info("[User info] confirmed_data set to: {0}".format(confirmed_data))
        db.update_user(self.facebook_id, field_to_update="confirmed_data", field_value=self.confirmed_data)
