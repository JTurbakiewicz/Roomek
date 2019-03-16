#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Flask app that handles json webhook messages. """

local_tokens = True    #change to False if you want to use main tokens file
database = False        #turns the database connection on and off
witai = False           #turns the NLP connection on and off

# import public modules:
import os
import json
import logging
from flask import Flask, request
# import from own modules:
if database: from Databases import mysql_connection as db
from Bot.bot_logic import *
from Bot.facebook_webhooks import verify_fb_token

#disable Flask server logs unless errors:
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#set logging parameters:
log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO,    #levels in order: DEBUG, INFO, WARNING, EXCEPTION, ERROR, CRITICAL
                    #filename='/folder/myapp.log',
                    #filemode='w',
                    format='%(asctime)s %(levelname)s from %(name)s: %(message)s',    #%()-5s adds space if less then 5 letters
                    datefmt='%Y.%m.%d %H:%M:%S')

#initiate the web app
app = Flask(__name__)

#We will receive messages that Facebook sends to our bot at this endpoint:
@app.route("/", methods=['GET', 'POST'])

def receive_message():
    log.debug(request.get_json())           # Full json content
    if request.method == 'GET':             # if type is 'GET' it means FB wants to verify tokens
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(request, token_sent)
    else:                                   # if type is not 'GET' it must be 'POST' - we have a message
        user_message = request.get_json()   # read message as json
        handle_messages(user_message)       # process the message and respond
    return "Message Processed"

#If the program is executed (double-clicked), it will set name to main, thus run app:
if __name__ == "__main__":
    log.info("Main app has been restarted. New Flask app initialized (local_tokens: "+str(local_tokens)+", database: "+str(database)+", witai: "+str(witai)+").")
    app.run()
