
""" Functions enabling the Bot to understand messages and intents. """

# import public modules:
import os
import random
import logging
from flask import Flask, request
# import from own modules:
from Flask_app import local_tokens, database, witai
if local_tokens: from Bot import tokens_local as tokens
else: from Bot import tokens
if database: from Databases import mysql_connection as db
from Bot.bot_responses import *
from Bot.facebook_webhooks import Bot

log = logging.getLogger(os.path.basename(__file__))

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

def best_entity(message, minimum=0.90):
    """ Return best matching entity from NLP or None. """
    try:
        entities = list(message.get('nlp').get('entities').keys())
        #entities.remove("sentiment")
        confidence = []
        for c in list(message.get('nlp').get('entities').values()):
            confidence.append(c[0]['confidence'])
        if max(confidence)>minimum:
            # create dictionary entity:confidence:
            iterable = zip(entities, confidence)
            pairs = {key: value for (key, value) in iterable}
            best_match = max(pairs, key=pairs.get)
            return [best_match, str(max(confidence))]
        else:
            return None
    except:
        return None


#Set of intents and patterns to recognize them:
pattern_dictionary = {
        'greetings': [r'\b(hi|h[ea]+l+?o|h[ea]+[yj]+|yo+|welcome|(good)?\s?(morning?|evenin?)|hola|howdy|shalom|salam|czesc|witaj|siemk?a|marhaba|salut)\b'],
        #'greetings': [r'\b(hi|h[ea]+l+?o|h[ea]+[yj]+|yo+|welcome|(good)?\s?(morning?|evenin?)|hola|howdy|shalom|salam|czesc|witaj|siemk?a|marhaba|salut)\b', r'(\🖐|\🖖|\👋|\🤙)'],     #🖐🏻,🖖🏻,👋🏻,🤙🏻,🖐🏼,🖖🏼,👋🏼,🤙🏼,🖐🏽,🖖🏽,👋🏽,🤙🏽,🖐🏾,🖖🏾,👋🏾,🤙🏾,🖐🏿,🖖🏿,👋🏿,🤙🏿
        'yes': r'\b(yes|si|ok|kk|ok[ae]y|confirm|good)\b',
        #'yes': [r'\b(yes|si|ok|kk|ok[ae]y|confirm)\b',r'(\✔️|\☑️|\👍|\👌)'],    #👍🏻,👌🏻,👍🏼,👌🏼,👍🏽,👌🏽,👍🏾,👌🏾,👍🏿,👌🏿
        'no': r'\b(n+o+|decline|negative|n+o+pe)\b',
        #'no': [r'\b(n+o+|decline|negative|n+o+pe)\b', r'\👎'],    #👎🏻,👎🏼,👎🏽,👎🏾,👎🏿
        'maybe' : r'\b(don\'?t\sknow?|maybe|perhaps?|not\ssure|y+)\b',
        'curse' : [r'\b(fuck|kurwa)\b', r'pierd[oa]l', r'\bass'],
        #'curse' : [r'\b(fuck|kurwa)\b', r'pierd[oa]l', r'\bass', r'\🖕'],  #🖕🏻,🖕🏼,🖕🏽,🖕🏾,🖕🏿
        'uname' : [r'y?o?ur\sname\??', r'(how|what)[\s\S]{1,15}call(ing)?\sy?o?u\??'],
        'ureal' : r'\by?o?u\s(real|true|bot|ai|human|person|man)\b',
        "secret" : r'(secret|password|key)',
        "rpsgame" : [r'start', r'play', r'game', r'rock ?paper ?scissors', r'rock', r'✊', r'paper', r'✋', r'scissors', r'✌'],
        "love" : r'love',
        #"love" : [r'love',r'(\❤️|\🧡|\💛|\💚|\💙|\💜|\🖤)'],
        'test_list_message': r'list message',
        'test_button_message': r'button message',
        'test_generic_message': r'generic message',
        'test_quick_replies': r'quick replies',
        'bye': r'(bye|exit|quit|end)'
    }


def recognize_sticker(sticker_id):
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
