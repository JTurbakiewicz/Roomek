#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import os
import random
import Bot.bot_responses_PL as response
from Bot.bot_cognition import recognize_location
import logging


def respond(message, bot):

    collect_information(message, bot)

    if hasattr(message, 'NLP_intent'):
        if message.NLP_intent == "greeting":
            response.greeting(message, bot)
        elif message.NLP_intent == "looking for":
            message.user.business_type = "rent"
            ask_for_information(message, bot)
        elif message.NLP_intent == "offering":
            message.user.business_type = "offer"
            response.unable_to_answer(message, bot)
        elif message.NLP_intent is None:
            ask_for_information(message, bot)
    else:
        ask_for_information(message, bot)

def collect_information(message, bot):
    if hasattr(message, 'NLP_entities'):
        for entity in message.NLP_entities:     # [entity, value, confidence, body]
            if message.user.city is None and entity[0] == "location":
                message.user.set_city(entity[1])
            elif message.user.location is None and entity[0] == "location":
                message.user.set_location(entity[1])
            elif message.user.location is None and message.type == "LocationAnswer":
                message.user.set_location(lat=message.latitude, long=message.longitude)
            elif message.user.housing_type is None and entity[0] == "housing_type":
                message.user.set_housing_type(entity[1])
            elif message.user.price_limit is None:
                message.user.set_price_limit(entity[3])
            elif message.user.features is None:
                message.user.add_feature(entity[1])
    else:
        if message.user.city is None:
            try: message.user.set_city(recognize_location(message.text).city)
            except: pass
        elif message.user.location is None and message.type == "LocationAnswer":
            message.user.set_location(message.latitude, message.longitude)
        elif message.user.location is None:
            try: message.user.set_location(recognize_location(message.text).city)
            except: pass
        elif message.user.housing_type is None:
            message.user.set_housing_type(message.text)
        elif message.user.price_limit is None:
            message.user.set_price_limit(message.text)
        elif message.user.features is None:
            message.user.add_feature(message.text)


def ask_for_information(message, bot):

    if message.user.city is None:
        response.ask_for_city(message, bot)
    elif message.user.location is None:
        response.ask_for_location(message, bot)
    elif message.user.housing_type is None:
        response.ask_for_housing_type(message, bot)
    elif message.user.price_limit is None:
        response.ask_for_price_limit(message, bot)
    elif message.user.features == []:
        response.ask_for_features(message, bot)
    elif message.user.add_more is True:
        response.ask_if_want_more(message, bot)
        if "no" in message.NLP_intent:  # TODO
            message.user.add_more = False
            # TODO
        else:
            response.ask_if_want_more(message, bot)
    elif message.user.add_more is False:
        response.show_input_data(message, bot)
        if message.user.confirmed_data == False:
            response.ask_what_wrong(message, bot)
        else:
            message.user.confirmed_data = True
            response.dead_end(message, bot)  # TODO
    elif message.user.confirmed_data is None:
        response.dead_end(message, bot)
        # TODO

    # else:
    #     response.default_message(message, bot)