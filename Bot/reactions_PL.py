#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from Bot.cognition import *
from settings import *
from OfferBrowser.best_offer import best_offer
from OfferParser.translator import translate
from time import sleep


def response_decorator(original_function):
    def wrapper(message, user, bot, *args, **kwargs):

        # Do something BEFORE the original function:
        if fake_typing:
            delay = len(str(message.text))/50       # +0.2 set amount of delay
            bot.fb_fake_typing(message.facebook_id, duration=delay)
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
    userword = message.text.split(' ', 1)[0].capitalize()
    if userword == 'Dzie' or userword == 'Dzien' or userword == 'Dzień':
        userword = "Dzień dobry"
    response = random.choice([
        f"{userword} {user.first_name}! Jestem Roomek i jestem na bieżąco z rynkiem nieruchomości.",
        f"{userword} {user.first_name}! Nazywam się Roomek i zajmuję się znajdywaniem najlepszych nieruchomości."
        ])
    bot.fb_send_text_message(str(message.facebook_id), response)
    bot.fb_fake_typing(message.facebook_id, 0.5)
    bot.fb_send_quick_replies(message.facebook_id, "Jak mogę Ci dzisiaj pomóc?", ['🔎 Szukam pokoju', '🔎 Szukam mieszkania', '💰 Sprzedam', '💰 Kupię'])

@response_decorator
def ask_for_housing_type(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Jakiego typu lokal Cię interesuje?", ['🚪 🛌 🛏 pokój', '🏢 mieszkanie', '🐌 kawalerka', '🏠 dom wolnostojący'])

@response_decorator
def ask_if_new_housing_type(message, user, bot, new_value):
    bot.fb_send_quick_replies(message.facebook_id, f"Czy chcesz zmienić typ z {user.housing_type} na {new_value}?", ['Tak', 'Nie'])


@response_decorator
def ask_for_city(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Które miasto Cię interesuje?", ['Warszawa', 'Kraków', 'Łódź', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin', 'Bydgoszcz', 'Białystok'])


@response_decorator
def ask_for_features(message, user, bot):
    question = random.choice(["Czy masz jakieś szczególne preferencje?", "na czymś jeszcze Ci zależy?"])
    bot.fb_send_quick_replies(message.facebook_id, question, ['Nie, pokaż oferty', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'ma garaż', '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])


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
    response1 = f"Zanotowałem, że szukasz {housing_type} w mieście {user.city} w okolicy {user.street} ({user.latitude},{user.longitude})"
    bot.fb_send_text_message(str(message.facebook_id), response1)
    response2 = f"które ma {str(user.features)} i kosztuje do {user.price_limit}zł."
    bot.fb_send_text_message(str(message.facebook_id), response2)
    # TODO add more params
    bot.fb_send_quick_replies(message.facebook_id, "Czy wszystko się zgadza?", ['Tak 👍', '👎 Nie'])


@response_decorator
def ask_what_wrong(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Coś pomyliłem?", ['nie, jest ok', 'zła okolica', 'złe parametry', 'zła cena'])


@response_decorator
def show_offers(message, user, bot):
    # TODO: Kuba popraw best_offer lub baze ofert bo nic nie zwraca :(
    best = best_offer(user_obj=user, count=3)

    if len(best) != 0:
        bot.fb_send_text_message(message.facebook_id, ["Zobacz co dla Ciebie znalazłem:", "Takich ofert jest dużo, ale wybrałem kilka ciekawych", "Co powiesz o tych:", "Może któraś z tych ofert:"])
        bot.fb_send_offers_carousel(message.facebook_id, best)
        sleep(4)
        bot.fb_fake_typing(message.facebook_id, 0.7)
        response = random.choice(["Czy któraś oferta Ci się podoba?", "Masz jakiegoś faworyta?", "Która z powyższych najbardziej Ci odpowiada?"])
        bot.fb_send_quick_replies(message.facebook_id, response, ['1⃣', '2⃣', '3⃣', 'pokaż następne'])
    else:
        bot.fb_send_text_message(message.facebook_id, "Niestety nie znalazłem ofert spełniających Twoje kryteria :(")


@response_decorator
def yes(message, user, bot):
    response = random.choice([
        "ok",
        "super",
        "jasne",
        "zanotowałem",
        "(y)"
    ])
    bot.fb_send_text_message(message.facebook_id, response)


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
    response = f"'{message.text.capitalize()}'? Potrzebuejesz chwilę, żeby się zastanowić?"
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
    # this_user = db.getuser(message.facebook_id)
    for key, val in vars(user).items():
        reply += "_" + str(key) + "_ = " + str(val) + "\n"
    bot.fb_send_text_message(str(message.facebook_id), reply)


def show_message_object(message, user, bot):
    reply = ""
    for key, val in vars(message).items():
        reply += str(key) + " = " + str(val) + "\n"
    bot.fb_send_text_message(str(message.facebook_id), reply)