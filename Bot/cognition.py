#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions enabling the Bot to understand messages and intents. """

# from Bot.bot_responses_PL import *
import logging

# Set of intents and patterns to recognize them:
pattern_dictionary = {
        'greeting': [r'\b(hi|h[ea]+l+?o|h[ea]+[yj]+|yo+|welcome|(good)?\s?(morning?|evenin?)|hola|howdy|shalom|salam|czesc|cześć|hejka|witaj|siemk?a|marhaba|salut)\b', r'(\🖐|\🖖|\👋|\🤙)'],
        'yes': [r'\b(yes|si|ok|kk|ok[ae]y|confirm)\b',r'\b(tak|oczywiście|dobra|dobrze)\b',r'(\✔️|\☑️|\👍|\👌)'],
        'no': [r'\b(n+o+|decline|negative|n+o+pe)\b', r'\b(nie+)\b', r'\👎'],
        'maybe' : r'\b(don\'?t\sknow?|maybe|perhaps?|not\ssure|może|moze|y+)\b',
        'curse' : [r'\b(fuck|kurwa)\b', r'pierd[oa]l', r'\bass', r'\🖕'],
        'uname' : [r'y?o?ur\sname\??', r'(how|what)[\s\S]{1,15}call(ing)?\sy?o?u\??'],
        'ureal' : r'\by?o?u\s(real|true|bot|ai|human|person|man)\b',
        'test_list_message': r'list message',
        'test_button_message': r'button message',
        'test_generic_message': r'generic message',
        'test_quick_replies': r'quick replies',
        'bye': r'(bye|exit|quit|end)'
    }


def collect_information(message, bot):
    """
    Function that parses message to find as many information as possible and add as parameters to the user object.
    """

    if not message.user.location and message.type == "LocationAnswer":
        message.user.add_location(message.latitude, message.longitude)

    elif message.NLP:
        if message.NLP_intent is not None:
            if message.NLP_intent == "boolean":
                print("TEMP 0001 Trochę DEAD END... " + message.NLP_intent)

        if message.NLP_entities:  # posiada entities

            for entity in message.NLP_entities:     # [entity, value, confidence, body]

                # TODO if confidence > minimum...

                # TODO zamiana logów na observer pattern - loguj jak zmiana usera

                if message.user.city is None and entity[0] == "location":
                    message.user.set_city(entity[1])

                elif message.user.wants_more_locations:
                    if entity[0] == "boolean" and entity[1] == "no":
                        message.user.wants_more_locations = False
                    elif message.type == "LocationAnswer":
                        message.user.add_location(lat=message.latitude, long=message.longitude)
                    elif entity[0] == "location":
                        message.user.add_location(entity[1])

                elif message.user.wants_more_features and entity[0] == "boolean" and entity[1] == "no":
                    message.user.wants_more_features = False
                    logging.info("[User {0} Update] wants_more_features = False".format(message.user.facebook_id))

                elif message.user.housing_type is None and entity[0] == "housing_type":
                    message.user.set_housing_type(entity[1])

                elif message.user.price_limit is None:
                    message.user.set_price_limit(entity[3])

                elif not message.user.wants_more_features and not message.user.confirmed_data:
                    if entity[0] == "boolean" and entity[1] == "yes":
                        message.user.confirmed_data = True
                        logging.info("[User {0} Update] confirmed_data = True".format(message.user.facebook_id))

                    elif entity[0] == "boolean" and entity[1] == "no":
                        message.user.confirmed_data = False
                        logging.info("[User {0} Update] confirmed_data = False".format(message.user.facebook_id))
                        # TODO dead end.

        else:   # ma nlp, ale intent=none i brak mu entities, więc freetext do wyłapania

            if message.user.city is None:
                try: message.user.set_city(recognize_location(message.text).city)
                except: pass

            elif not message.user.location and message.type == "LocationAnswer":
                message.user.add_location(message.latitude, message.longitude)

            elif not message.user.location:
                try: message.user.add_location(recognize_location(message.text).city)
                except: pass

            elif message.user.housing_type is None:
                message.user.set_housing_type(message.text)

            elif message.user.price_limit is None:
                print("tutaj 001")
                message.user.set_price_limit(message.text)

            elif message.user.wants_more_features:
                message.user.add_feature(message.text)

            elif message.user.wants_more_features and entity[0] == "boolean" and entity[1] == "no":
                message.user.wants_more_features = False
                logging.info("[User {0} Update] wants_more_features = False".format(message.user.facebook_id))
            else:
                response.default_message(message, bot)
    else:
        if message.user.price_limit is None and message.type == "TextMessage":
            print("tutaj 004")
            message.user.set_price_limit(99999999)


def regex_pattern_matcher(str, pat_dic=pattern_dictionary):
    """Regular Expression pattern finder that searches for intents from patternDictionary."""
    intent = False
    for key, value in pat_dic.items():
        search_object = False
        if type(value) == list:
            for v in value:
                s = re.search(v, str, re.M|re.I|re.U)    #|re.U
                if s != None:
                    search_object = s
        else:
            search_object = re.search(value, str, re.M|re.I|re.U)    #|re.U

        if search_object:
            intent = key   #cause found searchObj.group()

    return intent


def replace_emojis(to_replace):
    to_replace = replace_if_contains(to_replace, "🐶", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐱", "zwierz")
    to_replace = replace_if_contains(to_replace, "🔨", "remont")
    to_replace = replace_if_contains(to_replace, "🛀", "wanna")
    to_replace = replace_if_contains(to_replace, "🚬", "palący")
    to_replace = replace_if_contains(to_replace, "🚭", "niepalący")
    to_replace = replace_if_contains(to_replace, "💩", "słaba")
    to_replace = replace_if_contains(to_replace, "🐭", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐹", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐰", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐍", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐢", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐠", "zwierz")
    to_replace = replace_if_contains(to_replace, "🐟", "zwierz")
    to_replace = replace_if_contains(to_replace, "👏", "brawo")
    to_replace = replace_if_contains(to_replace, "👍", "tak")
    to_replace = replace_if_contains(to_replace, "👎", "nie")
    to_replace = replace_if_contains(to_replace, "🚲", "rower")
    to_replace = replace_if_contains(to_replace, "🎊", "imprez")
    to_replace = replace_if_contains(to_replace, "🎉", "imprez")
    return to_replace


def replace_if_contains(to_replace, if_contains, replace_with):
    if str(if_contains) in str(to_replace):
        return to_replace.replace(str(if_contains), str(replace_with))
        logging.debug("replaced {0} with {1}").format(str(if_contains), str(replace_with))
    else:
        return str(to_replace)


def recognize_sticker(sticker_id):
    sticker_id = str(sticker_id)
    if sticker_id.startswith('369239263222822'):  sticker_name = 'thumb'
    elif sticker_id.startswith('369239343222814'):  sticker_name = 'thumb+'
    elif sticker_id.startswith('369239383222810'): sticker_name = 'thumb++'
    elif sticker_id.startswith('523675'):  sticker_name = 'dogo'
    elif sticker_id.startswith('631487'):  sticker_name = 'cactus'
    elif sticker_id.startswith('788676574539860'):  sticker_name = 'dogo_great'
    elif sticker_id.startswith('78817'):  sticker_name = 'dogo'
    elif sticker_id.startswith('7926'):  sticker_name = 'dogo'
    elif sticker_id.startswith('1845'):  sticker_name = 'bird'
    elif sticker_id.startswith('1846'):  sticker_name = 'bird'
    elif sticker_id.startswith('14488'):  sticker_name = 'cat'
    elif sticker_id.startswith('65444'):  sticker_name = 'monkey'
    elif sticker_id.startswith('12636'):  sticker_name = 'emoji'
    elif sticker_id.startswith('1618'):  sticker_name = 'turtle'
    elif sticker_id.startswith('8509'):  sticker_name = 'office'
    elif sticker_id.startswith('2556'):  sticker_name = 'chicken'
    elif sticker_id.startswith('2095'):  sticker_name = 'fox'
    elif sticker_id.startswith('56663'):  sticker_name = 'kungfurry'
    elif sticker_id.startswith('30261'):  sticker_name = 'sloth'
    else:  sticker_name = 'unknown'
    return sticker_name
