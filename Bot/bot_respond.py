#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import os
import random
import Bot.bot_responses_PL as response
import logging
log = logging.getLogger(os.path.basename(__file__))


def respond(message, bot):

    if message.user.city is None:
        response.ask_for_city(message, bot)
    elif message.user.location is None:
        response.ask_for_location(message, bot)
    elif message.user.housing_type None:
        response.ask_for_housing_type(message, bot)
    elif message.user.price_limit is None:
        response.ask_for_price_limit(message, bot)
    elif message.user.features == []:
        response.ask_for_features(message, bot)
    elif message.user.add_more is True:
        response.ask_if_want_more(message, bot)
        if "NO":    # TODO
            message.user.add_more = False # TODO
        else:
            response.ask_if_want_more(message, bot)
    elif message.user.add_more is False:
        response.show_inut_data(message, bot)
        response.ask_if_correct(message, bot)
        if message.user.confirmed_data = False:
            response.ask_what_wrong(message, bot)
        else:
            message.user.confirmed_data = True
    elif message.user.confirmed_data is None:
        ...







    if user.showBL:
        pass
    else:
        pass

    if message.NLP_intent == "greeting":
        greeting(message, bot)

    elif message.NLP_intent == "looking for":
        if 'housing_type' not in message.NLP_entities:
            ask_for_housing_type(message, bot)
        elif 'wit/location' not in message.NLP_entities:
            ask_for_location(message, bot)
        elif 'wit/amount_of_money' not in message.NLP_entities:
            ask_for_money_limit(message, bot)
        else:
            show_offers(message, bot)

    elif message.NLP_intent == "offering":
        bot.fb_send_text_message(str(message.senderID),
                                 "Wybacz, na ten moment potrafię tylko szukać ofert wynajmu lub kupna.")
    else:
        default_message(message, bot)