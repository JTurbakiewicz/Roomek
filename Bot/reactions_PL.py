#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from Bot.cognition import *
from settings import *
#from OfferBrowser.best_offer import best_offer
from OfferParser.translator import translate
from pprint import pprint, pformat


def response_decorator(original_function):
    def wrapper(message, user, bot, *args, **kwargs):

        # Do something BEFORE the original function:
        if fake_typing: bot.fb_fake_typing(message.facebook_id, 0.4)
        show_user_object(message, user, bot)
        # show_message_object(message, user, bot)
        user.set_context(original_function.__name__)
        user.increment()

        # The original function:

        original_function(message, user, bot, *args, **kwargs)

        # Do something AFTER the original function:
        # TODO: bot.fb_send_text_message(str(message.facebook_id), response)

    return wrapper


@response_decorator
def default_message(message, user, bot):
    response = random.choice([
        "przepraszam?",
        "wybacz, nie rozumiem, czy mógłbyś powtórzyć innymi słowami?",
        "słucham?",
        "powiedz proszę jak mógłbym Ci pomóc"])
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def greeting(message, user, bot):
    response = random.choice([
        "{0}! Jestem Roomek i jestem na bieżąco z rynkiem nieruchomości.".format(message.text.split(' ', 1)[0].capitalize()),
        "{0}! Nazywam się Roomek i zajmuję się znajdywaniem najlepszych nieruchomości.".format(message.text.split(' ', 1)[0].capitalize())
        ])
    bot.fb_send_text_message(str(message.facebook_id), response)
    bot.fb_send_quick_replies(message.facebook_id, "Jak mogę Ci dzisiaj pomóc?", ['🔎 Szukam pokoju', '🔎 Szukam mieszkania', 'Sprzedaję mieszkanie'])


@response_decorator
def ask_for_housing_type(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Jakiego typu lokal Cię interesuje?", ['🚪 pokój', '🏢 mieszkanie', '🐌 kawalerka', '🏠 dom wolnostojący'])

@response_decorator
def ask_if_new_housing_type(message, user, bot, new_value):
    bot.fb_send_quick_replies(message.facebook_id, "Czy chcesz zmienić typ z {0} na {1}?".format(user.housing_type, new_value), ['Tak', 'Nie'])

@response_decorator
def ask_for_city(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Które miasto Cię interesuje?", ['Warszawa', 'Kraków', 'Łódź', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin', 'Bydgoszcz', 'Białystok'])

@response_decorator
def ask_for_features(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Czy masz jakieś szczególne preferencje?", ['Nie, pokaż oferty', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'garaż', '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])


@response_decorator
def ask_for_more_features(message, user, bot):
    question = random.choice(["Coś oprócz tego?", "Ok, jeszcze coś?", "Zanotowałem, chciałbyś coś dodać?"])
    bot.fb_send_quick_replies(message.facebook_id, question, ['Nie, wystarczy', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'garaż', '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])
    # TODO powinno wiedzieć jakie już padły


@response_decorator
def ask_for_location(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, reply_message="Gdzie chciałbyś mieszkać?", replies=['🎯 blisko centrum', 'Mokotów', 'Wola'], location=True)
    # TODO powinno sugerować dzielnice na bazie miasta, a nie default (nominatim get lower level nodes like suburb)


@response_decorator
def ask_more_locations(message, user, bot):
    question = random.choice(["Czy chciałbyś dodać jeszcze jakieś miejsce?","Zanotowałem, coś oprócz tego?"])
    bot.fb_send_quick_replies(message.facebook_id, reply_message=question, replies=['Nie', '🎯 blisko centrum', 'Mokotów', 'Wola'], location=True)
    # TODO tez powinno sugerować dzielnice i wiedzieć co już padło

@response_decorator
def ask_for_price_limit(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Ile jesteś w stanie płacić? (wraz z ew. czynszem i opłatami)", ['<800zł', '<1000zł', '<1500zł', '<2000zł','💸 dowolna kwota'])


@response_decorator
def show_input_data(message, user, bot):
    user.shown_input = True
    housing_type = translate(user.housing_type, "D")
    print(housing_type)
    response1 = "Zanotowałem, że szukasz {0} w mieście {1} w okolicy {2} ({3},{4})".format(housing_type, user.city, user.location, user.location_latitude, user.location_longitude)
    bot.fb_send_text_message(str(message.facebook_id), response1)
    response2 = "które ma {0} i kosztuje do {1}zł.".format(str(user.features), user.price_limit)
    bot.fb_send_text_message(str(message.facebook_id), response2)
    # TODO add more params...
    logging.debug("ADD OTHER FEATURES: "+str(message.user))
    bot.fb_send_quick_replies(message.facebook_id, "Czy wszystko się zgadza?",
                              ['Tak, pokaż oferty 🔮', 'Tak, chcę coś dodać', 'Nie'])


@response_decorator
def ask_what_wrong(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Coś pomyliłem?", ['nie, jest ok', 'zła okolica', 'złe parametry', 'zła cena'])


@response_decorator
def show_offers(message, user, bot):
    # bot.fb_send_text_message(str(message.facebook_id), "Znalazłem dla Ciebie takie oferty:")
    if fake_typing: bot.fb_fake_typing(message.facebook_id, 0.4)
    #best = best_offer(user_obj=message.user, count=3)
    bot.fb_send_text_message(str(message.facebook_id), best[0])
    bot.fb_send_text_message(str(message.facebook_id), best[1])
    bot.fb_send_text_message(str(message.facebook_id), best[2])
    bot.fb_send_generic_message(message.facebook_id, ['Oferta 1', 'Oferta 2', 'Oferta 3'])


@response_decorator
def yes(message, user, bot):
    response = random.choice([
        "ok",
        "super",
        "jasne",
        "zanotowałem",
        "(y)"
    ])
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def no(message, user, bot):
    response = random.choice([
        ":(",
        "nieeee",
        "dlaczego nie?",
        "trudno"
    ])
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def maybe(message, user, bot):
    response = "'{0}'? Potrzebuejesz chwilę, żeby się zastanowić?".format(message.text.capitalize())
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def dead_end(message, user, bot):
    response = "Ups, to ślepy zaułek tej konwersacji!"
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def unable_to_answer(message, user, bot):
    response = "Wybacz, na ten moment potrafię jedynie wyszukiwać najlepsze dostępne oferty wynajmu."
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def curse(message, user, bot):
    response = random.choice([
        "proszę, nie używaj takich słów",
        "spokojnie",
        "czy masz zamiar mnie obrazić?",
        "przykro mi"
    ])
    bot.fb_send_text_message(str(message.facebook_id), response)


# TODO!
@response_decorator
def thanks(message, user, bot):
    response = random.choice([
        "Nie ma sprawy!",
        "Cała przyjemność po mojej stronie!",
        "Nie ma za co",
        "od tego jestem :)"
    ])
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def url(message, user, bot):
    response = random.choice([
        "mam to otworzyć?",
        "co to za link?"
    ])
    bot.fb_send_text_message(str(message.facebook_id), response)


# @response_decorator
def sticker_response(message, user, bot):
    sticker_name = recognize_sticker(message.stickerID)
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        yes(message, user, bot)
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
        bot.fb_send_text_message(str(message.facebook_id), response)


def show_user_object(message, user, bot):

    reply = "*MESSAGE*\n"
    reply += "_recipientID =_ " + str(message.facebook_id) + "\n"
    try:
        reply += "_NLP intents =_ " + str(message.NLP_intent) + "\n"
        reply += "_NLP entities =_ " + str(message.NLP_entities) + "\n"
        reply += "_NLP language =_ " + str(message.NLP_language) + "\n"
    except:
        logging.warning("NLP not found")
    reply += "\n*USER*\n"
    # TODO pokaż obiekt user (mamy id)
    # this_user = db.getuser(message.facebook_id)
    # for key, val in vars(this_user).items():
    #     reply += "_" + str(key) + "_ = " + str(val) + "\n"
    # bot.fb_send_text_message(str(message.facebook_id), reply)


def show_message_object(message, user, bot):
    reply = ""
    for key, val in vars(message).items():
        reply += str(key) + " = " + str(val) + "\n"
    bot.fb_send_text_message(str(message.facebook_id), reply)