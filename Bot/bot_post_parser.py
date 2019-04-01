#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
from Dispatcher_app import use_local_tokens
from Bot.bot_cognition import recognize_sticker
if use_local_tokens: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens
log = logging.getLogger(os.path.basename(__file__))


class Message:
    """
    Has attributes taken from json post that was sent to the server from facebook.
    Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
    """

    def __init__(self, json_data):
        min_confidence = 0.90
        self.__dict__ = json_data  # previously json.loads
        self.id = self.entry[0]['id']
        if 'messaging' in self.entry[0]:
            self.messaging = self.entry[0]['messaging'][0]
            self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.senderID = self.messaging['sender']['id']
            self.recipientID = self.messaging['recipient']['id']
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
                        self.stickerName = recognize_sticker(self.stickerID)
                    else:
                        self.type = "MessageWithAttachment"
                        self.url = str(self.messaging['message']['url'])
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
                                if nlp['intent'][0]['confidence'] > min_confidence:
                                    self.NLP_intent = nlp['intent'][0]['value']
                                else:
                                    self.NLP_intent = None
                                entities.remove("intent")
                            else:
                                self.NLP_intent = None
                            for e in entities:
                                if nlp[e][0]['confidence'] > min_confidence:
                                    self.NLP_entities.append([
                                        nlp[e][0]['_entity'],
                                        nlp[e][0]['value'],
                                        nlp[e][0]['confidence'],
                                        nlp[e][0]['_body']
                                    ])
                        else:
                            self.NLP = False
            else:
                self.type = "UnknownType"
        else:
            self.type = "UnknownType"

        if int(self.recipientID) == int(tokens.fb_bot_id):
            self.recipient = "bot"
            self.sender = "user"
        else:
            self.recipient = "user"
            self.sender = "bot"

        # logs:
        if self.sender == "user":
            if self.type == "UnknownType":
                log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))
            elif self.type == "Delivery":
                log.info("Message from {0} has been delivered.".format(str(self.senderID)[0:5]))
            elif self.type == "ReadConfirmation":
                log.info("Message from {0} read by bot.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Message from user {0}:  '<sticker id={1}>'".format(str(self.senderID)[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Message from user {0}:  '<GIF link={1}>'".format(str(self.senderID)[0:5], self.url))
            elif self.type == "TextMessage":
                log.info("Message '{0}' from user {1}:  '{2}'".format(self.text, str(self.senderID)[0:5], self.messaging))
            else:
                log.error("Unknown message type! Content: " + message)
        if self.sender == "bot":
            if self.type == "UnknownType":
                log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(self.messaging))
            elif self.type == "Delivery":
                log.info("Bot's message to {0} has been delivered.".format(str(self.senderID)[0:5]))
            elif self.type == "ReadConfirmation":
                log.info("Bot's message read by {0}.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Bot's message to user {0}:  '<sticker id={1}>'".format(str(self.senderID)[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Bot's message to user {0}:  '<GIF link={1}>'".format(str(self.senderID)[0:5], self.url ))
            elif self.type == "TextMessage":
                log.info("Bot's message '{0}' to user {1}:  '{2}'".format(self.text, str(self.recipientID)[0:5], self.messaging))
            else:
                log.error("Unknown message type! Content: " + self.messaging)
        else:
            pass
            # log.error("Unknown sender! Content: " + str(self.messaging))
