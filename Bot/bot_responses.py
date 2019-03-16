#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

# import public modules:
import os
import re
import json
import random
import logging
from flask import Flask, request
# import from own modules:
from Dispatcher_app import local_tokens, database, witai
if local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
if database: from Databases import mysql_connection as db
from Bot.facebook_webhooks import Bot

log = logging.getLogger(os.path.basename(__file__))

#Set of responses for particular intents:
def responder(intent, user_message="", userid="", bot=""):
    switcher = {
        "greetings":   greetings,
        "yes":         yes,
        "no":          no,
        "maybe":       maybe,
        "curse":       curse,
        "uname":       uname,
        "ureal":       ureal,
        "thanks":      thanks,
        "datetime":    datetime,
        "money":       money,
        "phone":       phone,
        "email":       email,
        "distance":    distance,
        "quantity":    quantity,
        "temperature": temperature,
        "location":    location,
        "duration":    duration,
        "url":         url,
        "sentiment":   sentiment,
        "test_list_message":    test_list_message,
        "test_button_message":  test_button_message,
        "test_generic_message": test_generic_message,
        "test_quick_replies":   test_quick_replies,
        "bye":          bye
    }
    # Get the function from switcher dictionary
    func = switcher.get(intent, default_message)
    # previous version with bug: func = switcher.get(intent, lambda user_message, userid, bot : default_message)
    return func(user_message, userid, bot)

def default_message(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["przepraszam?",
                "wybacz, nie rozumiem, czy mógłbyś powtórzyć",
                "słucham?"]
    elif language=="EN":
        return ["Please rephrase it.",
                "Sorry, I have no idea what you mean by that.",
                "Excuse me?",
                "Sorry, I don't get it",
                "pardon me?"]

def greetings(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["{0}! Jak mogę Ci pomóc?".format(user_message.split(' ', 1)[0].capitalize()),
                "{0}! Co u Ciebie?".format(user_message.split(' ', 1)[0].capitalize())]
    elif language=="EN":
        return ["{0}! How are you doing?".format(user_message.split(' ', 1)[0].capitalize()),
                "{0}! How are you doing?".format(user_message.split(' ', 1)[0].capitalize())]

def yes(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["ok",
                "super",
                "jasne",
                "zanotowałem",
                "(y)"]
    elif language=="EN":
        return ["You confirm, good",
                "great",
                "perfect",
                "good",
                "(y)"]

def no(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return [":(",
                "nieeee",
                "dlaczego nie?",
                "trudno"]
    elif language=="EN":
        return [":(",
                "nooo",
                "why not?",
                "that's a pitty"]

def maybe(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "'{0}'? Potrzebuejesz chwilę, żeby się zastanowić?".format(user_message.capitalize())
    elif language=="EN":
        return "'{0}'? Do you need some time to think about it?".format(user_message.capitalize())

def curse(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["proszę, nie używaj takich słów",
                "spokojnie",
                "czy masz zamiar mnie obrazić?",
                "przykro mi"]
    elif language=="EN":
        return ["you {0}".format(user_message, userid="", bot=""),
                "not nice",
                "please calm down",
                "why are you so mean?"]

def uname(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["Mówią na mnie Roomek 😎",
                "dla Ciebie Roomek 😎",
                "Roomek, a Ty?",
                "Jestem Roomek, jestem 🤖"]
    elif language=="EN":
        return ["My name is Roomek 😎",
                "call me Roomek 😎",
                "Roomek, and you?",
                "I'm Rooomek, a bot 🤖"]

def ureal(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["Myślę więc jestem :)",
                "Nie, jestem botem 🤖",
                "Jestem 👽"]
    elif language=="EN":
        return ["Cogito Ergo Sum",
                "What is real?",
                "No, I'm a bot 🤖",
                "I'm an 👽"]

def thanks(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["Nie ma sprawy!",
                "Cała przyjemność po mojej stronie!",
                "Nie ma za co",
                "od tego jestem :)"]
    elif language=="EN":
        return ["No problem",
                "My pleasure!",
                "That's what I do"]

def datetime(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "Zerknę w kalendarz."
    elif language=="EN":
        return "Let me check in my calendar."

def money(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "💰💰💰!"
    elif language=="EN":
        return "💰💰💰!"

def phone(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "To Twój numer 📞?"
    elif language=="EN":
        return "Is that your phone 📞?"

def email(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "To Twój email?"
    elif language=="EN":
        return "Is that your email?"

def distance(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "🚗"
    elif language=="EN":
        return "🚗"

def quantity(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "ok, that's a lot."
    elif language=="EN":
        return "ok, that's a lot."

def temperature(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "brrr ⛄️"
    elif language=="EN":
        return "brrr ⛄️"

def location(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "sprawdzę na mapie"
    elif language=="EN":
        return "I will check where it is on the map"

def duration(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return "Ja mam sporo czasu ⌚️"
    elif language=="EN":
        return "I got plenty of time ⌚️"

def url(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["mam to otworzyć?",
                "co to za link?"]
    elif language=="EN":
        return ["you mind if I don't open that?",
                "cool link, what's that?"]

def sentiment(user_message, userid="", bot="", language="PL"):
    if language=="PL":
        return ["ehhh...",
                "czasami robię się sentymentalny"]
    elif language=="EN":
        return ["ehhh...",
                "good old times"]

def test_list_message(user_message, userid="", bot="", language="PL"):
    if database: db.add_conversation(userid, 'User', user_message)
    if database: db.add_conversation(userid, 'Bot', '<sent list message>')
    bot.fb_send_list_message(userid, ['test_value_1', 'test_value_2'], ['test_value_3', 'test_value_4']) #TODO not working
    return "already sent"

def test_button_message(user_message, userid="", bot="", language="PL"):
    if database: db.add_conversation(userid, 'User', user_message)
    if database: db.add_conversation(userid, 'Bot', '<sent button message>')
    bot.fb_send_button_message(userid, "test", ['test_value_1', 'test_value_2']) #TODO not working
    return "already sent"

def test_generic_message(user_message, userid="", bot="", language="PL"):
    if database: db.add_conversation(userid, 'User', user_message)
    if database: db.add_conversation(userid, 'Bot', '<sent generic message>')
    # temp: bot.fb_send_test_message(userid, ['test_value_1', 'test_value_2'])
    bot.fb_send_generic_message(userid, ['Test_value_1', 'Test_value_2'])
    # bot.fb_send_generic_message(userid, [['Title1','Subtitle1','image_url1',buttons=['title1','url1']],['Title2','Subtitle2','image_url2',buttons=['title2','url2']]])
    return "already sent"

def test_quick_replies(user_message, userid="", bot="", language="PL"):
    if database: db.add_conversation(userid, 'User', user_message)
    if database: db.add_conversation(userid, 'Bot', '<sent quick replies message>')
    bot.fb_send_quick_replies(userid, "This is a test of quick replies", ['test_value_1', 'test_value_2', 'test_value_3']) #TODO test if working
    return "already sent"

def bye(user_message, userid="", bot="", language="PL"):
    return "You going already? Goodbye then!"

def sticker_response(sticker_name, userid, bot):
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        yes(sticker_name, userid, bot)
        return "already sent"
    else:
        if language=="PL":
            return [{
                'cactus' : "Czy ten kaktus ma drugie znaczenie? :)",
                'dogo' : "Słodki :)",
                'dogo_great' : "dzięki!",
                'bird' : "Nie lubię ptaków. Szczególnie gołębi",
                'cat' : "Miauuuu :)",
                'monkey' : "🙈 🙉 🙊",
                'emoji' : ":)",
                'turtle' : "to mi przypomina mojego żółwia...",
                'office' : "hehe",
                'chicken' : "koko?",
                'fox' : "what does the fox say?!",
                'kungfurry' : "Kung fury! 👊👊👊",
                'sloth' : "moooogggęęę woooollllniiiieeeejjj"
             }.get(sticker_name, ["Fajna naklejka :)", "Czy to jest opowiedź na moje pytanie?"]), sticker_name]
        elif language=="EN":
            return [{
                'cactus' : "Does this cactus have a second meaning? :)",
                'dogo' : "Cute dog :)",
                'dogo_great' : "I know it's great, that's what I do!",
                'bird' : "I don't like birds, including doves",
                'cat' : "Miauuuu :)",
                'monkey' : "🙈 🙉 🙊",
                'emoji' : "Thats a big emoji",
                'turtle' : "It reminds me of my turtle... R.I.P",
                'office' : "hehe, office stickers from the 90s are so old-school",
                'chicken' : "koko?",
                'fox' : "what does the fox say?!",
                'kungfurry' : "Kung fury! 👊👊👊",
                'sloth' : "cute sloth"
             }.get(sticker_name, ["Cool sticker.", "I don't know how to relate to that sticker"]), sticker_name]
