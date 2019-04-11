#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
from Dispatcher_app import use_local_tokens
from Bot.bot_cognition import recognize_sticker
if use_local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
# TODO if use_database: from Databases.... import update_user
log = logging.getLogger(os.path.basename(__file__))

# in the future fetch user ids from the DB:
users = {}  # { userID : User() }
if use_database:
    users_in_db = db.get_all(table_name='users', fields_to_get='facebook_id')
    for user_in_db in users_in_db:
        users[user['facebook_id']] = user_in_db


class Message:
    """
    Has attributes taken from json post that was sent to the server from facebook.
    Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
    """

    def __init__(self, json_data):
        min_confidence = 0.90
        self.__dict__ = json_data  # previously json.loads
        self.id = self.entry[0]['id']
        if 'messaging' in self.entry[0]:
            self.messaging = self.entry[0]['messaging'][0]
            self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.senderID = self.messaging['sender']['id']
            self.recipientID = self.messaging['recipient']['id']
            if self.senderID not in users:
                # create new user and add to the dictionary (in class creator)
                self.user = User(self.senderID)
            else:
                # assign existing user to this object
                self.user = users[self.senderID]
            if 'delivery' in self.messaging: self.type = "Delivery"
            elif 'read' in self.messaging: self.type = "ReadConfirmation"
            elif 'message' in self.messaging:
                self.mid = 1234567890
                # self.mid = self.messaging['message']['mid']
                # TODO: delivery has mids not mid
                if 'attachments' in self.messaging['message']:
                    if 'sticker_id' in self.messaging['message']:
                        self.type = "StickerMessage"
                        self.stickerID = self.messaging['message']['sticker_id']
                        self.stickerName = recognize_sticker(self.stickerID)
                    else:
                        self.type = "MessageWithAttachment"
                        self.url = str(self.messaging['message']['url'])
                else:
                    self.text = self.messaging['message']['text']
                    if self.text.startswith('bottest'):
                        self.type = "BotTest"
                    else:
                        self.type = "TextMessage"
                        self.text = self.messaging['message']['text']
                        if 'nlp' in self.messaging['message']:
                            self.NLP = True
                            self.NLP_entities = []
                            nlp = self.messaging['message']['nlp']['entities']
                            entities = list(nlp.keys())
                            if 'intent' in entities:
                                if nlp['intent'][0]['confidence'] > min_confidence:
                                    self.NLP_intent = nlp['intent'][0]['value']
                                else:
                                    self.NLP_intent = None
                                entities.remove("intent")
                            else:
                                self.NLP_intent = None
                            for e in entities:
                                if nlp[e][0]['confidence'] > min_confidence:
                                    self.NLP_entities.append([
                                        nlp[e][0]['_entity'],
                                        nlp[e][0]['value'],
                                        nlp[e][0]['confidence'],
                                        nlp[e][0]['_body']
                                    ])
                        else:
                            self.NLP = False
            else:
                self.type = "UnknownType"
        else:
            self.type = "UnknownType"

        if int(self.recipientID) == int(tokens.fb_bot_id):
            self.recipient = "bot"
            self.sender = "user"
        else:
            self.recipient = "user"
            self.sender = "bot"

        # logs:
        # TODO: zmienne maja zle nazwy
        if self.sender == "user":
            if self.type == "UnknownType":
                log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))
            elif self.type == "Delivery":
                log.info("Message from {0} has been delivered.".format(str(self.senderID)[0:5]))
            elif self.type == "ReadConfirmation":
                log.info("Message from {0} read by bot.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Message from user {0}:  '<sticker id={1}>'".format(str(self.senderID)[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Message from user {0}:  '<GIF link={1}>'".format(str(self.senderID)[0:5], self.url))
            elif self.type == "TextMessage":
                log.info("Message '{0}' from user {1}:  '{2}'".format(self.text, str(self.senderID)[0:5], self.messaging))
            else:
                log.error("Unknown message type! Content: " + message)
        if self.sender == "bot":
            if self.type == "UnknownType":
                log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(self.messaging))
            elif self.type == "Delivery":
                log.info("Bot's message to {0} has been delivered.".format(str(self.senderID)[0:5]))
            elif self.type == "ReadConfirmation":
                log.info("Bot's message read by {0}.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Bot's message to user {0}:  '<sticker id={1}>'".format(str(self.senderID)[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Bot's message to user {0}:  '<GIF link={1}>'".format(str(self.senderID)[0:5], self.url ))
            elif self.type == "TextMessage":
                log.info("Bot's message '{0}' to user {1}:  '{2}'".format(self.text, str(self.recipientID)[0:5], self.text))
            else:
                log.error("Unknown message type! Content: " + self.messaging)
        else:
            pass
            # log.error("Unknown sender! Content: " + str(self.messaging))


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
        self.features = []      # ["dla studenta", "nieprzechodni", "niepalacy"]
        self.add_more = True
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
        # update_user(self.facebook_id, "facebook_id", facebook_id)

    def set_first_name(self, first_name):
        self.first_name = str(first_name)
        # update_user(self.facebook_id, "first_name", first_name)

    def set_last_name(self, last_name):
        self.last_name = str(last_name)
        # update_user(self.facebook_id, "last_name", last_name)

    def set_gender(self, gender):
        self.gender = str(gender)
        # update_user(self.facebook_id, "gender", gender)

    def set_business_type(self, business_type):
        self.business_type = str(business_type)
        # update_user(self.facebook_id, "business_type", business_type)
        
    def set_housing_type(self, housing_type):
        self.housing_type = str(housing_type)
        # update_user(self.facebook_id, "housing_type", housing_type)
        
    def set_gender(self, gender):
        self.gender = str(gender)
        # update_user(self.facebook_id, "gender", gender)
        
    def set_price_limit(self, price_limit):
        self.price_limit = int(price_limit)
        # update_user(self.facebook_id, "price_limit", int(price_limit))

    def set_city(self, city):
        self.city = str(city)
        # update_user(self.facebook_id, "city", city)
        
    def set_country(self, country):
        self.country = str(country)
        # update_user(self.facebook_id, "country", country)

    def set_location(self, x, y):
        self.location = [float(x), float(y)]
        # update_user(self.facebook_id, "location_latitude", float(x))
        # update_user(self.facebook_id, "location_longitude", float(y))

    # TODO debug me
    def add_feature(self, feature):
        self.features.append(feature)
        # current = get_user(self.facebook_id)[0]["features"]
        # appended = str(current)+"&"+str(feature)
        # update_user(self.facebook_id, "feature", appended)

    def set_add_more(self, add_more):
        self.add_more = add_more
        # update_user(self.facebook_id, "add_more", add_more)

    def set_confirmed_data(self, confirmed_data):
        self.confirmed_data = confirmed_data
        # update_user(self.facebook_id, "confirmed_data", confirmed_data)
