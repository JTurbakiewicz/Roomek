#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from Bot.cognition import *
from Dispatcher_app import fake_typing

# TODO do the decorator and try to input (message, bot):
def response_decorator(original_function):
    def wrapper(message, bot, *args, **kwargs):

        # Do something BEFORE the original function:
        if fake_typing: bot.fb_fake_typing(message.senderID, 0.4)

        # The original function:
        original_function(message, bot)

        # Do something AFTER the original function:
        # TODO: bot.fb_send_text_message(str(message.senderID), response)

    return wrapper


@response_decorator
def default_message(message, bot):
    response = random.choice([
        "przepraszam?",
        "wybacz, nie rozumiem, czy mógłbyś powtórzyć innymi słowami?",
        "słucham?",
        "powiedz proszę jak mógłbym Ci pomóc"])
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def greeting(message, bot):
    response = random.choice([
        "{0}! Jestem Roomek i jestem na bieżąco z rynkiem nieruchomości.".format(message.text.split(' ', 1)[0].capitalize()),
        "{0}! Nazywam się Roomek i zajmuję się znajdywaniem najlepszych nieruchomości.".format(message.text.split(' ', 1)[0].capitalize())
        ])
    bot.fb_send_text_message(str(message.senderID), response)
    bot.fb_send_quick_replies(message.senderID, "Jak mogę Ci dzisiaj pomóc?", ['🔎 Szukam pokoju', '🔎 Szukam mieszkania', 'Sprzedaję mieszkanie'])


@response_decorator
def ask_for_housing_type(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Jakiego typu lokal Cię interesuje?", ['🚪 pokój', '🏢 mieszkanie', '🐌 kawalerka', '🏠 dom wolnostojący'])


@response_decorator
def ask_for_city(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Które miasto Cię interesuje?", ['Warszawa', 'Kraków', 'Łódź', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin', 'Bydgoszcz', 'Białystok'])


@response_decorator
def ask_for_features(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Czy masz jakieś szczególne preferencje?", ['Nie, pokaż oferty', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'garaż', '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])


@response_decorator
def ask_for_more_features(message, bot):
    question = random.choice(["Coś oprócz tego?", "Ok, jeszcze coś?", "Zanotowałem, chciałbyś coś dodać?"])
    bot.fb_send_quick_replies(message.senderID, question, ['Nie, wystarczy', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'garaż', '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])
    # TODO powinno wiedzieć jakie już padły


@response_decorator
def ask_for_location(message, bot):
    bot.fb_send_quick_replies(message.senderID, reply_message="Gdzie chciałbyś mieszkać?", replies=['🎯 blisko centrum', 'Mokotów', 'Wola'], location=True)
    # TODO powinno sugerować dzielnice na bazie miasta, a nie default (nominatim get lower level nodes like suburb)


@response_decorator
def ask_more_locations(message, bot):
    question = random.choice(["Czy chciałbyś dodać jeszcze jakieś miejsce?","Zanotowałem, coś oprócz tego?"])
    bot.fb_send_quick_replies(message.senderID, reply_message=question, replies=['Nie', '🎯 blisko centrum', 'Mokotów', 'Wola'], location=True)
    # TODO tez powinno sugerować dzielnice i wiedzieć co już padło

@response_decorator
def ask_for_price_limit(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Ile jesteś w stanie płacić?", ['<800zł', '<1000zł', '<1500zł', '<2000zł','💸 dowolna kwota'])


@response_decorator
def show_input_data(message, bot):
    message.user.shown_input = True
    response1 = "Zanotowałem, że interesuje Cię {0} w {1} w okolicy {2}".format(message.housing_type, message.user.city, message.user.location)
    bot.fb_send_text_message(str(message.senderID), response1)
    response2 = "które ma {0} i kosztuje do {1}zł".format(str(message.features), message.user.price_limit)
    bot.fb_send_text_message(str(message.senderID), response2)
    # TODO add more params...
    bot.fb_send_quick_replies(message.senderID, "Czy wszystko się zgadza?",
                              ['Tak, pokaż oferty 🔮', 'Tak, chcę coś dodać', 'Nie'])


@response_decorator
def ask_what_wrong(message, bot):
    bot.fb_send_quick_replies(message.senderID, "Coś pomyliłem?", ['nie, jest ok', 'zła okolica', 'złe parametry', 'zła cena'])


@response_decorator
def show_offers(message, bot):
    bot.fb_send_text_message(str(message.senderID), "Znalazłem dla Ciebie takie oferty:")
    if fake_typing: bot.fb_fake_typing(message.senderID, 0.4)
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
def dead_end(message, bot):
    response = "Ups, to ślepy zaułek tej konwersacji!"
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def unable_to_answer(message, bot):
    response = "Wybacz, na ten moment potrafię jedynie wyszukiwać najlepsze dostępne oferty wynajmu."
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
    response = random.choice([
        "Nie ma sprawy!",
        "Cała przyjemność po mojej stronie!",
        "Nie ma za co",
        "od tego jestem :)"
    ])
    bot.fb_send_text_message(str(message.senderID), response)


@response_decorator
def url(message, bot):
    response = random.choice([
        "mam to otworzyć?",
        "co to za link?"
    ])
    bot.fb_send_text_message(str(message.senderID), response)


# @response_decorator
def sticker_response(message, bot):
    sticker_name = recognize_sticker(message.stickerID)
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        yes(message, bot)
    else:
        response = {
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
         }.get(sticker_name, ["Fajna naklejka :)", "Czy to jest opowiedź na moje pytanie?"])
        bot.fb_send_text_message(str(message.senderID), response)
