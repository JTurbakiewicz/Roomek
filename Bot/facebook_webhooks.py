#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This code contains functions for sending FB messages and other actions.
It mostly contains modified version of Davidchua's pymessenger(https://github.com/davidchua/pymessenger).
"""

from enum import Enum
import requests
from requests_toolbelt import MultipartEncoder
from time import sleep
import hashlib
import hmac
import six
import os
import random
import logging
import tokens


# TODO add a 'tag' NON_PROMOTIONAL_SUBSCRIPTION
# TODO add a 'messaging_type' TYPE_MESSAGE_TYPE
# https://developers.facebook.com/docs/messenger-platform/send-messages/message-tags

DEFAULT_API_VERSION = 3.2   # 2.6


def verify_fb_token(request, token_sent):
    """Take token sent by facebook and verify if it matches"""
    if token_sent == tokens.fb_verification:
        return request.args.get("hub.challenge")
        logging.info("FB token verification succesfull.")
    else:
        logging.warning("Failed to verify FB token.")
        return 'You are seeing this text, because you have probably entered the website and it is only supposed to exchange posts with facebook bot. You return invalid verification token. Just close this. For more info contact: artomczak@gmail.com'


class NotificationType(Enum):
    regular = "REGULAR"
    silent_push = "SILENT_PUSH"
    no_push = "NO_PUSH"


class Bot:
    def __init__(self, access_token, **kwargs):
        """
            @required:
                access_token
            @optional:
                api_version
                app_secret
        """

        self.api_version = kwargs.get('api_version') or DEFAULT_API_VERSION
        self.app_secret = kwargs.get('app_secret')
        self.graph_url = f'https://graph.facebook.com/v{self.api_version}'
        self.access_token = access_token

    @property
    def auth_args(self):
        if not hasattr(self, '_auth_args'):
            auth = {
                'access_token': self.access_token
            }
            if self.app_secret is not None:
                appsecret_proof = generate_appsecret_proof(self.access_token, self.app_secret)
                auth['appsecret_proof'] = appsecret_proof
            self._auth_args = auth
        return self._auth_args

    def fb_send_recipient(self, userid, payload, notification_type=NotificationType.regular):
        payload['recipient'] = {
            'id': userid
        }
        payload['notification_type'] = notification_type.value
        return self.fb_send_raw(payload)

    def fb_send_message(self, userid, message, notification_type=NotificationType.regular):
        return self.fb_send_recipient(userid, {
            'message': message
        }, notification_type)

    def fb_send_attachment(self, userid, attachment_type, attachment_path,
                        notification_type=NotificationType.regular):
        """Send an attachment to the specified recipient using local path.
        Input:
            userid: recipient id to send to
            attachment_type: type of attachment (image, video, audio, file)
            attachment_path: Path of attachment
        Output:
            Response from API as <dict>
        """
        payload = {
            'recipient': {
                {
                    'id': userid
                }
            },
            'notification_type': notification_type,
            'message': {
                {
                    'attachment': {
                        'type': attachment_type,
                        'payload': {}
                    }
                }
            },
            'filedata': (os.path.basename(attachment_path), open(attachment_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.graph_url, data=multipart_data,
                             params=self.auth_args, headers=multipart_header).json()

    def fb_send_attachment_url(self, userid, attachment_type, attachment_url,
                            notification_type=NotificationType.regular):
        """Send an attachment to the specified recipient using URL.
        Input:
            userid: recipient id to send to
            attachment_type: type of attachment (image, video, audio, file)
            attachment_url: URL of attachment
        Output:
            Response from API as <dict>
        """
        return self.fb_send_message(userid, {
            'attachment': {
                'type': attachment_type,
                'payload': {
                    'url': attachment_url
                }
            }
        }, notification_type)

    def fb_send_text_message(self, userid, message, notification_type=NotificationType.regular):
        """Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            userid: recipient id to send to
            message: message to send
        Output:
            Response from API as <dict>
        """
        # TODO character limit error
        if type(message) == list:
            message = random.choice(message)

        # if use_database: db.add_conversation(str(userid), 'User', message)
        logging.info(f"BOT({str(userid)[0:5]}): '{str(message)}'")

        return self.fb_send_message(userid, {
            'text': message
        }, notification_type)

    def fb_send_offers_carousel(self, userid, offers):
        elements = []
        for offer in offers:
            t = f"{offer['area']}m2 za {offer['price']}zł, {offer['location']}"
            st = f"{offer['provider']}: {offer['title']}"
            buttons = [self.fb_create_button(title="Sprawdź", url=offer['link']),
                self.fb_create_button(title="Podoba mi się!", url=offer['link'])]
            elements.append(self.fb_create_element(title=t, subtitle=st, image_url=offer['picUrl'], url=offer['link'], buttons=buttons, height="TALL"))

        self.fb_send_generic_message(userid, elements)

    def fb_send_generic_message(self, userid, elements, notification_type=NotificationType.regular):
        """Send generic messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
        Input:
            userid: recipient id to send to
            elements: generic message elements to send
        Output:
            Response from API as <dict>
        """
        logging.debug("Trying to send generic message.")

        return self.fb_send_message(userid, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        }, notification_type)

    # def fb_send_list_message(self, userid, elements=[], buttons=[], notification_type=NotificationType.regular):
    #     logging.debug("Trying to send list message.")
    #
    #     return self.fb_send_message(userid, {
    #         "attachment": {
    #             "type": "template",
    #             "payload": {
    #                 "template_type": "list",
    #                 "top_element_style": "compact",
    #                 "elements": [
    #                     {
    #                         "title": "Proba",
    #                         "subtitle": "See all our colors",
    #                         "default_action": {
    #                             "type": "web_url",
    #                             "url": "https://peterssendreceiveapp.ngrok.io/view?item=100",
    #                             "messenger_extensions": "false",
    #                             # "messenger_extensions": False,
    #                             "webview_height_ratio": "tall"
    #                         }
    #                     },
    #                     {
    #                         "title": "Gruba",
    #                         "subtitle": "See all our colors 2",
    #                         "default_action": {
    #                             "type": "web_url",
    #                             "url": "https://peterssendreceiveapp.ngrok.io/view?item=100",
    #                             "messenger_extensions": "false",
    #                             # "messenger_extensions": False,
    #                             "webview_height_ratio": "tall"
    #                         }
    #                     }
    #                 ],
    #                  "buttons": buttons
    #             }
    #         }
    #     }, notification_type)

    # def fb_send_button_message(self, userid, text="abc", buttons=[], notification_type=NotificationType.regular):
    #     """Send text messages to the specified recipient.
    #     https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
    #     Input:
    #         userid: recipient id to send to
    #         text: text of message to send
    #         buttons: buttons to send
    #     Output:
    #         Response from API as <dict>
    #     """
    #     logging.debug("Trying to send button message.")
    #
    #     return self.fb_send_message(userid, {
    #         "attachment": {
    #             "type": "template",
    #             "payload": {
    #                 "template_type": "button",
    #                 "text": text,
    #                 "buttons": buttons
    #             }
    #         }
    #     }, notification_type)

    def fb_create_button(self, title, url):
        """
        https://developers.facebook.com/docs/messenger-platform/send-messages/buttons
        """
        button = {
                "title": str(title),
                "type": "web_url",
                # "type":"postback",
                "url": url
                # "messenger_extensions": "true",
                # "webview_height_ratio": "tall",
                # "payload":"DEVELOPER_DEFINED_PAYLOAD"
                # "fallback_url": "http://www.olx.com"
            }
        return button

    def fb_create_element(self, title="", subtitle="", image_url="", url="", height="TALL", buttons=[]):
        element={
            "title": str(title),
            "subtitle": str(subtitle),
            "image_url": image_url,
            "buttons": buttons,
            "default_action": {
                "type": "web_url",      # web_url,
                "url": url,
                "webview_height_ratio": height     # COMPACT, TALL, FULL
                }
            }
        return element

    def fb_send_action(self, userid, action, notification_type=NotificationType.regular):
        """Send typing indicators or send read receipts to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions

        Input:
            userid: recipient id to send to
            action: action type (mark_seen, typing_on, typing_off)
        Output:
            Response from API as <dict>
        """
        return self.fb_send_recipient(userid, {
            'sender_action': action
        }, notification_type)

    def fb_send_image(self, userid, image_path, notification_type=NotificationType.regular):
        """Send an image to the specified recipient.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            userid: recipient id to send to
            image_path: path to image to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment(userid, "image", image_path, notification_type)

    def fb_send_image_url(self, userid, image_url, notification_type=NotificationType.regular):
        """Send an image to specified recipient using URL.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            userid: recipient id to send to
            image_url: url of image to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment_url(userid, "image", image_url, notification_type)


    # def fb_send_quick_replies(self, userid, reply_message = "", replies = ['a','b','c'], location=False, notification_type=NotificationType.regular):

    # TODO Temp:
    def fb_send_quick_replies(self, userid, reply_message="", replies=['a', 'b', 'c'], location=False, notification_type=NotificationType.regular):

        """Send quick replies to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
        Input:
            userid: recipient id to send to
            reply_message: text of message to send
            replies: quick_replies to send e.g.['a','b','c']
        Output:
            Response from API as <dict>
        """

        # TODO add icon near quick replies: {...,"image_url":"http://example.com/img/red.png"}
        reply_options = []
        if location:
            reply_options.append({"content_type": "location", "title": "mapka"})
        for option in replies:
            content = {
                "content_type": "text",
                "title": str(option),
                "payload": "<POSTBACK_PAYLOAD>"
            }
            reply_options.append(content)

        # if use_database: db.add_conversation(str(userid), 'User', message)
        logging.info(f"BOT({str(userid)[0:5]}): '{str(reply_message)}' Replies{str(replies)}")

        return self.fb_send_message(userid, {
            "text": reply_message,
            "quick_replies": reply_options
        }, notification_type)

    def fb_fake_typing(self, userid, duration=0.6):
        """ Pretend the bot is typing for n seconds. """
        # TODO shouldn't it be waiting a bit before typing? sleep(duration/2)
        self.fb_send_action(userid, 'typing_on')
        sleep(duration)
        self.fb_send_action(userid, 'typing_off')

    def fb_get_user_info(self, userid, fields=None):
        """Getting information about the user
        https://developers.facebook.com/docs/messenger-platform/user-profile
        Input:
        userid: recipient id to send to
        Output:
        Response from API as <dict>
        """
        params = {}
        if fields is not None and isinstance(fields, (list, tuple)):
            params['fields'] = ",".join(fields)

            params.update(self.auth_args)

            request_endpoint = f'{self.graph_url}/{userid}'
            response = requests.get(request_endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None

    def fb_send_audio(self, userid, audio_path, notification_type=NotificationType.regular):
        """Send audio to the specified recipient.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            userid: recipient id to send to
            audio_path: path to audio to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment(userid, "image", audio_path, notification_type)

    def fb_send_audio_url(self, userid, audio_url, notification_type=NotificationType.regular):
        """Send audio to specified recipient using URL.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            userid: recipient id to send to
            audio_url: url of audio to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment_url(userid, "audio", audio_url, notification_type)

    def fb_send_video(self, userid, video_path, notification_type=NotificationType.regular):
        """Send video to the specified recipient.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            userid: recipient id to send to
            video_path: path to video to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment(userid, "video", video_path, notification_type)

    def fb_send_video_url(self, userid, video_url, notification_type=NotificationType.regular):
        """Send video to specified recipient using URL.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            userid: recipient id to send to
            video_url: url of video to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment_url(userid, "video", video_url, notification_type)

    def fb_send_file(self, userid, file_path, notification_type=NotificationType.regular):
        """Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            userid: recipient id to send to
            file_path: path to file to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment(userid, "file", file_path, notification_type)

    def fb_send_file_url(self, userid, file_url, notification_type=NotificationType.regular):
        """Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            userid: recipient id to send to
            file_url: url of file to be sent
        Output:
            Response from API as <dict>
        """
        return self.fb_send_attachment_url(userid, "file", file_url, notification_type)

    def fb_send_raw(self, payload):
        request_endpoint = f'{self.graph_url}/me/messages'
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        result = response.json()

        return result


def get_user_info(facebook_id):
    request_endpoint = f"https://graph.facebook.com/v2.6/{facebook_id}"
    response = requests.get(
        request_endpoint,
        params={
            "access_token": str(tokens.fb_access),
            "fields": "first_name,last_name,profile_pic,gender,locale,timezone"
        }
    )
    result = response.json()

    return result


def validate_hub_signature(app_secret, request_payload, hub_signature_header):
    """
        @inputs:
            app_secret: Secret Key for application
            request_payload: request body
            hub_signature_header: X-Hub-Signature header sent with request
        @outputs:
            boolean indicated that hub signature is validated
    """
    try:
        hash_method, hub_signature = hub_signature_header.split('=')
    except:
        pass
    else:
        digest_module = getattr(hashlib, hash_method)
        if six.PY2:
            hmac_object = hmac.new(
                str(app_secret), unicode(request_payload), digest_module)
        else:
            hmac_object = hmac.new(bytearray(app_secret, 'UTF-8'), str(request_payload).encode('UTF-8'), digest_module)
        generated_hash = hmac_object.hexdigest()
        if hub_signature == generated_hash:
            return True
    return False


def generate_appsecret_proof(access_token, app_secret):
    """
        @inputs:
            access_token: page access token
            app_secret_token: app secret key
        @outputs:
            appsecret_proof: HMAC-SHA256 hash of page access token
                using app_secret as the key
    """
    if six.PY2:
        hmac_object = hmac.new(str(app_secret), unicode(access_token), hashlib.sha256)
    else:
        hmac_object = hmac.new(bytearray(app_secret, 'UTF-8'), str(access_token).encode('UTF-8'), hashlib.sha256)
    generated_hash = hmac_object.hexdigest()
    return generated_hash
