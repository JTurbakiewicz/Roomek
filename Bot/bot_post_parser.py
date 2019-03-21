#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

# import public modules:
import os
import json
import logging
log = logging.getLogger(os.path.basename(__file__))
from datetime import date
if tokens_local: from Bot.tokens import tokens_local as tokens
else: from Bot.tokens import tokens

class Message():
    """
    Has attributes taken from json post that was sent to the server from facebook.
    Types: TextMessage/StickerMessage/MessageWithAttachment/Delivery/ReadConfirmation/UnknownType
    """

    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)
        self.id = self.entry[0]['id']
        self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        self.messaging = self.entry[0]['messaging'][0]
        self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        self.senderID = self.messaging['sender']['id']
        self.recipientID = self.messaging['recipient']['id']
        if 'delivery' in self.messaging: self.type = "Delivery"
        elif 'read' in self.messaging: self.type = "ReadConfirmation"
        elif 'message' in self.messaging:
            self.mid = self.messaging['message']['mid']
            if 'attachments' in self.messaging['message']:
                if 'sticker_id' in self.messaging['message']:
                    self.type = "StickerMessage"
                    self.stickerID = self.messaging['message']['sticker_id']
                else:
                    self.type = "MessageWithAttachment"
                    self.url = str(self.messaging['message']['url'])
            else:
                self.type = "TextMessage"
                self.text = self.messaging['message']['text']
                if 'nlp' in self.messaging['message']:
                    self.NLP = True
                    self.NLP_entities = self.messaging['message']['nlp']['entities']
                else:
                    self.NLP = False
        # TODO: elif '???' in self.messaging: self.type = "?????"
        else: self.type = "UnknownType"

        if int(self.recipientID) == int(tokens.fb_bot_id):
            self.recipient = "bot"
            self.sender = "user"
        else:
            self.recipient = "user"
            self.sender = "bot"

        #logs:
        if self.sender == "user":
            if self.type == "UnknownType": log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))
            elif self.type == "Delivery":
                log.info("Message {0} from {1} has been delivered.".format(self.mid[0:7], self.senderID[0:5]))
            elif self.type == "ReadConfirmation":
                log.info("Message from {0} read by bot.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Message '{0}' from user {1}:  '<sticker id={2}>'".format(self.mid[0:7], self.senderID[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Message '{0}' from user {1}:  '<GIF link={2}>'".format(self.mid[0:7], self.senderID[0:5], self.url))
            elif self.type == "TextMessage":
                log.info("Message '{0}' from user {1}:  '{2}'".format(self.mid[0:7], self.senderID[0:5], self.messaging))
            else: log.error("Unknown message type! Content: " + message)
        if self.sender == "bot":
            if self.type == "UnknownType": log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(self.messaging))
            elif self.type == "Delivery":
                log.info("Bot's message: {0} to {1} has been delivered.".format("""mid""", str(self.senderID[0:5])))
            elif self.type == "ReadConfirmation":
                log.info("Bot's message read by {0}.".format(self.senderID[0:5]))
            elif self.type == "StickerMessage":
                log.info("Bot's message '{0}' to user {1}:  '<sticker id={2}>'".format(self.mid[0:7], self.senderID[0:5], self.stickerID))
            elif self.type == "MessageWithAttachment":
                log.info("Bot's message '{0}' to user {1}:  '<GIF link={2}>'".format(self.mid[0:7], self.senderID[0:5], self.url ))
            elif self.type == "TextMessage":
                log.info("Bot's message '{0}' to user {1}:  '{2}'".format(self.mid[0:7], self.recipientID[0:5], self.messaging))
            else: log.error("Unknown message type! Content: " + self.messaging)
        else:
            log.error("Unknown sender! Content: " + str(self.messaging))

    def best_entity(self, minimum=0.90):
        """ Return best matching entity from NLP or None. """
        if 'nlp' in self.messaging['message']:
            entities = list(self.NLP_entities.keys())
            #entities.remove("sentiment")
            confidence = []
            for c in list(self.NLP_entities.values()):
                confidence.append(c[0]['confidence'])
            if max(confidence)>minimum:
                # create dictionary entity:confidence:
                iterable = zip(entities, confidence)
                pairs = {key: value for (key, value) in iterable}
                best_match = max(pairs, key=pairs.get)
                return [best_match, str(max(confidence))]
            else:
                return None
        else:
            return None

# TESTING:
#
# fb_bot_id = '1368143226655403'
#
# test_json_data = """
# {"entry": [{
#     "id": "1368143226655403",
#     "messaging": [{
#         "message": {
#          "mid": "GZ1aEkkMhti8WBa22tk5lXWJoZXN9QKZWH8NjK5DYEFKf7dFmM-QZEUThzNoJk73q2QSR5AD_aEDnRjNS6XHbw",
#          "nlp": {
#             "entities": {
#                "bye": [{
#                   "_entity": "bye",
#                   "confidence": 0.29891659254789,
#                   "value": "true"}],
#                "greetings": [{
#                   "_entity": "greetings",
#                   "confidence": 0.99988770484656,
#                   "value": "true"}],
#                "sentiment": [{
#                   "_entity": "sentiment",
#                   "confidence": 0.54351806476846,
#                   "value": "positive"},
#                   {"_entity": "sentiment",
#                   "confidence": 0.43419978802319,
#                   "value": "neutral"},
#                   {"_entity": "sentiment",
#                   "confidence": 0.022282101881069,
#                   "value": "negative"}],
#                "thanks": [{
#                     "_entity": "thanks",
#                     "confidence": 0.056984366913182,
#                     "value": "true"}]}},
#         "seq": 671186,
#         "text": "hello"},
#         "recipient": {"id": "1368143226655403"},
#         "sender": {"id": "2231584683532589"},
#         "timestamp": 1550245454526}],
#    "time": 1550245455532}],
# "object": "page"}"""

# message = Message(test_json_data)
#
# print(message.entry[0])
# print(message.id)
# print(message.time)
# print(message.timestamp)
# print(message.type)
# print(message.messaging)
# print(message.text)
# print(message.senderID)
# print(message.sender)
# print(message.recipientID)
# print(message.recipient)
# print(message.NLP)
# print("_________________________")
# print(message.NLP_entities)
# print("_________________________")
# print(list(message.NLP_entities.keys()))
# print("_________________________")
# print(list(message.NLP_entities.values()))
# print("_________________________")
# print(message.best_entity())
