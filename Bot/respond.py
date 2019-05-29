#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import Bot.responses_PL as response
from Bot.cognition import collect_information


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


def ask_for_information(message, bot):

    if message.user.city is None:
        response.ask_for_city(message, bot)

    elif not message.user.location:
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

    elif not message.user.wants_more_features and not message.user.confirmed_data:
        response.show_input_data(message, bot)

    # TODO response.ask_what_wrong(message, bot)

    elif message.user.confirmed_data:
        response.show_offers(message, bot)

    else:
        response.default_message(message, bot)
