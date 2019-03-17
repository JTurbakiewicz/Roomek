#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Functions for basic bot behaviours. """

# import public modules:
import json
import logging
from flask import Flask, request
log = logging.getLogger(os.path.basename(__file__))

def parse_rest_message(rest_message):
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
                        mids = "DELI-MID"
                    if int(message['recipient']['id']) == int(tokens.fb_bot_id):
                        mid=""
                        for m in mids:
                            mid += ",'"+str(m)[0:7]+"'"
                        mid = mid[1:]
                        log.info("Bot's message: {0} to {1} has been delivered.".format("""mid""", str(message['sender']['id'][0:5])))
                    else:
                        log.info("Message {0} from {1} has been delivered.".format(str("""mid""")[0:7], str(message['sender']['id'][0:5])))
                elif message.get('read'):
                    if int(message['recipient']['id']) == int(tokens.fb_bot_id):
                        log.info("Bot's message read by {0}.".format(message['sender']['id'][0:5]))
                    else:
                        log.info("Message from {0} read by bot.".format(str(message['sender']['id'][0:5])))
                elif message.get('message'):
                    senderid = message['sender']['id']
                    recipientid = message['recipient']['id']
                    message = message['message']
                    user_message = message.get('text')
                    try:
                        mid = message.get('mid')
                    except:
                        mid = "TEXT-MID"
                    if int(senderid) != int(tokens.fb_bot_id):
                        if message.get('text'):
                            log.info("Message '{0}' from user {1}:  '{2}'".format(str(mid)[0:7], str(senderid)[0:5], user_message))
                        elif message.get('sticker_id'):
                            log.info("Message '{0}' from user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
                        elif message.get('attachments'):
                            log.info("Message '{0}' from user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
                    else:
                        if message.get('text'):
                            log.info("Bot's message '{0}' to user {1}:  '{2}'".format(str(mid)[0:7], recipientid[0:5], user_message))
                        elif message.get('sticker_id'):
                            log.info("Bot's message '{0}' to user {1}:  '<sticker id={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('sticker_id')) ))
                        elif message.get('attachments'):
                            log.info("Bot's message '{0}' to user {1}:  '<GIF link={2}>'".format(str(mid)[0:7], str(senderid)[0:5], str(message.get('url')) ))
                else:
                    log.error("Unknown message type! Content: " + message)
