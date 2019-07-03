#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

from settings import *
import tokens
from Databases import mysql_connection as db
from Bot.cognition import *
from Bot.reactions_PL import *
from Bot.respond import *
from Bot.message import Message
from Bot.facebook_webhooks import Bot

# initiate the bot object:
bot = Bot(tokens.fb_access)


def handle_message(user_message):
    """ Recognize the content and respond accordingly. """
    message = Message(user_message)
    if message.type == "TextMessage" \
            or message.type == "StickerMessage" \
            or message.type == "MessageWithAttachment" \
            or message.type == "LocationAnswer" \
            or message.type == "BotTest":
        if not message.is_echo:
            bot.fb_send_action(str(message.user_id), 'mark_seen')
            
            if message.type == "TextMessage":
                handle_text(message, bot)
            elif message.type == "StickerMessage":
                handle_sticker(message, bot)
            if message.type == "LocationAnswer":
                handle_location(message, bot)
            elif message.type == "MessageWithAttachment":
                handle_attachment(message, bot)
            elif message.type == "BotTest":
                handle_test(message, bot)
    elif message.type == "Delivery":
        pass
    elif message.type == "ReadConfirmation":
        pass
    elif message.type == "UnknownType":
        pass
    else:
        logging.warning("Didn't recognize the message type. Json content:  \n"+str(user_message))


def handle_text(message, bot):
    """ React when the user sends any text. """
    if message.NLP:
        if hasattr(message, "NLP_intent") or message.NLP_entities is not None:
            concat = ""
            for m in range(len(message.NLP_entities)):
                concat += str(message.NLP_entities[m][0])+" = "+str(message.NLP_entities[m][1])+' ('+str(float(message.NLP_entities[m][2])*100)[0:5]+'%);'
            logging.info("NLP recognized: '{0}' as: intent=[{1}], entities=[{2}]".format(message.text, message.NLP_intent, concat))
        respond(message, bot)
    else:
        default_message(message, bot)


def handle_sticker(message, bot):
    """ React when the user sends a sticker. """
    bot.fb_fake_typing(str(message.user_id), 0.5)
    response = sticker_response(message, bot)
    if response != "already sent":
        bot.fb_send_text_message(str(message.user_id), response)
    logging.info("Message '{0}' from {1} recognized as '{2}' sticker (id={3})".format("<sticker>", str(message.user_id)[0:5], message.sticker_name, message.stickerID))
    logging.info("Bot's response to user {1} sticker:  '{0}'".format(response, str(message.user_id)))


def handle_attachment(message, bot):
    """ React when the user sends a GIF, photos, videos, or any other non-text item."""
    if fake_typing: bot.fb_fake_typing(str(message.user_id), 0.8)
    image_url = r'https://media.giphy.com/media/L7ONYIPYXyc8/giphy.gif'
    bot.fb_send_image_url(str(message.user_id), image_url)
    logging.info("Bot's response to user {1} gif:  '{0}'".format('<GIF>', str(message.user_id)))


def handle_location(message, bot):
    """ React when the user replies with location."""
    respond(message, bot)


def handle_test(message, bot):
    if 'quick' in message.text:
        bot.fb_send_quick_replies(message.user_id, "This is a test of quick replies", ['test_value_1', 'test_value_2', 'test_value_3'])
    elif 'list' in message.text:
        print("TEMP GOT HERE")
        bot.fb_send_list_message(message.user_id, element_titles=['test_value_1', 'test_value_2'], button_titles=['test_value_3', 'test_value_4'])  # TODO not working
    elif 'menu' in message.text:
        print("TEMP GOT HERE TO MENY TRY")
        bot.fb_create_menu()
    elif 'button' in message.text:
        bot.fb_send_button_message(message.user_id, "test", ['test_value_1', 'test_value_2'])  # TODO not working
    elif 'generic' in message.text:
        bot.fb_send_generic_message(message.user_id, ['Test_value_1', 'Test_value_2'])
        # temp: bot.fb_send_test_message(userid, ['test_value_1', 'test_value_2'])
        # bot.fb_send_generic_message(
        # userid, [['Title1','Subtitle1','image_url1',
        # buttons=['title1','url1']],['Title2','Subtitle2',
        # 'image_url2',buttons=['title2','url2']]])
    else:
        bot.fb_send_text_message(str(message.user_id), 'Hello world!')
