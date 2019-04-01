#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" How the Bot reacts to certain messages, depending on the context. """

import os
import random
import logging
log = logging.getLogger(os.path.basename(__file__))


# Set of responses for particular intents:
def respond(message, bot):
    if message.NLP_intent == "greeting": greeting(message, bot)
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


def default_message(message, bot, language="PL"):
    if language == "PL":
        response = random.choice([
            "przepraszam?",
            "wybacz, nie rozumiem, czy mógłbyś powtórzyć innymi słowami?",
            "słucham?",
            "jak mogę Ci pomoć?"])
    elif language == "EN":
        response = random.choice([
            "Please rephrase it.",
            "Sorry, I have no idea what you mean by that.",
            "Excuse me?",
            "Sorry, I don't get it",
            "pardon me?"])
    bot.fb_send_text_message(str(message.senderID), response)


def greeting(message, bot, language="PL"):
    if language == "PL":
        response = random.choice([
        "{0}! Jestem Roomek i jestem na bieżąco z rynkiem nieruchomości.".format(message.text.split(' ', 1)[0].capitalize()),
        "{0}! Nazywam się Roomek i zajmuję się znajdywaniem najlepszych nieruchomości.".format(message.text.split(' ', 1)[0].capitalize())
        ])
    bot.fb_send_text_message(str(message.senderID), response)
    bot.fb_send_quick_replies(message.senderID, "Jak mogę Ci dzisiaj pomóc?", ['Szukam pokoju na wynajem', 'Chcę kupić mieszkanie'])


def ask_for_housing_type(message, bot, language="PL"):
    bot.fb_fake_typing(message.senderID, 0.5)
    if language == "PL":
        bot.fb_send_quick_replies(message.senderID, "Jakie typu lokal Cię interesuje?", ['pokój', 'mieszkanie', 'kawalerka', 'dom wolnostojący'])


def ask_for_location(message, bot, language="PL"):
    bot.fb_fake_typing(message.senderID, 0.5)
    if language == "PL":
        bot.fb_send_quick_location(message.senderID, reply_message = "Gdzie chciałbyś mieszkać?")


def ask_for_money_limit(message, bot, language="PL"):
    bot.fb_fake_typing(message.senderID, 0.5)
    if language == "PL":
        bot.fb_send_quick_replies(message.senderID, "Ile jesteś w stanie płacić?", ['<800zł', '<1000', '<1500', '<2000'])


def show_offers(message, bot, language="PL"):
    bot.fb_fake_typing(message.senderID, 0.8)
    if language == "PL":
        bot.fb_send_text_message(str(message.senderID), "Znalazłem dla Ciebie takie oferty:")
        bot.fb_fake_typing(message.senderID, 0.4)
        bot.fb_send_generic_message(userid, ['Oferta 1', 'Oferta 2', 'Oferta 3'])


def yes(message, bot, language="PL"):
    if language == "PL":
        return ["ok",
                "super",
                "jasne",
                "zanotowałem",
                "(y)"]
    elif language == "EN":
        return ["You confirm, good",
                "great",
                "perfect",
                "good",
                "(y)"]


def no(message, bot, language="PL"):
    if language == "PL":
        return [":(",
                "nieeee",
                "dlaczego nie?",
                "trudno"]
    elif language == "EN":
        return [":(",
                "nooo",
                "why not?",
                "that's a pitty"]


def maybe(message, bot, language="PL"):
    if language == "PL":
        return "'{0}'? Potrzebuejesz chwilę, żeby się zastanowić?".format(message.text.capitalize())
    elif language == "EN":
        return "'{0}'? Do you need some time to think about it?".format(message.text.capitalize())


def curse(message, bot, language="PL"):
    if language == "PL":
        return ["proszę, nie używaj takich słów",
                "spokojnie",
                "czy masz zamiar mnie obrazić?",
                "przykro mi"]
    elif language == "EN":
        return ["not nice",
                "please calm down",
                "why are you so mean?"]


def uname(message, bot, language="PL"):
    if language == "PL":
        return ["Mówią na mnie Roomek 😎",
                "dla Ciebie Roomek 😎",
                "Roomek, a Ty?",
                "Jestem Roomek i jestem 🤖"]
    elif language == "EN":
        return ["My name is Roomek 😎",
                "call me Roomek 😎",
                "Roomek, and you?",
                "I'm Rooomek and I'm a bot 🤖"]


def ureal(message, bot, language="PL"):
    if language == "PL":
        return ["Myślę więc jestem :)",
                "Nie, jestem botem 🤖",
                "Jestem 👽"]
    elif language == "EN":
        return ["Cogito Ergo Sum",
                "What is real?",
                "No, I'm a bot 🤖",
                "I'm an 👽"]


def thanks(message, bot, language="PL"):
    if language == "PL":
        return ["Nie ma sprawy!",
                "Cała przyjemność po mojej stronie!",
                "Nie ma za co",
                "od tego jestem :)"]
    elif language == "EN":
        return ["No problem",
                "My pleasure!",
                "That's what I do"]


def datetime(message, bot, language="PL"):
    if language == "PL":
        return "Zerknę w kalendarz."
    elif language == "EN":
        return "Let me check in my calendar."


def money(message, bot, language="PL"):
    if language == "PL":
        return "💰💰💰!"
    elif language == "EN":
        return "💰💰💰!"


def location(message, bot, language="PL"):
    if language == "PL":
        return "sprawdzę na mapie"
    elif language == "EN":
        return "I will check where it is on the map"


def duration(message, bot, language="PL"):
    if language == "PL":
        return "Ja mam sporo czasu ⌚️"
    elif language == "EN":
        return "I got plenty of time ⌚️"


def url(message, bot, language="PL"):
    if language == "PL":
        return ["mam to otworzyć?",
                "co to za link?"]
    elif language == "EN":
        return ["you mind if I don't open that?",
                "cool link, what's that?"]


def bye(message, bot, language="PL"):
    return "You going already? Goodbye then!"


def sticker_response(message, bot, language="PL"):
    if message.stickerName == 'thumb' or message.stickerName == 'thumb+' or message.stickerName == 'thumb++':
        yes(message.stickerName, message.senderID, bot)
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
             }.get(message.stickerName, ["Fajna naklejka :)", "Czy to jest opowiedź na moje pytanie?"]), message.stickerName]
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
             }.get(message.stickerName, ["Cool sticker.", "I don't know how to relate to that sticker"]), message.stickerName]
