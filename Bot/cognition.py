#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions enabling the Bot to understand messages and intents. """

# from Bot.bot_responses_PL import *
import logging
from settings import MINIMUM_CONFIDENCE
import Bot.reactions_PL as response
from OfferParser.translator import translate
from pprint import pprint


def collect_information(message, user, bot):
    """
    Function that parses message to find as many information as possible and add as parameters to the user object.
    """

    if user.context == "":
        # TODO np. dodawanie features
        pass

    if message.NLP:

        if message.NLP_intent is not None:
            if message.NLP_intent == "greeting":
                pass
            elif message.NLP_intent == "offering":
                user.set_business_type("offering")
            elif message.NLP_intent == "looking for":
                user.set_business_type("looking for")
            else:
                logging.warning(f"Didn't catch what user said! Intent: {message.NLP_intent}")

        if message.NLP_entities:
            for entity in message.NLP_entities:     # [name, value, confidence, body, (role)]
                try:
                    print(entity, 'to jest to')
                except:
                    pass
                if entity[2] >= MINIMUM_CONFIDENCE:

                    if entity[0] == "housing_type":
                        if user.housing_type is None:
                            user.set_housing_type(entity[1])
                        # else:
                        #     new = translate(entity[1], "Q")
                        #     if user.housing_type != new:
                        #         response.ask_if_new_housing_type(message, user, bot, new)
                        #     else:
                        #         logging.info("Housing_type already has this value.")

                    if entity[0] == "location":
                        user.add_location(location=entity[1])


                    try:
                        if entity[4] == "price_limit":
                            user.set_price_limit(entity[1])
                    except:
                        print("Żałuję że to była lista a nie słownik")

                    """

                    if entity[0] == "housing_type":
                        if user.housing_type is None:
                            user.set_housing_type(entity[1])
                        else:
                            new = translate(entity[1], "Q")
                            if user.housing_type != new:
                                response.ask_if_new_housing_type(message, user, bot, new)
                            else:
                                logging.info("Housing_type already has this value.")

                    if entity[0] == "location":
                        
                    if user.wants_more_locations:
                        if entity[0] == "boolean" and entity[1] == "no":
                            user.wants_more_locations = False

                    """

                    # TODO!
                    # if user.wants_more_features and user.asked_for_features and entity[0] == "boolean" and entity[1] == "no":
                    #     user.wants_more_features = False

                    # TODO!
                    if user.context == "show_input_data":
                        if entity[0] == "boolean" and entity[1] == "yes":
                            user.confirmed_data = True
                            logging.info(f"[User {user.facebook_id} Update] confirmed_data = True")

                        elif entity[0] == "boolean" and entity[1] == "no":
                            user.confirmed_data = False
                            logging.info(f"[User {user.facebook_id} Update] confirmed_data = False")
                            # TODO dead end.


        if not message.NLP_intent and not message.NLP_entities:   # ma nlp, ale intent=none i brak mu entities, więc freetext do wyłapania

            print("____________________ TEST 001 ________________________")

            if user.city is None:
                print("____________________ TEST 002 ________________________")
                try:
                    user.set_city(recognize_location(message.text).city)
                except:
                    pass

            elif user.latitude == 0 and message.type == "LocationAnswer":
                print("____________________ TEST 003 ________________________")

                user.add_location(lat=message.latitude, long=message.longitude)

            elif user.latitude == 0:
                print("____________________ TEST 004 ________________________")

                try:
                    user.add_location(location=recognize_location(message.text).city)
                except:
                    pass

            elif user.housing_type is None:
                print("____________________ TEST 005 ________________________")

                user.set_housing_type(message.text)

            elif user.price_limit is None:
                print("____________________ TEST 006 ________________________")

                user.set_price_limit(message.text)

            elif user.wants_more_features:
                print("____________________ TEST 007 ________________________")

                user.add_feature(message.text)

            elif user.wants_more_features and entity[0] == "boolean" and entity[1] == "no":
                print("____________________ TEST 008 ________________________")

                user.wants_more_features = False
                logging.info(f"[User {user.facebook_id} Update] wants_more_features = False")
            else:
                print("____________________ TEST 009 ________________________")

                response.default_message(message, user, bot)
    else:
        logging.warning("Didn't catch what user said! ")


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
        logging.debug(f"replaced {str(if_contains)} with {str(replace_with)}")
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
