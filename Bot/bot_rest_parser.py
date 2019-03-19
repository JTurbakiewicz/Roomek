#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

# import public modules:
import os
import json
import logging
log = logging.getLogger(os.path.basename(__file__))
from datetime import date

test_json_data = """
{"entry": [{
    "id": "1368143226655403",
    "messaging": [{
        "message": {
         "mid": "GZ1aEkkMhti8WBa22tk5lXWJoZXN9QKZWH8NjK5DYEFKf7dFmM-QZEUThzNoJk73q2QSR5AD_aEDnRjNS6XHbw",
         "nlp": {
            "entities": {
               "bye": [{
                  "_entity": "bye",
                  "confidence": 0.29891659254789,
                  "value": "true"}],
               "greetings": [{
                  "_entity": "greetings",
                  "confidence": 0.99988770484656,
                  "value": "true"}],
               "sentiment": [{
                  "_entity": "sentiment",
                  "confidence": 0.54351806476846,
                  "value": "positive"},
                  {"_entity": "sentiment",
                  "confidence": 0.43419978802319,
                  "value": "neutral"},
                  {"_entity": "sentiment",
                  "confidence": 0.022282101881069,
                  "value": "negative"}],
               "thanks": [{
                    "_entity": "thanks",
                    "confidence": 0.056984366913182,
                    "value": "true"}]}},
        "seq": 671186,
        "text": "hello"},
        "recipient": {"id": "1368143226655403"},
        "sender": {"id": "2231584683532589"},
        "timestamp": 1550245454526}],
   "time": 1550245455532}],
"object": "page"}"""


class Message():
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)
        self.id = self.entry[0]['id']
        self.time = date.fromtimestamp(float(self.entry[0]['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        self.messaging = self.entry[0]['messaging'][0]
        self.timestamp = date.fromtimestamp(float(self.messaging['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        self.sender = self.messaging['sender']['id']
        self.recipient = self.messaging['recipient']['id']
        if 'delivery' in self.messaging: self.type = "Delivery"
        elif 'read' in self.messaging: self.type = "ReadConfirmation"
        elif 'message' in self.messaging:
            self.mid = self.messaging['message']['mid']
            if 'attachments' in self.messaging['message']:
                if 'sticker_id' in self.messaging['message']: self.type = "StickerMessage"
                else: self.type = "MessageWithAttachment"
            else:
                self.type = "TextMessage"
                self.text = self.messaging['message']['text']
                self.NLP = self.messaging['message']['nlp']['entities']
        # TODO: elif '???' in self.messaging: self.type = "?????"
        else: self.type = "UnknownType"

message = Message(test_json_data)

print(message.entry[0])
print(message.id)
print(message.time)
print(message.timestamp)
print(message.type)
print(message.messaging)
print(message.sender)
print(message.recipient)
print(message.recipient)
print(message.NLP)




# def parse_rest_message(json_message):
#     for entry in user_message['entry']:
#         message_id = entry['id']
#         try:
#             messaging = entry['messaging']
#         except:
#             messaging = False
#             log.warning("This wasn't a message, perhaps it's an info request. Content:  \n"+str(user_message))
#
#         if messaging != False:
#             for message in messaging:
#                 if message.get('delivery'):
#                     deli = message['delivery']
#                     try:
#                         mids = deli.get('mids')
#                     except:
#                         mids = "DELI-MID"
#                     if int(message['recipient']['id']) == int(tokens.fb_bot_id):
#                         mid=""
#                         for m in mids:
#                             mid += ",'"+str(m)[0:7]+"'"
#                         mid = mid[1:]
#                         log.info("Bot's message: {0} to {1} has been delivered.".format("""mid""", str(message['sender']['id'][0:5])))
#                     else:
#                         log.info("Message {0} from {1} has been delivered.".format(str("""mid""")[0:7], str(message['sender']['id'][0:5])))
#                 elif message.get('read'):
#                     if int(message['recipient']['id']) == int(tokens.fb_bot_id):
#                         log.info("Bot's message read by {0}.".format(message['sender']['id'][0:5]))
#                     else:
#                         log.info("Message from {0} read by bot.".format(str(message['sender']['id'][0:5])))
#                 elif message.get('message'):
#                     senderid = message['sender']['id']
#                     recipientid = message['recipient']['id']
#                     message = message['message']
#                     user_message = message.get('text')
#                     try:
#                         mid = message.get('mid')
#                     except:
#                         mid = "TEXT-MID"
#                     if int(senderid) != int(tokens.fb_bot_id):
#                         if message.get('text'):
#                             log.info("Message '{0}' from user {1}:  '{2}'".format(str(mid)[0:7], str(senderid)[0:5], user_message))
#                         elif message.get('sticker_id'):
#                             log.info("Message '{0}' from user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
#                         elif message.get('attachments'):
#                             log.info("Message '{0}' from user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
#                     else:
#                         if message.get('text'):
#                             log.info("Bot's message '{0}' to user {1}:  '{2}'".format(str(mid)[0:7], recipientid[0:5], user_message))
#                         elif message.get('sticker_id'):
#                             log.info("Bot's message '{0}' to user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
#                         elif message.get('attachments'):
#                             log.info("Bot's message '{0}' to user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
#                 else:
#                     log.error("Unknown message type! Content: " + message)
