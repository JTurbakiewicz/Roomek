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

def

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

def update_entity(entity_name, entity_description = None, lookups = None, values = None):
    meth = 'PUT'
    path = '/entities/' + entity_name
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    data = {}
    data["id"] = entity_name
    if entity_description:
        data["doc"] = entity_description
    if lookups:
        data["lookups"] = lookups
    if values:  #You can update values for keyword entities. For traits or free-text entities, use POST /samples
        data["values"] = values

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers) + ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data=json.dumps(data)
    )

    return response_status(rsp)

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

def delete_role(entity_name, role_name):
    meth = 'DELETE'
    path = '/entities/' + entity_name + ':' + role_name
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

def add_entity_value(entity_name, value, expressions = None, metadata = None):
    """This only applies to keyword entities. For trait or free-text entities, use POST /samples"""
    meth = 'POST'
    path = '/entities/' + entity_name + '/values'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    data = {}
    data["value"] = str(value)
    if expressions:
        data["expressions"] = expressions #expression is a keyword synonym
    if metadata:
        data["metadata"] = metadata

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers) + ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data=json.dumps(data)
    )

    return response_status(rsp)

def delete_entity_value(entity_name, value):
    """This only applies to keyword entities. For trait or free-text entities, use POST /samples"""
    meth = 'DELETE'
    path = '/entities/' + entity_name + '/values/' + value
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

def create_expression(entity_name, value, expression = None):
    """This only applies to keyword entities. For trait or free-text entities, use POST /samples
    Expression is a synonym to a keyword"""
    meth = 'POST'
    path = '/entities/' + entity_name + '/values/' + value + '/expressions'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }

    data = {}
    data["expression"] = str(expression)

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers) + ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data=json.dumps(data)
    )

    return response_status(rsp)

def delete_expression(entity_name, value, expression):
    meth = 'DELETE'
    path = '/entities/' + entity_name + '/values/' + value + '/expressions/' + expression
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

def get_samples(limit = 1, offset = None, entity_ids = None, entity_values = None, negative = None):
    meth = 'GET'
    path = '/samples?limit=' + str(limit)

    if offset:
        path = path + '&offset=' + str(offset)
    if entity_ids:
        path = path + '&entity_ids=' + ','.join(entity_ids)
    if entity_values: #works only if entity_ids specified
        path = path + '&entity_values=' + ','.join(entity_values)
    if negative:
        path = path + '&negative=true'
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

def delete_samples(messages):
    meth = 'DELETE'
    path = '/samples'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
    }
    if not isinstance(messages, (list,)):
        messages = [messages]
    messages_array = []
    for message in messages:
        messages_array.append({"text" : message})

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(messages_array))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data = json.dumps(messages_array)
    )

    return response_status(rsp)

def get_all_apps(limit = 1, offset = None):
    meth = 'GET'
    path = '/apps?limit=' + str(limit)
    if offset:
        path = path + '&offset=' + str(offset)
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

def get_app_info(app_id):
    meth = 'GET'
    path = '/apps/' + app_id
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

def create_new_app(app_name, app_lang, app_privacy, app_description = None):
    meth = 'POST'
    path = '/apps'
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
        'Content-Type': 'application/json',
    }
    data = {}
    data["name"] = app_name
    data["lang"] = app_lang
    data["private"] = app_privacy
    if app_description:
        data["desc"] = app_description

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data = json.dumps(data)
    )

    return response_status(rsp)

def update_app(app_id, app_name=None, app_lang=None, app_privacy=None, app_timezone=None, app_description = None):
    meth = 'PUT'
    path = '/apps/' + app_id
    full_url = WIT_API_HOST + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
        'Content-Type': 'application/json',
    }
    data = {}
    if app_name:
        data["name"] = app_name.replace(" ", "")
    if app_lang:
        data["lang"] = app_lang
    if app_privacy:
        data["private"] = app_privacy
    if app_timezone:
        data["timezone"] = app_privacy
    if app_description:
        data["desc"] = app_description

    logging.debug('Request content: ' + ' | ' + meth + ' | ' + full_url + ' | ' + str(headers)+ ' | ' + str(data))

    rsp = requests.request(
        meth,
        full_url,
        headers = headers,
        data = json.dumps(data)
    )

    return response_status(rsp)

def delete_app(app_id):
    meth = 'DELETE'
    path = '/apps/' + app_id
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

def get_app_zip():
    meth = 'GET'
    path = '/export'
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

