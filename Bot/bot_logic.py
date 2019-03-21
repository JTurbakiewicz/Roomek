#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

# import public modules:
import os
import re
import json
import random
import logging
from flask import Flask, request
# import from own modules:
from Dispatcher_app import tokens_local, database, witai
if tokens_local: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
if database: from Databases import mysql_connection as db
from Bot.bot_cognition import *
from Bot.bot_responses import *
from Bot.bot_post_parser import Message
from Bot.facebook_webhooks import Bot

log = logging.getLogger(os.path.basename(__file__))

#initiate the bot object:
bot = Bot(tokens.fb_access)

#fetch user ids from the DB:
users = []
if database:
    for user in db.get_all('facebook_id'):
        users.append(user)

def handle_message(user_message):
    """ Recognize the content and respond accordingly. """
    message = Message(user_message)
    if message.type == "TextMessage" or message.type == "StickerMessage" or message.type == "MessageWithAttachment":
        bot.fb_send_action(message.senderID, 'mark_seen')
        add_new_user(message.senderID)
        if message.type == "TextMessage":
            handle_text(message, bot)
        elif message.type == "StickerMessage":
            handle_sticker(message, bot)
        elif message.type == "MessageWithAttachment":
            handle_attachment(message, bot)
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
        #TODO withdraw more info: bot.fb_get_user_info(bot,userid)  #first_name
        if database: db.create_player(user_id)
        users.append(user_id)
    else:
        #TODO withdraw more info from the database.
        if database: db.query(user_id, ('first_name','last_name'))

def handle_text(message, bot):
    """ React when the user sends any text. """
    entity = messege.best_entity()
    user_message = message.text
    if entity == "" or entity is None:
        entity = regex_pattern_matcher(message.text)   #no entity from NLP so try to find with regex
        log.info("Message '{0}' from {1} recognized as '{2}' using REGEX.".format(message.mid[0:7], message.senderID[0:5], entity))
    else:
        log.info("Message '{0}' from {1} recognized as '{2}' ({3}% confidence) using NLP from FB.".format(message.mid[0:7], message.senderID[0:5], entity[0], str(float(entity[1])*100)[0:5]))
        entity = entity[0]
    # React:
    response = responder(entity, message.text, message.senderID, bot)   #prepare the response based on the entity given
    if response != "already sent":
        if type(response) == list:
            response = random.choice(response)
        bot.fb_send_text_message(message.senderID, response)
        if database: db.add_conversation(message.senderID, 'User', message.text)
        if database: db.add_conversation(message.senderID, 'Bot', response)

def handle_sticker(message, bot):
    """ React when the user sends a sticker. """
    bot.fb_fake_typing(message.senderID, 0.5)
    sticker_id = message.stickerID
    sticker_name = recognize_sticker(message.stickerID)
    response = sticker_response(sticker_name, message.senderID, bot)
    if response != "already sent":
        bot.fb_send_text_message(message.senderID, response)
    if database: db.add_conversation(message.senderID, 'User', '<sticker_{0}_{1}>'.format(sticker_name, message.stickerID))
    if database: db.add_conversation(message.senderID, 'Bot', response)
    log.info("Message '{0}' from {1} recognized as '{1}' sticker (id={2})".format(message.mid, message.senderID[0:5], sticker_name, message.stickerID))
    log.info("Bot's response to user {1} sticker:  '{0}'".format(response, message.senderID))

def handle_attachment(message, bot):
    """ React when the user sends a GIF, photos, videos, or any other non-text item."""
    bot.fb_fake_typing(message.senderID, 0.8)
    image_url = r'https://media.giphy.com/media/L7ONYIPYXyc8/giphy.gif'
    bot.fb_send_image_url(message.senderID, image_url)
    if database: db.add_conversation(message.senderID,'User','<GIF>')
    if database: db.add_conversation(message.senderID, 'Bot', "<GIF>")
    log.info("Bot's response to user {1} gif:  '{0}'".format('<GIF>', message.senderID))

def stack_items(id, item, stack_size = 3):
    """A function that lets you keep multiple (amount equal to stack_size) items in a list. The lists are
    than put in a one common dictionary. id -> dictionary index; item -> item to put in the stack"""
    global stacked_items # variable init in a a function to allow for easy function copy-pasting.
    try:
        stacked_items.get('') # checks if the variable is already created
    except:
        stacked_items = {} # if it's not, create the variable
    if id in stacked_items:
        stacked_items[id].append(item)
        if len (stacked_items[id]) > stack_size:
            stacked_items[id].pop(0)
    else:
        stacked_items[id] = []
        stacked_items[id].append(item)
