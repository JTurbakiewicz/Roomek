#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
from Dispatcher_app import use_local_tokens, use_database
from Bot.cognition import recognize_sticker
from Bot.user import *
if use_local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
# TODO if use_database: from Databases.... import update_user

# # in the future fetch user ids from the DB:
# users = {}  # { userID : User() }
# if use_database:
#     users_in_db = db.get_all(table_name='users', fields_to_get='facebook_id')
#     for user_in_db in users_in_db:
#         users[user['facebook_id']] = user_in_db


class Message:
    """
    Has attributes taken from json post that was sent to the server from facebook.
    Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
    """

    def __init__(self, json_data):
        minimum_confidence = 0.85
        self.__dict__ = json_data  # previously json.loads
        self.id = self.entry[0]['id']
        # TODO już teraz wiadomo czy od usera czy od bota!
        if 'messaging' in self.entry[0]:
            self.messaging = self.entry[0]['messaging'][0]
            self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.senderID = self.messaging['sender']['id']
            self.recipientID = self.messaging['recipient']['id']
            if self.senderID not in users:
                # create new user and add to the dictionary (in class creator)
                self.user = User(self.senderID)
            else:
                # assign existing user to this object
                self.user = users[self.senderID]
            if 'delivery' in self.messaging: self.type = "Delivery"
            elif 'read' in self.messaging: self.type = "ReadConfirmation"
            elif 'message' in self.messaging:
                self.mid = 1234567890
                # self.mid = self.messaging['message']['mid']
                # TODO: delivery has mids not mid
                if 'attachments' in self.messaging['message']:
                    if 'sticker_id' in self.messaging['message']:
                        self.type = "StickerMessage"
                        self.stickerID = self.messaging['message']['sticker_id']
                        self.sticker_name = recognize_sticker(self.stickerID)
                    elif self.messaging['message']['attachments'][0]['type'] == "location":
                        self.type = "LocationAnswer"
                        self.latitude = self.messaging['message']['attachments'][0]['payload']['coordinates']['lat']
                        self.longitude = self.messaging['message']['attachments'][0]['payload']['coordinates']['long']
                    else:
                        if self.messaging['message']['attachments'][0]['type'] == 'image':
                            # gif etc.
                            self.type = "GifMessage"
                            self.url = str(self.messaging['message']['attachments'][0]['payload']['url'])
                        elif self.messaging['message']['attachments'][0]['type'] == 'template':
                            self.type = "MessageWithAttachment"
                            if self.messaging['message']['attachments'][0]['payload']['template_type'] == 'button':
                                    # button message
                                self.url = str(self.messaging['message']['attachments'][0]['payload']['buttons'])
                            elif self.messaging['message']['attachments'][0]['payload']['template_type'] == 'list':
                                # list message
                                self.url = str(self.messaging['message']['attachments'][0]['payload']['buttons'])
                            else:
                                print("Unknown Template message with attachment: " + str(self.messaging['message']))
                        else:
                            self.type = "MessageWithAttachment"
                            print("Unknown message with attachment: " + str(self.messaging['message']))
                else:
                    self.text = self.messaging['message']['text']
                    if self.text.startswith('bottest'):
                        self.type = "BotTest"
                    else:
                        self.type = "TextMessage"
                        self.text = self.messaging['message']['text']
                        if 'nlp' in self.messaging['message']:
                            self.NLP = True
                            self.NLP_entities = []
                            nlp = self.messaging['message']['nlp']['entities']
                            entities = list(nlp.keys())
                            if 'intent' in entities:
                                if nlp['intent'][0]['confidence'] > minimum_confidence:
                                    self.NLP_intent = nlp['intent'][0]['value']
                                else:
                                    self.NLP_intent = None
                                entities.remove("intent")
                            else:
                                self.NLP_intent = None
                            for e in entities:
                                if float(nlp[e][0]['confidence']) > 0.8:   # minimum_confidence:
                                    try:
                                        self.NLP_entities.append([
                                            nlp[e][0]['_entity'],
                                            nlp[e][0]['value'],
                                            nlp[e][0]['confidence'],
                                            nlp[e][0]['_body']
                                        ])
                                    except:
                                        logging.warning(self.messaging)
                        else:
                            self.NLP = False
            else:
                self.type = "UnknownType"
        else:
            self.type = "UnknownType"

        try:
            if int(self.senderID) == int(tokens.fb_bot_id):
                self.sender = "bot"
                self.recipient = "user"
            else:
                self.sender = "user"
                self.recipient = "bot"
            # Logs:
            if self.sender == "user":
                short_id = str(self.senderID)[0:5]
                if self.type == "UnknownType":
                    logging.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))
                elif self.type == "Delivery":
                    logging.debug("USER({0}) message has been delivered.".format(short_id))
                elif self.type == "ReadConfirmation":
                    logging.debug("USER({0}) message read by bot.".format(short_id))
                elif self.type == "StickerMessage":
                    logging.info("USER({0}): <sticker id={1}>".format(short_id, self.stickerID))
                elif self.type == "GifMessage":
                    logging.info("USER({0}): <GIF link={1}>".format(short_id, self.url))
                elif self.type == "MessageWithAttachment":
                    logging.info("USER({0}): <MessageWithAttachment>".format(short_id))
                elif self.type == "LocationAnswer":
                    logging.info("USER({0}): <Location: lat={1}, long={2}>".format(short_id, self.latitude, self.longitude))
                elif self.type == "TextMessage":
                    logging.info("USER({0}): '{1}'".format(short_id, self.text))
                else:
                    logging.error("Unknown message type! Content: " + str(self.messaging))
            # if self.sender == "bot":
            #     try:
            #         short_id = str(self.recipientID)[0:5]
            #         if self.type == "UnknownType":
            #             logging.warning(
            #                 "This wasn't a message, perhaps it's an info request. Content:  \n" + str(self.messaging))
            #         elif self.type == "Delivery":
            #             logging.info("BOT({0}) message has been delivered.".format(short_id))
            #         elif self.type == "ReadConfirmation":
            #             logging.info("BOT({0}) message has been read.".format(short_id))
            #         elif self.type == "StickerMessage":
            #             logging.info("BOT({0}): <sticker id={1}>".format(short_id, self.stickerID))
            #         elif self.type == "MessageWithAttachment":
            #             logging.info("BOT({0}): <GIF link={1}>".format(short_id, self.url))
            #         elif self.type == "TextMessage":
            #             logging.info("BOT({0}): '{1}'".format(short_id, self.text))
            #         else:
            #             logging.error("Unknown message type! Content: " + self.messaging)
            #     except:
            #         logging.warning("Couldn't assign a recipientID. Content:  \n"+str(self.messaging))
        except AttributeError:
            logging.error("that was probably a sample test message")
