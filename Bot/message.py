#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
from Bot.cognition import recognize_sticker
from Bot.user import *
import tokens


class Message:
    """
        Has attributes taken from json post that was sent to the server from facebook.
        Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
        """
    minimum_confidence = 0.85

    def __init__(self, json_data):

        self.__dict__ = json_data  # previously json.loads

        self.is_echo = None     # rozróżnia bota od usera
        self.user_id = None     # niezależnie czy od czy do niego
        self.mid = None         # id wiadomości z jsona, może nieprzydatne

        self.time = None
        self.timestamp = None

        self.type = None

        self.text = None

        self.NLP = None
        self.NLP_entities = None
        self.NLP_language = None
        self.NLP_intent = None

        self.latitude = None
        self.longitude = None

        self.stickerID = None
        self.sticker_name = None

        self.url = None


        if 'messaging' in self.entry[0]:
            self.messaging = self.entry[0]['messaging'][0]
            self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')

            self.is_echo = False
            try:
                if 'is_echo' in self.messaging['message']:
                    if self.messaging['message']['is_echo']:
                        self.is_echo = True
            except KeyError:
                logging.warning("messaging without message")

            # get user_id, check if already in db and create if not:
            if self.is_echo:
                self.user_id = self.messaging['recipient']['id']
            else:
                self.user_id = self.messaging['sender']['id']


            if 'delivery' in self.messaging:
                self.type = "Delivery"
            elif 'read' in self.messaging:
                self.type = "ReadConfirmation"
            elif 'message' in self.messaging:
                self.mid = 1234567890   # TODO mid z wiadomości
                # TODO: delivery has mids not mid
                # self.mid = self.messaging['message']['mid']

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
                            print(nlp)
                            entities = list(nlp.keys())
                            self.NLP_language = []
                            try:
                                for n in self.messaging['message']['nlp']['detected_locales']:
                                    self.NLP_language.append([n['locale'], n['confidence']])
                                    print(self.NLP_language)
                            except:
                                logging.warning("ERROR02 " + str(self.messaging))

                            if 'intent' in entities:
                                if nlp['intent'][0]['confidence'] > self.minimum_confidence:
                                    self.NLP_intent = nlp['intent'][0]['value']
                                else:
                                    self.NLP_intent = None
                                entities.remove("intent")
                            else:
                                self.NLP_intent = None
                            for e in entities:
                                if float(nlp[e][0]['confidence']) > self.minimum_confidence:
                                    logging.info(self.NLP_entities)
                                    logging.info(nlp[e][0])

                                    try:
                                        self.NLP_entities.append([
                                            nlp[e][0]['_entity'],
                                            nlp[e][0]['value'],
                                            nlp[e][0]['confidence'],
                                            nlp[e][0]['_body']
                                        ])
                                    except:
                                        logging.warning("NIE UDAŁO SIĘ ZNALEŹĆ JAKIEGOŚ PARAMETRU NLP! "+str(self.messaging))
            else:
                self.type = "UnknownType"
        else:
            self.type = "UnknownType"


        # Logs:
        short_id = str(self.user_id)[0:5]
        if self.is_echo:
            if self.type == "UnknownType":
                logging.warning(
                    "This wasn't a message, perhaps it's an info request.")
            elif self.type == "Delivery":
                logging.info("BOT({0}) message has been delivered.".format(short_id))
            elif self.type == "ReadConfirmation":
                logging.info("BOT({0}) message has been read.".format(short_id))
            elif self.type == "StickerMessage":
                logging.info("BOT({0}): <sticker id={1}>".format(short_id, self.stickerID))
            elif self.type == "MessageWithAttachment":
                logging.info("BOT({0}): <GIF link={1}>".format(short_id, self.url))
            elif self.type == "TextMessage":
                logging.info("BOT({0}): '{1}'".format(short_id, self.text))
            else:
                logging.error("Unknown message type! Content: " + self.messaging)

        else:
            if self.type == "UnknownType":
                logging.warning("This wasn't a message, perhaps it's an info request.")
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
