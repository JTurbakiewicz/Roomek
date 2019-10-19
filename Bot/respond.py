#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import Bot.reactions_PL as response
from Bot.cognition import collect_information
from Databases import mysql_connection as db
from schemas import user_questions, bot_phrases, query_scheme
import random

# TODO bug: adding place yes/no returns nothing
def respond(message, user, bot):

    if message.NLP_intent == "greeting":
        response.greeting(message, user, bot)
    elif not message.NLP_intent and not message.NLP_entities:   # nie zrozumiał, więc ponawia pytanie
        response.default_message(message, user, bot)
        response2 = random.choice(bot_phrases['back_to_context'])
        bot.fb_send_text_message(str(message.facebook_id), response2)
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

    if db.user_query(user.facebook_id, "business_type") is None:
        response.ask_for(message, user, bot, param="business_type")

    elif db.user_query(user.facebook_id, "city") is None:
        response.ask_for(message, user, bot, param="city")

    # TODO not the best approach
    elif user.context == "ask_for_city":
        response.ask_for_location(message, user, bot)

    elif user.wants_more_locations:
        response.ask_more_locations(message, user, bot)

    elif db.user_query(user.facebook_id, "housing_type") is None:
        response.ask_for(message, user, bot, param="housing_type")

    elif db.user_query(user.facebook_id, "price") is None:
        response.ask_for(message, user, bot, param="price")

    elif user.wants_more_features:
        features_in_schema = [field_name for field_name, field_value in query_scheme.items() if
                              field_value['is_feature']]
        user_features_queried = [query_tuple[0] for query_tuple in db.get_all_queries(facebook_id=user.facebook_id)]
        features_recorded = [i for i in user_features_queried if i in features_in_schema]
        if len(features_recorded) == 0:
            response.ask_for(message, user, bot, param="features")
        else:
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
