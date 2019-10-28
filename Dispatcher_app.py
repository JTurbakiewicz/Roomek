#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Flask app that handles json webhook messages. """

import os
import logging
from settings import *

logging.basicConfig(level=logging_level,
                    # filename='/folder/myapp.log',
                    # filemode='w',
                    format='%(asctime)s %(levelname)-7s %(module)-19s L%(lineno)-3d: %(message)s',
                    # %()-5s adds space if less then 5 letters
                    datefmt='%m.%d %H:%M:%S')

# disable Flask server logs unless errors and set our logging parameters:
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from flask import Flask, request
from Databases import mysql_connection as db
from Bot.logic import handle_message
from Bot.message import Message
from Bot.user import User
from Bot.facebook_webhooks import verify_fb_token

# initiate the web app
app = Flask(__name__)

# We will receive messages that Facebook sends to our bot at this endpoint:
@app.route("/fb/", methods=['GET', 'POST'])
def receive_message():
    logging.debug(request.get_json())          # Full json content
    if request.method == 'GET':            # if type is 'GET' it means FB wants to verify tokens
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(request, token_sent)
    else:                                  # if type is not 'GET' it must be 'POST' - we have a message
        json_message = request.get_json()  # read message as json
        message = Message(json_message)

        if db.user_exists(message.facebook_id):
            user = db.get_user(message.facebook_id)
        elif json_message['facebook_id']:
            user = User(message.facebook_id)
        else:
            user = User(88888888)
            logging.warning(f"Message without facebook_id: {json_message}")

        if message.mid and message.mid not in db.get(table='conversations', fields_to_get='mid'):
            handle_message(message, user)  # process the message and respond
        else:
            logging.warning(f"Message was already processed and was probably resent by facebook: {json_message}")

    return "Message Processed"

# TODO dodać API żeby np. zacząć od nowa po kliknięciu w menu
# @app.route("/api/", methods=['GET', 'POST'])
# def call_api():
#     logging.debug(request.get_json())       # Full json content
#     json_message = request.get_json()       # read message as json
#     print(json_message)
#     return "Message Processed"

# If the program is executed (double-clicked), it will set name to main, thus run app:
if __name__ == "__main__":
    logging.info("Main app has been restarted. New Flask app initialized")
    app.run()
