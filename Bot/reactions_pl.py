#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Set of responses for particular intents"""

import os
import random
import logging
from time import sleep
import datetime

from settings import *
from schemas import user_questions, bot_phrases, months, user_questions_translations

import Bot.cognition as cog
import Bot.geolocate as geo
from RatingEngine.best_offer import best_offer
from OfferParser.translator import translate
from Databases import mysql_connection as db


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
                elif key == "meta":
                    pass
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
def ask_for(message, user, bot, param, meta=""):
    question = random.choice(user_questions[param]['question'])
    custom = f'responses_{meta}'
    if meta != "" and custom in user_questions[param]:
        responses = user_questions[param][custom]
    else:
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
    city = db.get_query(user.facebook_id, "city")
    replies = ['Blisko centrum']
    districts = geo.child_locations(city)
    if districts:
        replies = replies + geo.child_locations(city)[0:10]
    bot.fb_send_quick_replies(message.facebook_id, reply_message=question, replies=replies)


@response_decorator
def ask_more_locations(message, user, bot):
    question = random.choice(["Czy chciałbyś dodać jeszcze jakieś miejsce?", "Zanotowałem, coś oprócz tego?"])
    city = db.get_query(user.facebook_id, "city")
    replies = ['Nie', 'Blisko centrum']
    districts = geo.child_locations(city)
    if districts:
        replies = replies + geo.child_locations(city)[0:9]
    already_asked_for = db.get_query(facebook_id=user.facebook_id, field_name='district').split(',')
    replies = [i for i in replies if i not in already_asked_for]
    bot.fb_send_quick_replies(message.facebook_id, reply_message=question, replies=replies)


@response_decorator
def ask_if_new_housing_type(message, user, bot, new_value):
    bot.fb_send_quick_replies(message.facebook_id,
                              f"Czy chcesz zmienić typ z {db.get_query(facebook_id=message.facebook_id)} na {new_value}?",
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
    ask_for(message, user, bot, param="interest")


@response_decorator
def ask_for_more_features(message, user, bot, meta=""):
    question = random.choice(["Coś oprócz tego?", "Ok, jeszcze coś?", "Zanotowałem, chciałbyś coś dodać?"])
    custom = f'responses_{meta}'
    user.set_param("context", "ask_for_more_features")
    if meta != "" and custom in user_questions['features']:
        responses = user_questions['features'][custom]
    else:
        responses = user_questions['features']['responses']
    already_asked_for_eng = [x[0] for x in db.get_all_queries(facebook_id=user.facebook_id)]
    already_asked_for_pl = []
    for asked_in_eng in already_asked_for_eng:
        for polish, english in user_questions_translations.items():
            if english == asked_in_eng:
                already_asked_for_pl.append(polish)
    responses = [i for i in responses if i not in already_asked_for_pl]
    bot.fb_send_quick_replies(message.facebook_id, question, responses)


@response_decorator
def show_input_data(message, user, bot):
    user.shown_input = True
    housing_type = translate(db.get_query(user.facebook_id, field_name='housing_type'), "D")
    business_type = db.get_query(user.facebook_id, field_name='business_type')
    if business_type == 'rent':
        business_type = "na wynajem"
    elif business_type == 'buy':
        business_type = "do kupienia"

    response1 = f"Zanotowałem, że szukasz {housing_type} {business_type} w mieście {db.get_query(user.facebook_id, field_name='city')}"

    street = db.get_query(user.facebook_id, field_name='street')
    district = db.get_query(user.facebook_id, field_name='district')
    if street:
        response1 += f", blisko ulicy {street}"
    elif district:
        response1 += f", najlepiej w dzielnicy {district}"
    else:
        response1 += f", blisko miejsca o współrzędnych: {db.get_query(user.facebook_id, field_name='latitude')}, {db.get_query(user.facebook_id, field_name='longitude')}"

    bot.fb_send_text_message(str(message.facebook_id), response1)

    price = db.get_query(user.facebook_id, field_name='total_price')
    if price < 99999998:
        response2 = f"które kosztuje do {price}zł"
    else:
        response2 = f"którego cena nie gra roli 🤑"
    bot.fb_send_text_message(str(message.facebook_id), response2)

    features = db.get_all_queries(user.facebook_id)
    remove = ['business_type', 'city', 'total_price', 'street', 'district', 'latitude', 'longitude', 'housing_type']
    features = [f for f in features if f[0] not in remove]

    if features:
        response3 = []
        for feature in features:
            if feature[1] == 1:
                response3.append("które ma " + str(feature[0]))
            elif feature[1] == 0:
                response3.append("które nie ma " + str(feature[0]))
            elif feature[0] == 'ready_from':
                time_now = datetime.datetime.now()
                if feature[1] < time_now:
                    response3.append("które jest dostępne od zaraz ")
                else:
                    response3.append(f"które będzie dostępne od {months[feature[1]].month}")
            else:
                response3.append("którego " + str(feature[0]) + " to " + str(feature[1]))

        response3 = ', '.join(response3)
        response3 = "i " + response3 + "."

        bot.fb_send_text_message(str(message.facebook_id), response3)

    bot.fb_send_quick_replies(message.facebook_id, "Czy wszystko się zgadza?", ['Tak 👍', '👎 Nie'])


@response_decorator
def ask_what_wrong(message, user, bot):
    bot.fb_send_quick_replies(message.facebook_id, "Coś pomyliłem?",
                              ['jest ok', 'zła okolica', 'złe parametry', 'zła cena'])


@response_decorator
def show_offers(message, user, bot):
    best = best_offer(user_obj=user, count=3)
    city = db.get_query(user.facebook_id, field_name='city')
    if len(best['offers']) != 0:
        bot.fb_send_text_message(message.facebook_id, [
            f"Spośród {best['offers_count_city']} ofert w mieście {city} jest {best['offers_count']} ofert, które spełniają Twoje kryteria. Moim zdaniem te są najciekawsze:",
            f"Spośród {best['offers_count_city']} ofert w mieście {city}, takich ofert znalazłem {best['offers_count']}. Co powiesz o tych:"])
        bot.fb_send_offers_carousel(message.facebook_id, best['offers'])
        sleep(4)    # TODO asyncio!
        bot.fb_fake_typing(message.facebook_id, 0.7)
        response = random.choice(["Czy znalazłeś to czego szukałeś, czy pokazać następne?", "Masz jakiegoś faworyta, czy pokazać kolejne oferty?"])
        # "Która z powyższych najbardziej Ci odpowiada?""Która z powyższych najbardziej Ci odpowiada?"
        bot.fb_send_quick_replies(message.facebook_id, response,
                                  ['Pokaż następne', 'Zacznijmy od nowa'])
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


# @response_decorator
def sticker_response(message, user, bot):
    # TODO !!! Problemy z naklejkami, rozumieniem "thumb", zapisem do bazy oraz z odpowiadaniem na naklejke.
    sticker_name = cog.recognize_sticker(message.stickerID)
    if sticker_name == 'thumb' or sticker_name == 'thumb+' or sticker_name == 'thumb++':
        # Fake message NLP:
        message.NLP_entities = [{'entity': "boolean", "value": "yes"}]
        cog.collect_information(message, user, bot)
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
        }.get(sticker_name, ["Fajna naklejka :)", "Haha!"])
        bot.fb_send_text_message(str(message.facebook_id), response)
        #ask_for_information(message, user, bot)

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