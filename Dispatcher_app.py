#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Flask app that handles json webhook messages. """

import os
import logging

# ------------------app-configuration----------------------------------------------------------------
use_local_tokens = True         # change to False if you want to use main tokens file
use_database = False            # turns the database connection on and off
use_witai = False               # turns the NLP connection on and off
fake_typing = False
logging_level = logging.DEBUG   # levels in order: DEBUG, INFO, WARNING, EXCEPTION, ERROR, CRITICAL
# ---------------------------------------------------------------------------------------------------

from flask import Flask, request
# import from own modules:
if use_database: from Databases import mysql_connection as db
from Bot.logic import *
from Bot.facebook_webhooks import verify_fb_token

# disable Flask server logs unless errors and set our logging parameters:
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging_level,
                    # filename='/folder/myapp.log',
                    # filemode='w',
                    # %(pathname)s Full pathname of the source file where the logging call was issued(if available).
                    # %(filename)s Filename portion of pathname.
                    # %(module)s Module (name portion of filename).
                    # %(funcName)s Name of function containing the logging call.
                    # %(lineno)d Source line number where the logging call was issued (if available).
                    format='%(asctime)s %(levelname)-7s %(module)-19s L%(lineno)-3d: %(message)s',
                    # %()-5s adds space if less then 5 letters
                    datefmt='%m.%d %H:%M:%S')

# initiate the web app
app = Flask(__name__)

# We will receive messages that Facebook sends to our bot at this endpoint:


@app.route("/", methods=['GET', 'POST'])
def receive_message():
    logging.debug(request.get_json())          # Full json content
    if request.method == 'GET':            # if type is 'GET' it means FB wants to verify tokens
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(request, token_sent)
    else:                                  # if type is not 'GET' it must be 'POST' - we have a message
        # print("______________________________________________________________________________________________")
        json_message = request.get_json()  # read message as json
        handle_message(json_message)       # process the message and respond
    return "Message Processed"


# If the program is executed (double-clicked), it will set name to main, thus run app:
if __name__ == "__main__":
    logging.info("Main app has been restarted. New Flask app initialized (tokens_local: "+str(use_local_tokens)+", database: "+str(use_database)+", witai: "+str(use_witai)+").")
    app.run()
