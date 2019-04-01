#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

from Dispatcher_app import use_local_tokens, use_database, use_witai
if use_local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
if use_database: from Databases import mysql_connection as db
from Bot.bot_cognition import *
from Bot.bot_responses import *
from Bot.bot_post_parser import Message
from Bot.facebook_webhooks import Bot
log = logging.getLogger(os.path.basename(__file__))

# initiate the bot object:
bot = Bot(tokens.fb_access)

# fetch user ids from the DB:
users = []
if use_database:
    for user in db.get_all('facebook_id'):
        users.append(user)


def handle_message(user_message):
    """ Recognize the content and respond accordingly. """
    message = Message(user_message)
    if message.type == "TextMessage" or message.type == "StickerMessage" or message.type == "MessageWithAttachment" or message.type == "BotTest":
        bot.fb_send_action(str(message.senderID), 'mark_seen')
        add_new_user(str(message.senderID))
        if message.type == "TextMessage":
            handle_text(message, bot)
        elif message.type == "StickerMessage":
            handle_sticker(message, bot)
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
        log.warning("Didn't recognize the message type. Json content:  \n"+str(user_message))


def add_new_user(user_id):
    """ Check if already exists. If not - add to database. """
    if user_id not in users:
        # TODO withdraw more info: bot.fb_get_user_info(bot,userid)  #first_name
        if use_database: db.create_player(user_id)
        users.append(user_id)
    else:
        # TODO withdraw more info from the database.
        if use_database: db.query(user_id, ('first_name', 'last_name'))


def handle_text(message, bot):
    """ React when the user sends any text. """
    if message.NLP:
        if message.NLP_intent is not None:
            log.info("Message '{0}' from {1} recognized as '{2}' using wit-ai, with entities:".format(message.text, str(message.senderID)[0:5], message.NLP_intent))
            for m in range(len(message.NLP_entities)):
                log.info(message.NLP_entities[m][0]+" = "+message.NLP_entities[m][1]+' ('+str(float(message.NLP_entities[m][2])*100)[0:5]+'%).')
        respond(message, bot)
    else:
        default_message(message, bot)


def handle_sticker(message, bot):
    """ React when the user sends a sticker. """
    bot.fb_fake_typing(str(message.senderID), 0.5)
    sticker_id = message.stickerID
    sticker_name = recognize_sticker(message.stickerID)
    response = sticker_response(sticker_name, str(message.senderID), bot)
    if response != "already sent":
        bot.fb_send_text_message(str(message.senderID), response)
    if use_database: db.add_conversation(str(message.senderID), 'User', '<sticker_{0}_{1}>'.format(sticker_name, message.stickerID))
    if use_database: db.add_conversation(str(message.senderID), 'Bot', response)
    log.info("Message '{0}' from {1} recognized as '{1}' sticker (id={2})".format(str(message.mid), str(message.senderID)[0:5], sticker_name, message.stickerID))
    log.info("Bot's response to user {1} sticker:  '{0}'".format(response, str(message.senderID)))


def handle_attachment(message, bot):
    """ React when the user sends a GIF, photos, videos, or any other non-text item."""
    bot.fb_fake_typing(str(message.senderID), 0.8)
    image_url = r'https://media.giphy.com/media/L7ONYIPYXyc8/giphy.gif'
    bot.fb_send_image_url(str(message.senderID), image_url)
    if use_database: db.add_conversation(str(message.senderID),'User','<GIF>')
    if use_database: db.add_conversation(str(message.senderID), 'Bot', "<GIF>")
    log.info("Bot's response to user {1} gif:  '{0}'".format('<GIF>', str(message.senderID)))


def handle_test(message, bot):
    if 'quick' in message.text:
        bot.fb_send_quick_replies(userid, "This is a test of quick replies", ['test_value_1', 'test_value_2', 'test_value_3'])  # TODO test if working
    elif 'list' in message.text:
        bot.fb_send_list_message(message.senderID, ['test_value_1', 'test_value_2'], ['test_value_3', 'test_value_4'])  # TODO not working
    elif 'button' in message.text:
        bot.fb_send_button_message(userid, "test", ['test_value_1', 'test_value_2'])  # TODO not working
    elif 'generic' in message.text:
        bot.fb_send_generic_message(userid, ['Test_value_1', 'Test_value_2'])
        # temp: bot.fb_send_test_message(userid, ['test_value_1', 'test_value_2'])
        # bot.fb_send_generic_message(
        # userid, [['Title1','Subtitle1','image_url1',
        # buttons=['title1','url1']],['Title2','Subtitle2',
        # 'image_url2',buttons=['title2','url2']]])
    else:
        bot.fb_send_text_message(str(message.senderID), 'Hello world!')


def stack_items(id, item, stack_size = 3):
    """A function that lets you keep multiple (amount equal to stack_size) items in a list. The lists are
    than put in a one common dictionary. id -> dictionary index; item -> item to put in the stack"""
    global stacked_items  # variable init in a a function to allow for easy function copy-pasting.
    try:
        stacked_items.get('')  # checks if the variable is already created
    except:
        stacked_items = {}  # if it's not, create the variable
    if id in stacked_items:
        stacked_items[id].append(item)
        if len (stacked_items[id]) > stack_size:
            stacked_items[id].pop(0)
    else:
        stacked_items[id] = []
        stacked_items[id].append(item)
