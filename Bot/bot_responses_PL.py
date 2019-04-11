#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from Bot.bot_cognition import *
log = logging.getLogger(os.path.basename(__file__))


# TODO do the decorator and try to input (message, bot):
def response_decorator(original_function):
    def new_function(*args, **kwargs):
        bot.fb_fake_typing(message.senderID, 0.5)
        print("cokolwiek")
        return cokolwiek

    return new_function


@response_decorator
def default_message(message, bot):
    response = random.choice([
        "przepraszam?",
        "wybacz, nie rozumiem, czy mógłbyś powtórzyć innymi słowami?",
        "słucham?",
        "jak mogę Ci pomoć?"])
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def greeting(message, bot):
    response = random.choice([
        "{0}! Jestem Roomek i jestem na bieżąco z rynkiem nieruchomości.".format(message.text.split(' ', 1)[0].capitalize()),
        "{0}! Nazywam się Roomek i zajmuję się znajdywaniem najlepszych nieruchomości.".format(message.text.split(' ', 1)[0].capitalize())
        ])
    bot.fb_send_text_message(str(message.senderID), response)
    bot.fb_send_quick_replies(message.senderID, "Jak mogę Ci dzisiaj pomóc?", ['Szukam pokoju', 'Sprzedaje mieszkanie'])


@response_decorator
def ask_for_housing_type(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Jakie typu lokal Cię interesuje?", ['pokój', 'mieszkanie', 'kawalerka', 'dom wolnostojący'])


@response_decorator
def ask_for_location(message, bot):
    bot.fb_send_quick_location(message.senderID, reply_message = "Gdzie chciałbyś mieszkać?")


@response_decorator
def ask_for_money_limit(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Ile jesteś w stanie płacić?", ['<800zł', '<1000', '<1500', '<2000'])


@response_decorator
def show_offers(message, bot):
    bot.fb_send_text_message(str(message.senderID), "Znalazłem dla Ciebie takie oferty:")
    bot.fb_fake_typing(message.senderID, 0.4)
    bot.fb_send_generic_message(userid, ['Oferta 1', 'Oferta 2', 'Oferta 3'])


@response_decorator
def yes(message, bot):
    response = random.choice([
        "ok",
        "super",
        "jasne",
        "zanotowałem",
        "(y)"
    ])
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def no(message, bot):
    response = random.choice([
        ":(",
        "nieeee",
        "dlaczego nie?",
        "trudno"
    ])
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def maybe(message, bot):
    response = "'{0}'? Potrzebuejesz chwilę, żeby się zastanowić?".format(message.text.capitalize())
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def curse(message, bot):
    response = random.choice([
        "proszę, nie używaj takich słów",
        "spokojnie",
        "czy masz zamiar mnie obrazić?",
        "przykro mi"
    ])
    bot.fb_send_text_message(str(message.senderID), response)

# TODO!
@response_decorator
def thanks(message, bot):
    if language == "PL":
        return ["Nie ma sprawy!",
                "Cała przyjemność po mojej stronie!",
                "Nie ma za co",
                "od tego jestem :)"]
    elif language == "EN":
        return ["No problem",
                "My pleasure!",
                "That's what I do"]

# TODO!
@response_decorator
def location(message, bot):
    if language == "PL":
        return "sprawdzę na mapie"
    elif language == "EN":
        return "I will check where it is on the map"

# TODO!
@response_decorator
def url(message, bot):
    if language == "PL":
        return ["mam to otworzyć?",
                "co to za link?"]
    elif language == "EN":
        return ["you mind if I don't open that?",
                "cool link, what's that?"]

# TODO!
@response_decorator
def bye(message, bot):
    return "You going already? Goodbye then!"

# TODO!
@response_decorator
def sticker_response(message, bot):
    sticker_name = recognize_sticker(message.stickerID)
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        yes(sticker_name, message.senderID, bot)
        return "already sent"
    else:
        if language == "PL":
            return [{
                'cactus': "Czy ten kaktus ma drugie znaczenie? :)",
                'dogo': "Słodki :)",
                'dogo_great': "dzięki!",
                'bird': "Nie lubię ptaków. Szczególnie gołębi",
                'cat': "Miauuuu :)",
                'monkey': "🙈 🙉 🙊",
                'emoji': ":)",
                'turtle': "to mi przypomina mojego żółwia...",
                'office': "hehe",
                'chicken': "koko?",
                'fox': "what does the fox say?!",
                'kungfurry': "Kung fury! 👊👊👊",
                'sloth': "moooogggęęę woooollllniiiieeeejjj"
             }.get(sticker_name, ["Fajna naklejka :)", "Czy to jest opowiedź na moje pytanie?"]), sticker_name]
        elif language == "EN":
            return [{
                'cactus': "Does this cactus have a second meaning? :)",
                'dogo': "Cute dog :)",
                'dogo_great': "I know it's great, that's what I do!",
                'bird': "I don't like birds, including doves",
                'cat': "Miauuuu :)",
                'monkey': "🙈 🙉 🙊",
                'emoji': "Thats a big emoji",
                'turtle': "It reminds me of my turtle... R.I.P",
                'office': "hehe, office stickers from the 90s are so old-school",
                'chicken': "koko?",
                'fox': "what does the fox say?!",
                'kungfurry': "Kung fury! 👊👊👊",
                'sloth': "cute sloth"
             }.get(sticker_name, ["Cool sticker.", "I don't know how to relate to that sticker"]), sticker_name]
