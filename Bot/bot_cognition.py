#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions enabling the Bot to understand messages and intents. """
from geopy.geocoders import Nominatim
from geopy.point import Point
# from Bot.bot_responses_PL import *

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


def recognize_location(location):
    geolocator = Nominatim(user_agent="Roomek")
    loc = geolocator.geocode(location, viewbox=[Point(40, 10), Point(60, 30)], bounded=True, country_codes=['pl'], addressdetails = True)
    return loc
    # (loc.raw)
    # TODO pass attributes like street, boundingbox etc.

# recognize_location("twarda 18")
