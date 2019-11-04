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


def handle_message(message, user):
    """ Recognize the content and respond accordingly. """

    db.create_message(msg_obj=message)

    if message.is_echo:
        pass
    elif db.msg_in(message.facebook_id, message.mid):
        logging.info("this message has been already processed.")
    else:

        bot.fb_send_action(str(message.facebook_id), 'mark_seen')

        if message.type == "Delivery":
            pass
        elif message.type == "ReadConfirmation":
            pass
        elif message.type == "UnknownType":
            pass
        elif message.type == "TextMessage":
            handle_text(message, user, bot)
        elif message.type == "StickerMessage":
            handle_sticker(message, user, bot)
        elif message.type == "LocationAnswer":
            handle_location(message, user, bot)
        elif message.type == "GifMessage":
            handle_attachment(message, user, bot)
        elif message.type == "MessageWithAttachment":
            handle_attachment(message, user, bot)
        elif message.type == "DevMode":
            handle_devmode(message, user, bot)
        else:
            logging.warning(f"Didn't recognize the message type: {message.type}")


def handle_text(message, user, bot):
    """ React when the user sends any text. """
    if message.NLP:
        logging.info(f"-NLP→ intent: {str(message.NLP_intent)}, entities: {str(message.NLP_entities)}")
        collect_information(message, user, bot)
        respond(message, user, bot)
    else:
        default_message(message, user, bot)


def handle_sticker(message, user, bot):
    """ React when the user sends a sticker. """
    bot.fb_fake_typing(str(message.facebook_id), 0.5)
    response = sticker_response(message, user, bot)
    if response != "already sent":
        bot.fb_send_text_message(str(message.facebook_id), response)
    logging.info(f"Message <sticker> from {str(message.facebook_id)[0:5]} recognized as '{message.sticker_name}' sticker (id={message.stickerID})")
    logging.info(f"Bot's response to user {str(message.facebook_id)} sticker:  '{response}'")


def handle_attachment(message, user, bot):
    """ React when the user sends a GIF, photos, videos, or any other non-text item."""
    if fake_typing: bot.fb_fake_typing(str(message.facebook_id), 0.8)
    image_url = r'https://media.giphy.com/media/L7ONYIPYXyc8/giphy.gif'
    bot.fb_send_image_url(str(message.facebook_id), image_url)
    logging.info(f"Bot's response to user {str(message.facebook_id)} gif:  '<GIF>'")


def handle_location(message, user, bot):
    """ React when the user replies with location."""
    if user.context == "ask_for_city":
        user.add_location(message.latitude, message.longitude, city_known=False)
    elif user.context == "ask_for_location":
        user.add_location(message.latitude, message.longitude, city_known=True)
    respond(message, user, bot)


def handle_devmode(message, user, bot):
    if 'quick' in message.text:
        bot.fb_send_quick_replies(message.facebook_id, "This is a test of quick replies", ['test_value_1', 'test_value_2', 'test_value_3'])
    # elif 'list' in message.text:
    #     bot.fb_send_list_message(message.facebook_id, element_titles=['test_value_1', 'test_value_2'], button_titles=['test_value_3', 'test_value_4'])  # TODO not working
    # elif 'button' in message.text:
    #     bot.fb_send_button_message(message.facebook_id, "test", ['test_value_1', 'test_value_2'])  # TODO not working
    # elif 'generic' in message.text:
    #     bot.fb_send_generic_message(message.facebook_id, ['Test_value_1', 'Test_value_2'])
    elif 'd' in message.text:
        bot.fb_send_text_message(str(message.facebook_id), 'Your data has been erased.')
        db.drop_user(message.facebook_id)
    elif 's' in message.text:
        response.show_user_object(message, user, bot)
    else:
        bot.fb_send_text_message(str(message.facebook_id), 'Hello world!')
