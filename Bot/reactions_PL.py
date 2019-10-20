#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from Bot.cognition import collect_information
from settings import *
from OfferBrowser.best_offer import best_offer
from OfferParser.translator import translate
from time import sleep
from schemas import user_questions, bot_phrases, months
from Bot.geolocate import child_locations
from Databases import mysql_connection as db
import datetime


def response_decorator(original_function):
    def wrapper(message, user, bot, **kwargs):

        # Do something BEFORE the original function:
        if fake_typing:
            delay = len(str(message.text)) / 50  # +0.2 set amount of delay
            bot.fb_fake_typing(message.facebook_id, duration=delay)
        # show_message_object(message, user, bot)
        # TODO naprawić to, bo tak nie działa :(

        if kwargs:
            for key, value in kwargs.items():
                if key == "param":
                    user.set_param("context", "ask_for_" + str(value))
                else:
                    user.set_param("context", original_function.__name__)
        else:
            user.set_param("context", original_function.__name__)

        # The original function:
        original_function(message, user, bot, **kwargs)

        # Do something AFTER the original function:
        # TODO: bot.fb_send_text_message(str(message.facebook_id), response)

    return wrapper


@response_decorator
def default_message(message, user, bot):
    response = random.choice(bot_phrases['default'])
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def ask_for(message, user, bot, param):
    question = random.choice(user_questions[param]['question'])
    responses = user_questions[param]['responses']
    bot.fb_send_quick_replies(message.facebook_id, question, responses)


@response_decorator
def greeting(message, user, bot):
    user_greeting = message.text.split(' ', 1)[0].capitalize()
    if user_greeting == 'Dzie' or user_greeting == 'Dzien' or user_greeting == 'Dzień':
        user_greeting = "Dzień dobry"
    bot_greeting = random.choice(bot_phrases['greeting'])
    bot_greeting = bot_greeting.format(greeting=user_greeting, first_name=user.first_name)
    bot.fb_send_text_message(str(message.facebook_id), bot_greeting)
    ask_for(message, user, bot, param="interest")


@response_decorator
def ask_for_location(message, user, bot):
    question = random.choice(bot_phrases['ask_location'])
    city = db.user_query(user.facebook_id, "city")
    # TODO DISTRICTS!

    replies = ['🎯 centrum'] + child_locations(city)[0:10]
    bot.fb_send_quick_replies(message.facebook_id, reply_message=question, replies=replies, location=True)


@response_decorator
def ask_more_locations(message, user, bot):
    question = random.choice(["Czy chciałbyś dodać jeszcze jakieś miejsce?", "Zanotowałem, coś oprócz tego?"])
    city = db.user_query(user.facebook_id, "city")
    # TODO DISTRICTS!

    replies = ['Nie', '🎯 centrum'] + child_locations(city)[0:9]
    bot.fb_send_quick_replies(message.facebook_id, reply_message=question, replies=replies, location=True)
    # TODO powinno wiedzieć co już padło


@response_decorator
def ask_if_new_housing_type(message, user, bot, new_value):
    bot.fb_send_quick_replies(message.facebook_id,
                              f"Czy chcesz zmienić typ z {db.user_query(facebook_id=message.facebook_id)} na {new_value}?",
                              ['Tak', 'Nie'])


@response_decorator
def ask_if_restart(message, user, bot):
    question = random.choice(
        ["Czy na pewno chcesz rozpocząć wyszukiwanie na nowo?", "Ok, zacznijmy od nowa. Zadam Ci parę pytań, dobrze?"])
    bot.fb_send_quick_replies(message.facebook_id, question, ['Tak 👍', '👎 Nie'])


@response_decorator
def restart(message, user, bot):
    user.set_param("wants_restart", False)
    bot.fb_send_text_message(str(message.facebook_id), "Ok, spróbujmy wyszukać od nowa.")
    ask_how_help(message, user, bot)


@response_decorator
def ask_for_more_features(message, user, bot):
    question = random.choice(["Coś oprócz tego?", "Ok, jeszcze coś?", "Zanotowałem, chciałbyś coś dodać?"])
    bot.fb_send_quick_replies(message.facebook_id, question,
                              ['Nie, wystarczy', 'od zaraz', 'przyjazne dla 🐶🐱', 'blisko do...', 'garaż',
                               '🔨 wyremontowane', 'umeblowane', 'ma 🛀', 'dla 🚬', 'dla 🚭'])
    # TODO powinno wiedzieć jakie już padły


@response_decorator
def show_input_data(message, user, bot):
    user.shown_input = True
    housing_type = translate(db.user_query(user.facebook_id, field_name='housing_type'), "D")
    if db.user_query(user.facebook_id, field_name='street'):
        location = db.user_query(user.facebook_id, field_name='street')
    elif db.user_query(user.facebook_id, field_name='district'):
        location = db.user_query(user.facebook_id, field_name='district')
    else:
        location = f"miejsca o współrzędnych: {db.user_query(user.facebook_id, field_name='latitude')}, {db.user_query(user.facebook_id, field_name='longitude')}"

    if location != 'no_district' and location != 'no_street':
        response1 = f"Zanotowałem, że szukasz {housing_type} w mieście {db.user_query(user.facebook_id, field_name='city')} w okolicy {location}"
    else:
        response1 = f"Zanotowałem, że szukasz {housing_type} w mieście {db.user_query(user.facebook_id, field_name='city')}"

    bot.fb_send_text_message(str(message.facebook_id), response1)

    if db.get_all_queries(user.facebook_id):
        response2 = "które ma "
        for feature in db.get_all_queries(user.facebook_id):
            if feature[1] == 1:
                response2 += ", ma " + str(feature[0])
            elif feature[1] == 0:
                response2 += ", nie ma " + str(feature[0])
            elif feature[0] == 'ready_from':
                time_now = datetime.datetime.now()
                if feature[1] < time_now:
                    response2 += ", które jest dostępne od zaraz "
                else:
                    response2 += f", które będzie dostępne od {months[feature[1]].month}"
            else:
                response2 += ", którego " + str(feature[0]) + " to " + str(feature[1])
        bot.fb_send_text_message(str(message.facebook_id), response2)

    response3 = f"i kosztuje do {db.user_query(user.facebook_id, field_name='price')}zł."
    bot.fb_send_text_message(str(message.facebook_id), response3)
    # TODO add more params

    bot.fb_send_quick_replies(message.facebook_id, "Czy wszystko się zgadza?", ['Tak 👍', '👎 Nie'])


@response_decorator
def ask_what_wrong(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Coś pomyliłem?",
                              ['nie, jest ok', 'zła okolica', 'złe parametry', 'zła cena'])


@response_decorator
def show_offers(message, user, bot):
    best = best_offer(user_obj=user, count=3)
    if len(best['offers']) != 0:
        bot.fb_send_text_message(message.facebook_id, [
            f"Spośród {best['offers_count_city']} ofert w Twoim mieście jest {best['offers_count']} ofert, które spełniają Twoje kryteria. Moim zdaniem te są najciekawsze:",
            f"Spośród {best['offers_count_city']} ofert w Twoim mieście, takich ofert znalazłem {best['offers_count']}. Co powiesz o tych:"])
        bot.fb_send_offers_carousel(message.facebook_id, best['offers'])
        sleep(4)    # TODO asyncio!
        bot.fb_fake_typing(message.facebook_id, 0.7)
        response = random.choice(["Znalazłeś to czego szukałeś, czy pokazać następne?", "Masz jakiegoś faworyta, czy pokazać kolejne oferty?"])
        # "Która z powyższych najbardziej Ci odpowiada?""Która z powyższych najbardziej Ci odpowiada?"
        bot.fb_send_quick_replies(message.facebook_id, response,
                                  ['pokaż następne oferty', 'zacznijmy od nowa'])
    else:
        bot.fb_send_text_message(message.facebook_id, "Niestety nie znalazłem ofert spełniających Twoje kryteria :(")


@response_decorator
def dead_end(message, user, bot):
    response = "Ups, to ślepy zaułek tej konwersacji!"
    bot.fb_send_text_message(str(message.facebook_id), response)


@response_decorator
def unable_to_answer(message, user, bot):
    response = "Wybacz, na ten moment potrafię jedynie wyszukiwać najlepsze dostępne oferty wynajmu."
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
    sticker_name = 'thumb'  # TODO
    # sticker_name = cog.recognize_sticker(message.stickerID)
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        # Fake message NLP:
        message.NLP_entities = [{'entity': "boolean", "value": "yes"}]
        collect_information(message, user, bot)
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