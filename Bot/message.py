#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

import os
import logging
from datetime import date
from Bot.cognition import recognize_sticker
from Bot.user import *
import tokens
from settings import MINIMUM_CONFIDENCE
from pprint import pprint

class Message:
    """
        Has attributes taken from json post that was sent to the server from facebook.
        Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
        """

    def __init__(self, json_data):

        logging.debug(json_data)

        self.__dict__ = json_data  # previously json.loads

        self.is_echo = None     # rozróżnia bota od usera
        self.facebook_id = None     # niezależnie czy od czy do niego
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

            # get facebook_id, check if already in db and create if not:
            if self.is_echo:
                self.facebook_id = self.messaging['recipient']['id']
            else:
                self.facebook_id = self.messaging['sender']['id']


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
                            elif self.messaging['message']['attachments'][0]['payload']['template_type'] == 'generic':
                                # generic message
                                # TODO po co to? nie działa
                                self.url = str(self.messaging['message']['attachments'][0]['payload'])
                            else:
                                logging.warning("Unknown Template message with attachment: " + str(self.messaging['message']))
                        else:
                            self.type = "MessageWithAttachment"
                            logging.warning("Unknown message with attachment: " + str(self.messaging['message']))
                else:

                    self.text = self.messaging['message']['text']
                    if self.text.startswith('$okoń$'):
                        self.type = "DevMode"
                    else:
                        self.type = "TextMessage"
                        self.text = self.messaging['message']['text']

                        if 'nlp' in self.messaging['message']:
                            self.NLP = True
                            self.NLP_entities = []
                            nlp = self.messaging['message']['nlp']['entities']
                            entities = list(nlp.keys())
                            self.NLP_language = []
                            try:
                                for n in self.messaging['message']['nlp']['detected_locales']:
                                    self.NLP_language.append([n['locale'], n['confidence']])
                            except:
                                logging.warning(str(self.messaging))

                            if 'intent' in entities:
                                if nlp['intent'][0]['confidence'] >= MINIMUM_CONFIDENCE:
                                    self.NLP_intent = nlp['intent'][0]['value']
                                else:
                                    self.NLP_intent = None
                                entities.remove("intent")
                            else:
                                self.NLP_intent = None

                            for e in entities:
                                print(e)
                                if float(nlp[e][0]['confidence']) >= MINIMUM_CONFIDENCE:
                                    if e != 'datetime':
                                        self.NLP_entities.append({
                                            'entity': nlp[e][0]['_entity'],
                                            'value': nlp[e][0]['value'],
                                            'confidence': nlp[e][0]['confidence'],
                                            'body': nlp[e][0]['_body']})
                                        if '_role' in nlp[e][0]:
                                            self.NLP_entities[-1]['role'] = nlp[e][0]['_role']
                                    else:   # process date and time entities:
                                        self.NLP_entities.append({
                                            'entity': 'datetime',
                                            'value': nlp[e][0]['values'][0]['to']['value'],
                                            'confidence': nlp[e][0]['confidence'],
                                            'body': nlp[e][0]['_body']})
                                else:
                                    logging.warning(f"NLP entity not correct: {e}")
            else:
                self.type = "UnknownType"
        else:
            self.type = "UnknownType"

        # Logs:
        short_id = str(self.facebook_id)[0:5]
        if self.is_echo:
            if self.type == "UnknownType":
                logging.warning(
                    "This wasn't a message, perhaps it's an info request.")
            elif self.type == "Delivery":
                logging.info(f"BOT({short_id}) message has been delivered.")
            elif self.type == "ReadConfirmation":
                logging.info(f"BOT({short_id}) message has been read.")
            elif self.type == "StickerMessage":
                logging.info(f"BOT({short_id}): <sticker id={self.stickerID}>")
            elif self.type == "MessageWithAttachment":
                # TODO rozroznic na generic message (karuzela) i gify
                logging.info(f"BOT({short_id}): <GIF link={self.url[:15]}...>")
            elif self.type == "TextMessage":
                pass
                # logging.info(f"BOT({short_id}): '{self.text}'")
            else:
                logging.error("Unknown message type! Content: " + str(self.messaging))

        else:
            if self.type == "UnknownType":
                logging.warning("This wasn't a message, perhaps it's an info request.")
            elif self.type == "Delivery":
                logging.debug(f"USER({short_id}) message has been delivered.")
            elif self.type == "ReadConfirmation":
                logging.debug(f"USER({short_id}) message read by bot.")
            elif self.type == "StickerMessage":
                logging.info(f"USER({short_id}): <sticker id={self.stickerID}>")
            elif self.type == "GifMessage":
                logging.info(f"USER({short_id}): <GIF link={self.url}>")
            elif self.type == "MessageWithAttachment":
                logging.info(f"USER({short_id}): <MessageWithAttachment>")
            elif self.type == "LocationAnswer":
                logging.info(f"USER({short_id}): <Location: lat={self.latitude}, long={self.longitude}>")
            elif self.type == "DevMode":
                logging.info(f"DEVMODE({short_id}): '{self.text}'")
            elif self.type == "TextMessage":
                logging.info(f"USER({short_id}): '{self.text}'")
            else:
                logging.error("Unknown message type! Content: " + str(self.messaging))
