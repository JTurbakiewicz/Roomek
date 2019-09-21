#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import Bot.reactions_PL as response
from Bot.cognition import collect_information
from Databases import mysql_connection as db


# TODO bug: adding place yes/no returns nothing
def respond(message, user, bot):

    if message.NLP_intent == "greeting":
        response.greeting(message, user, bot)
    elif not message.NLP_intent and not message.NLP_entities:
        response.default_message(message, user, bot)
        bot.fb_send_text_message(str(message.facebook_id), "o co ja miałem pytać...")
        ask_for_information(message, user, bot)
    elif message.NLP_intent == "restart":
        response.ask_if_restart(message, user, bot)
    elif user.wants_restart:
        response.restart(message, user, bot)
    elif user.confirmed_data:
        response.show_offers(message, user, bot)
    else:
        ask_for_information(message, user, bot)


def ask_for_information(message, user, bot):

    if user.city is None:
        response.ask_for_city(message, user, bot)

    # TODO not the best approach
    elif user.context == "ask_for_city":
        response.ask_for_location(message, user, bot)

    elif user.wants_more_locations:
        response.ask_more_locations(message, user, bot)

    elif user.housing_type is None:
        response.ask_for(message, user, bot, "housing_type")

    elif user.price_limit is None:
        response.ask_for(message, user, bot, "price_limit")

    elif not user.features and user.wants_more_features:
        response.ask_for(message, user, bot, "features")

    elif user.wants_more_features:
        response.ask_for_more_features(message, user, bot)

    elif not user.wants_more_features and not user.confirmed_data:
        response.show_input_data(message, user, bot)

    # TODO response.ask_what_wrong(message, user, bot)

    elif user.confirmed_data and not user.wants_restart:
        response.show_offers(message, user, bot)

    elif user.wants_restart:
        db.drop_user(user.facebook_id)
        response.restart(message, user, bot)

    else:
        response.default_message(message, user, bot)
