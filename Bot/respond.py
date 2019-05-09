#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import os
import random
import Bot.responses_PL as response
from Bot.cognition import recognize_location
import logging


# TODO bug: adding place yes/no returns nothing
# TODO multiple parameters in one message
def respond(message, bot):

    collect_information(message, bot)

    # TODO no greeting start
    if hasattr(message, 'NLP_intent'):
        if message.NLP_intent == "greeting":
            response.greeting(message, bot)
        elif message.NLP_intent == "looking for":
            message.user.set_business_type("rent")
            ask_for_information(message, bot)
        elif message.NLP_intent == "offering":
            message.user.set_business_type("offer")
            response.unable_to_answer(message, bot)
        # TODO inne opcje jak kupno itd
        else:
            ask_for_information(message, bot)
    else:
        ask_for_information(message, bot)


def collect_information(message, bot):

    if message.user.location is None and message.type == "LocationAnswer":
        message.user.set_location(message.latitude, message.longitude)

    elif message.user.price_limit is None and "kwota" in message.text:
        message.user.set_price_limit(99999999)

    elif message.NLP:
        if message.NLP_intent is not None:
            if message.NLP_intent == "boolean":
                print("TEMP 0001 Trochę DEAD END... " + message.NLP_intent)

        if message.NLP_entities:  # posiada entities

            for entity in message.NLP_entities:     # [entity, value, confidence, body]

                if message.user.city is None and entity[0] == "location":
                    message.user.set_city(entity[1])

                elif message.user.location is None and entity[0] == "location":
                    message.user.set_location(entity[1])

                elif message.user.location is None and message.type == "LocationAnswer":
                    message.user.set_location(lat=message.latitude, long=message.longitude)

                elif message.user.wants_more_locations and entity[0] == "boolean" and entity[1] == "no":
                    message.user.wants_more_locations = False

                elif message.user.wants_more_features and entity[0] == "boolean" and entity[1] == "no":
                    message.user.wants_more_features = False

                elif message.user.housing_type is None and entity[0] == "housing_type":
                    message.user.set_housing_type(entity[1])

                elif message.user.price_limit is None:
                    message.user.set_price_limit(entity[3])

                elif not message.user.wants_more_features and message.user.confirmed_data is None:
                    if entity[0] == "boolean" and entity[1] == "yes":
                        message.user.confirmed_data = True
                    elif entity[0] == "boolean" and entity[1] == "no":
                        message.user.confirmed_data = False

        else:   # ma nlp, ale intent=none i brak mu entities, więc freetext do wyłapania

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

            elif message.user.wants_more_features:
                message.user.add_feature(message.text)

            elif message.user.wants_more_features and entity[0] == "boolean" and entity[1] == "no":
                message.user.wants_more_features = False

            else:
                response.default_message(message, bot)


def ask_for_information(message, bot):

    if message.user.city is None:
        response.ask_for_city(message, bot)

    elif message.user.location is None:
        response.ask_for_location(message, bot)

    elif message.user.wants_more_locations:
        response.ask_more_locations(message, bot)

    elif message.user.housing_type is None:
        response.ask_for_housing_type(message, bot)

    elif message.user.price_limit is None:
        response.ask_for_price_limit(message, bot)

    elif not message.user.features and not message.user.asked_for_features and message.user.wants_more_features:
        response.ask_for_features(message, bot)
        message.user.asked_for_features = True

    elif message.user.wants_more_features is True:
        response.ask_for_more_features(message, bot)

    elif message.user.wants_more_features is False:
        response.show_input_data(message, bot)
        # TODO TEMP
        response.show_offers(message, bot)

    # elif not message.user.confirmed_data:
        # TODO TEMP response.ask_what_wrong(message, bot)
        # best = best_offer(user_obj=message.user)
        # response.show_offers(message, bot, best)

    elif message.user.confirmed_data is None:
        response.show_offers(message, bot)
        # TODO

    else:
        response.default_message(message, bot)
