import requests
import os
import json
import logging

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
WIT_API_VERSION = os.getenv('WIT_API_VERSION', '20160516')
access_token = 'KSDIFR7JNR5BA2YVBX7QHO4IDIKIJS3Y'  #TESTING APP TOKEN -> TO CHANGE

logging.basicConfig(level='DEBUG')

def response_status(rsp):
    if rsp.status_code == 409:
        logging.debug('Entity already exists')
    elif rsp.status_code > 200:
        logging.debug('Wit responded with status: ' + str(rsp.status_code) +
                       ' (' + rsp.reason + ')')
    else:
        logging.debug(rsp.content)
        return rsp

def send_message(message, context = None, msg_id = None, thread_id = None, n = None, verbose = None):
    meth = 'GET'
    path = '/message'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }
    params = {}
    params['q'] =  message
    if context:
        params['context'] = context
    if msg_id:
        params['msg_id'] = msg_id
    if thread_id:
        params['thread_id'] = thread_id
    if n:
        params['n'] = n
    if verbose:
        params['verbose'] = verbose

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(params))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        params = params
    )

    return response_status(rsp)

def get_available_entities():
    meth = 'GET'
    path = '/entities'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
    )

    return response_status(rsp)

def create_new_entity(entity_name, entity_description = None):
    meth = 'POST'
    path = '/entities'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
        'Content-Type': 'application/json',
    }
    data = {}
    data["id"] = entity_name
    if entity_description:
        data["doc"] = entity_description

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data = json.dumps(data)
    )

    return response_status(rsp)

def retrive_entity_values(entity_name):
    meth = 'GET'
    path = '/entities/' + entity_name
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
    )

    return response_status(rsp)

##TODO Update the information of an entity

def delete_entity(entity_name):
    meth = 'DELETE'
    path = '/entities/' + entity_name
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
    )

    return response_status(rsp)

def train(entity_name, entity_value, text):
    meth = 'POST'
    path = '/samples'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
        'Content-Type': 'application/json',
    }
    entity = {
        "entity": entity_name,
        "value": entity_value,
        "start": 14,
        "end": 17
    }
    data = {
        "text": text,
        "entities": [entity]
    }
    json_list = []
    json_list.append(data)

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data = json.dumps(json_list)
    )

    return response_status(rsp)

