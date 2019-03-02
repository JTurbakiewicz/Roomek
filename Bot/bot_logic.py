
""" Functions for basic bot behaviours. """

# import public modules:
import os
import re
import json
import random
import logging
from flask import Flask, request
# import from own modules:
from Flask_app import local_tokens, database, witai
if local_tokens: from Bot import tokens_local as tokens
else: from Bot import tokens
if database: from Databases import mysql_connection as db
from Bot.bot_responses import *
from Bot.facebook_webhooks import Bot

log = logging.getLogger(os.path.basename(__file__))

#initiate the bot object:
bot = Bot(tokens.fb_access)

#fetch user ids from the DB:
users = []
if database:
    for user in db.get_all('facebook_id'):
        users.append(user)

def handle_messages(user_message):
    """ Recognize the content and respond accordingly. """
    for entry in user_message['entry']:
        message_id = entry['id']
        try:
            messaging = entry['messaging']
        except:
            messaging = False
            log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))

        if messaging != False:
            for message in messaging:
                if message.get('delivery'):
                    deli = message['delivery']
                    try:
                        mids = deli.get('mids')
                    except:
                        mids = "DELIXXXXXXXXXXXXXX"
                    if int(message['recipient']['id']) == int(tokens.fb_bot_id):
                        mid=""
                        for m in mids:
                            mid += ",'"+str(m)[0:7]+"'"
                        mid = mid[1:]
                        log.info("Bot's message: {0} to {1} has been delivered.".format(mid, str(message['sender']['id'][0:5])))
                    else:
                        log.info("Message {0} from {1} has been delivered.".format(str(mid)[0:7], str(message['sender']['id'][0:5])))
                elif message.get('read'):
                    if int(message['recipient']['id']) == int(tokens.fb_bot_id):
                        log.info("Bot's message read by {0}.".format(message['sender']['id'][0:5]))
                    else:
                        log.info("Message from {0} read by bot.".format(str(message['sender']['id'][0:5])))
                elif message.get('message'):
                    bot.fb_send_action(message['sender']['id'], 'mark_seen')
                    add_new_user(message['sender']['id'])
                    senderid = message['sender']['id']
                    recipientid = message['recipient']['id']
                    message = message['message']
                    user_message = message.get('text')
                    try:
                        mid = message.get('mid')
                    except:
                        mid = "TEXTXXXXXXXXXXXXXX"
                    if int(senderid) != int(tokens.fb_bot_id):
                        if message.get('text'):
                            log.info("Message '{0}' from user {1}:  '{2}'".format(str(mid)[0:7], str(senderid)[0:5], user_message))
                            handle_text(message, senderid, bot)
                        elif message.get('sticker_id'):
                            log.info("Message '{0}' from user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
                            handle_sticker(message, senderid, bot)
                        elif message.get('attachments'):
                            log.info("Message '{0}' from user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
                            handle_attachment(message, senderid, bot)
                    else:
                        if message.get('text'):
                            log.info("Bot's message '{0}' to user {1}:  '{2}'".format(str(mid)[0:7], recipientid[0:5], user_message))
                        elif message.get('sticker_id'):
                            log.info("Bot's message '{0}' to user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
                        elif message.get('attachments'):
                            log.info("Bot's message '{0}' to user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
                else:
                    log.error("Unknown message type! Content: " + message)

def add_new_user(user_id):
    """ Check if already exists. If not - add to database. """
    if user_id not in users:
        #TODO withdraw more info: bot.fb_get_user_info(bot,userid)  #first_name
        if database: db.create_player(user_id)
        users.append(user_id)
    else:
        #TODO withdraw more info from the database.
        if database: db.query(user_id, (first_name,last_name))

def handle_text(message, userid, bot):
    """ React when the user sends any text. """
    entity = best_entity(message)
    user_message = message.get('text')
    try:
        mid = message.get('mid')
    except:
        mid = "RECOGNITIONXXXXXXXXXXXXXX"
    if entity == "" or entity is None:
        entity = regex_pattern_matcher(user_message)   #no entity from NLP so try to find with regex
        log.info("Message '{0}' from {1} recognized as '{2}' using REGEX.".format(str(mid)[0:7], str(userid)[0:5], entity))
    else:
        log.info("Message '{0}' from {1} recognized as '{2}' ({3}% confidence) using NLP from FB.".format(str(mid)[0:7], str(userid)[0:5], entity[0], str(float(entity[1])*100)[0:5]))
        entity = entity[0]
    # React:
    response = responder(entity, user_message, userid, bot)   #prepare the response based on the entity given
    if response != "already sent":
        if type(response) == list:
            response = random.choice(response)
        bot.fb_send_text_message(userid, response)
        if database: db.add_conversation(userid, 'User', user_message)
        if database: db.add_conversation(userid, 'Bot', response)

def handle_sticker(message, userid, bot):
    """ React when the user sends a sticker. """
    bot.fb_fake_typing(userid, 0.5)
    sticker_id = str(message.get('sticker_id'))
    sticker_name = recognize_sticker(sticker_id)
    response = sticker_response(sticker_name)
    bot.fb_send_text_message(userid, response)
    try:
        mid = message.get('mid')
    except:
        mid = "STICKERXXXXXXXXXXXXXX"
    if database: db.add_conversation(userid,'User', '<sticker_{0}_{1}>'.format(sticker_name, str(sticker_id)))
    if database: db.add_conversation(userid,'Bot', response)
    log.info("Message '{0}' from {1} recognized as '{1}' sticker (id={2})".format(str(mid)[0:7], str(userid)[0:5], sticker_name, str(sticker_id)))
    log.info("Bot's response to user {1} sticker:  '{0}'".format(response, str(userid)))

def handle_attachment(message, userid, bot):
    """ React when the user sends a GIF, photos, videos, or any other non-text item."""
    bot.fb_fake_typing(userid, 0.8)
    image_url = r'https://media.giphy.com/media/L7ONYIPYXyc8/giphy.gif'
    bot.fb_send_image_url(userid, image_url)
    #or from local file: #bot.fb_send_image(userid, r'..\resources\CogitoErgoSum.jpg')
    try:
        mid = message.get('mid')
    except:
        mid = "GIFXXXXXXXXXXXXXX"
    if database: db.add_conversation(userid,'User','<GIF>')
    if database: db.add_conversation(userid, 'Bot', "<GIF>")
    log.info("Bot's response to user {1} gif:  '{0}'".format('<GIF>', str(userid)))


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
