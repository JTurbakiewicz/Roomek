import re
import mysql.connector
from mysql.connector import errorcode
import logging
import os
import tokens
log = logging.getLogger(os.path.basename(__file__))


"""Funtion definition"""

class DB_Connection():

    def __init__(self, db_config, DB_NAME):
        self.db_config = db_config
        self.db_name = DB_NAME

    def __enter__(self):
        self.cnx = mysql.connector.connect(**self.db_config)
        self.cursor = self.cnx.cursor(buffered=True, dictionary=True)
        self.cursor.execute("USE {}".format(self.db_name))
        return self.cnx, self.cursor

    def __exit__(self, *args):
        self.cnx.close()

def set_up_db(db_config):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        log.info("Connection succeeded")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            log.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            log.error("Database does not exist")
        else:
            log.error(str(err))
    try:
        cursor.execute("CREATE DATABASE {} "
                       "DEFAULT CHARACTER SET utf8mb4".format(DB_NAME))
        log.info("Database created")
    except mysql.connector.Error as err:
        log.info("Failed creating database: {}".format(err))
    try:
        cursor.execute("USE {}".format(DB_NAME))
        log.info("Database chosen")
    except mysql.connector.Error as err:
        log.error("Failed choosing database: {}".format(err))

    for table_name in db_tables:
        table_description = db_tables[table_name]
        try:
            log.info("Creating table {0}".format(table_name))
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                log.info("Table already exists")
            else:
                log.error(str(err.msg))
        else:
            log.info("OK")
    cnx.close()

def create_offer(item):
    """ Creates an offer DB record.

    A function that reads the offer object received from the Scrapy framework, read all of the object
    data and inputs the data into the MySQL table.

    Args:
        item: A scrapy.item object, that contains all of the scraped data.
    """
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        try:
            if type(item).__name__ == 'OfferItem':
                fields_to_insert_into_offers = str(list(item.keys()))
                fields_to_insert_into_offers = re.sub("""[[']|]""", '', fields_to_insert_into_offers)
                s_to_insert_into_offers = ('%s,' * len(item.keys()))[:-1]
                add_query = ("INSERT INTO offers "
                                "(%s) "
                                "VALUES (%s)" % (fields_to_insert_into_offers,s_to_insert_into_offers))
                values = []
                for val in item.values():
                    values.append(val[0])
                cursor.execute(add_query, values)

            elif type(item).__name__ == 'OfferFeaturesItem':
                fields_to_insert_into_offer_features = str(list(item.keys()))
                fields_to_insert_into_offer_features = re.sub("""[[']|]""", '', fields_to_insert_into_offer_features)
                s_to_insert_into_offer_features = ('%s,' * len(item.keys()))[:-1]
                add_query = ("INSERT INTO offer_features "
                                   "(%s) "
                                   "VALUES (%s)" % (fields_to_insert_into_offer_features, s_to_insert_into_offer_features))
                values = []
                for val in item.values():
                    values.append(val[0])
                cursor.execute(add_query, values)
        except mysql.connector.IntegrityError as err:
                log.error("Error: {}".format(err))
        cnx.commit()

def get_all(table_name = 'offers', fields_to_get = '*'):
    """ Gets all off rows from DB.

    A function that wraps MySQL query into a python function. It lets you to easly return
    all rows of the specified fields from the DB

    Args:
        fields_to_get: A list of strings containing all of fields, that you want to return:
        e.g. fields_to_get = ['offer_url', 'price']

    Returns:
        A list of dictionaries, that cover all of the fields required by the input.
        e.g. input of fields_to_get = ['offer_url', 'price'] would return:
        [{'offer_url': 'abc.html', 'price': 1500}, {'offer_url': 'def.html', 'price': 2000},...]
    """
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_get_str = str(fields_to_get)
        fields_to_get_clean = re.sub("""[[']|]""", '', fields_to_get_str)
        query =  """SELECT %s
                 FROM %s
                 """ % (fields_to_get_clean, table_name)
        cursor.execute(query)
        result = cursor.fetchall()
        return result

def get(fields_to_get = '*', amount_of_items = 5, fields_to_compare = [], value_to_compare_to = [], comparator = []):
    """ Gets rows from DB that meet the specific criteria.

    A function that wraps MySQL query into a python function. It lets you to easly return
    rows of the specified fields from the DB, that meet the specific criteria set up by the user.

    A function call of:

    get(fields_to_get = ['city', 'price'], amount_of_items = 5, fields_to_compare = ['city', 'price'],
        value_to_compare_to = [['lodz', 'poznan'], 1500], comparator = [['=', '='], '<'])

    would generate a MySQL query of:

    SELECT
        city, price
    FROM
        offers
    WHERE
        city = 'lodz' OR city = 'poznan' AND price < 1500

    and would return something similar to:

    [{'city': 'lodz', 'price': 1000}, {'city': 'poznan', 'price': 750},...]

    Args:
        fields_to_get: A list of strings containing all of fields, that you want to return:
        e.g. fields_to_get = ['offer_url', 'price']

        amount_of_items: An integer number that specifies how many items should be returned.

        fields_to_compare: a list of strings that name the fields you want to compare
        e.g. fields_to_compare = ['city', 'price']

        value_to_compare_to: a list of values and/or lists of values that specifies the values you want to compare
        your fields to
        e.g. value_to_compare_to = [['lodz', 'poznan'], 1500] would compare fields_to_compare[0] to either
        'lodz' OR 'poznan' and fields_to_compare[1] to 1500

        comparator: a list of strings and/or lists of strings that specifies the way you want to compare
        e.g. comparator = comparator = [['=', '='], '<'] would compare fields_to_compare[0] to either
        something EQUALTO or something EQUALTO and fields_to_compare[1] to something LESS THAN

    Returns:
        A list of dictionaries, that cover all of the fields required by the input.
    """
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_get_str = str(fields_to_get)
        fields_to_get_clean = re.sub("""[[']|]""", '', fields_to_get_str)
        if type(fields_to_compare) is not list:
            fields_to_compare = [fields_to_compare]
        for value in range(len(value_to_compare_to)):
            if type(value_to_compare_to[value]) is not list:
                value_to_compare_to[value] = [value_to_compare_to[value]]
        for compar in range(len(comparator)):
            if type(comparator[compar]) is not list:
                comparator[compar] = [comparator[compar]]
        if type(comparator) is not list:
            comparator = [comparator]

        comparative_string = ''

        if len(fields_to_compare) != 0:
            comparative_string = ''.join([comparative_string, 'where'])
            for field in range(len(fields_to_compare)):
                for value in range(len(value_to_compare_to[field])):
                    comparative_string = ' '.join([comparative_string, fields_to_compare[field], comparator[field][value]])
                    comparative_string = ''.join([comparative_string,"""'""",str(value_to_compare_to[field][value]),"""'"""])
                    if value != len(value_to_compare_to[field])-1:
                        comparative_string = ' '.join([comparative_string, 'or'])
                if field != len(value_to_compare_to[field]):
                    comparative_string = ' '.join([comparative_string, 'and'])

        query = """SELECT 
                        %s
                    FROM 
                        offers
                    %s
                    """ % (fields_to_get_clean, comparative_string)
        # TODO -> change in a MySQL secure way
        cursor.execute(query)
        return cursor.fetchmany(amount_of_items)

def get_like(like_field, like_phrase, fields_to_get = '*'):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_get_str = str(fields_to_get)
        fields_to_get_clean = re.sub("""[[']|]""", '', fields_to_get_str)
        like_phrase = "'" + like_phrase + "'"
        query = """SELECT 
                            %s
                        FROM 
                            offers
                        WHERE
                            %s
                        LIKE
                            %s
                        """ % (fields_to_get_clean, like_field, like_phrase)
        cursor.execute(query)
        return cursor.fetchall()

def get_custom(sql_query):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query = sql_query
        cursor.execute(query)
        return cursor.fetchall()

def update_field(table_name, field_name, field_value, where_field, where_value, if_null_required = False):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query = """
           UPDATE {}
           SET {}=%s
           WHERE {}=%s
        """.format(table_name, field_name, where_field)
        if if_null_required:
            query = query + 'AND ' + field_name + ' IS NULL'
        cursor.execute(query, (field_value,where_value))
        cnx.commit()

def update_user(facebook_id, field_to_update, field_value, if_null_required = False):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query = """
           UPDATE users
           SET {}=%s
           WHERE facebook_id=%s
        """.format(field_to_update)
        if if_null_required:
            query = query + 'AND ' + field_to_update + ' IS NULL'
        cursor.execute(query, (field_value,facebook_id))
        cnx.commit()

def get_user(facebook_id):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query =  """SELECT *
                 FROM users
                 WHERE facebook_id = %s
                 """ % (facebook_id)
        cursor.execute(query)
        return cursor.fetchone()

def create_user(facebook_id):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        add_query = ("INSERT INTO users "
                    "(facebook_id) "
                    "VALUES (%s)")
        cursor.execute(add_query, (facebook_id,))
        cnx.commit()

def create_conversation(facebook_id, who_said_it, text = None, sticker_id = None, nlp_intent = None, nlp_entity = None, nlp_value = None, message_time = None):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_add = 'facebook_id, who_said_it'
        conversation_data = [facebook_id, who_said_it]
        if text:
            fields_to_add = fields_to_add + ',text'
            conversation_data.append(text)
        if sticker_id:
            fields_to_add = fields_to_add + ',sticker_id'
            conversation_data.append(sticker_id)
        if nlp_intent:
            fields_to_add = fields_to_add + ',nlp_intent'
            conversation_data.append(nlp_intent)
        if nlp_entity:
            fields_to_add = fields_to_add + ',nlp_entity'
            conversation_data.append(nlp_entity)
        if nlp_value:
            fields_to_add = fields_to_add + ',nlp_value'
            conversation_data.append(nlp_value)
        if nlp_entity:
            fields_to_add = fields_to_add + ',nlp_entity'
            conversation_data.append(nlp_entity)
        if message_time:
            fields_to_add = fields_to_add + ',message_time'
            conversation_data.append(message_time)
        placeholders = '%s,' * len(fields_to_add.split(','))
        placeholders = placeholders[:-1]

        query = """INSERT INTO conversations
                ({})
                VALUES ({})""".format(fields_to_add,placeholders)
        cursor.execute(query, conversation_data)
        cnx.commit()

"""DATA"""

DB_NAME = 'offers'
db_tables = {}
db_tables['offers'] = (
    "CREATE TABLE `offers` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `city` varchar(50) NOT NULL,"
    "  `offer_type` varchar(50) NOT NULL,"
    "  `offer_name` varchar(200),"
    "  `offer_thumbnail_url` varchar(400),"    
    "  `price` int(1),"
    "  `street` varchar(50),"
    "  `district` varchar(50),"
    "  `date_of_the_offer` DATETIME ,"
    "  `offer_id` int(1),"
    "  `offer_text` LONGTEXT,"
    "  `offer_from` varchar(25),"
    "  `apartment_level` smallint(1),"
    "  `furniture` varchar(25),"
    "  `type_of_building` varchar(25),"
    "  `area` smallint(1),"
    "  `amount_of_rooms` int(1),"
    "  `additional_rent` int(1),"
    "  `price_per_m2` int(1),"
    "  `type_of_market` varchar(25),"
    "  `security_deposit` SMALLINT	(1),"
    "  `building_material` varchar(25),"
    "  `windows` varchar(25),"
    "  `heating` varchar(50),"
    "  `building_year` SMALLINT	(1),"
    "  `fit_out` varchar(50),"
    "  `ready_from` DATETIME,"
    "  `type_of_ownership` varchar(50),"
    "  `rental_for_students` varchar(25),"
    "  `location_latitude` FLOAT,"
    "  `location_longitude` FLOAT,"
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`offer_url`)"
    ") ENGINE=InnoDB")

db_tables['offer_features'] = (
    "CREATE TABLE `offer_features` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `internet` BOOLEAN,"
    "  `cable_tv` BOOLEAN,"
    "  `closed_terrain` BOOLEAN,"
    "  `monitoring_or_security` BOOLEAN,"
    "  `entry_phone` BOOLEAN,"
    "  `antibulglar_doors_windows` BOOLEAN,"
    "  `alarm_system` BOOLEAN,"
    "  `antibulglar_blinds` BOOLEAN,"
    "  `dishwasher` BOOLEAN,"
    "  `cooker` BOOLEAN,"
    "  `fridge` BOOLEAN,"
    "  `oven` BOOLEAN,"
    "  `washing_machine` BOOLEAN,"
    "  `tv` BOOLEAN,"
    "  `elevator` BOOLEAN,"
    "  `phone` BOOLEAN,"
    "  `AC` BOOLEAN,"
    "  `garden` BOOLEAN,"
    "  `utility_room` BOOLEAN,"
    "  `parking_space` BOOLEAN,"
    "  `terrace` BOOLEAN,"
    "  `balcony` BOOLEAN,"
    "  `non_smokers_only` BOOLEAN,"
    "  `separate_kitchen` BOOLEAN,"
    "  `basement` BOOLEAN,"
    "  `virtual_walk` BOOLEAN,"
    "  `two_level_apartment` BOOLEAN,"
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`offer_url`)"
    ") ENGINE=InnoDB")

db_tables['user'] = (
    "CREATE TABLE `users` ("
    "  `facebook_id` char(100) NOT NULL,"
    "  `first_name` varchar(100),"
    "  `last_name` varchar(100),"
    "  `gender` enum('Female','Male'),"
    "  `business_type` varchar(100),"
    "  `price_limit` int(1),"
    "  `location_latitude` FLOAT,"
    "  `location_longitude` FLOAT,"
    "  `city` varchar(100),"  
    "  `country` varchar(100),"  
    "  `housing_type` varchar(100),"
    "  `features` varchar(1000),"
    "  `confirmed_data` BOOLEAN,"
    "  `add_more` BOOLEAN,"
    "  `shown_input` BOOLEAN,"
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`facebook_id`)"
    ") ENGINE=InnoDB")

db_tables['conversations'] = (
    "CREATE TABLE `conversations` ("
    "  `conversation_no` int(1) NOT NULL AUTO_INCREMENT,"
    "  `facebook_id` char(100) NOT NULL,"
    "  `who_said_it` BOOLEAN,"
    "  `text` varchar(999),"
    "  `sticker_id` varchar(999),"
    "  `nlp_intent` varchar(999),"
    "  `nlp_entity` varchar(999),"
    "  `nlp_value` varchar(999),"
    "  `message_time` date,"
    "  PRIMARY KEY (`facebook_id`,`conversation_no`), KEY `conversation_no` (`conversation_no`),"
    "  CONSTRAINT `conversation_ibfk_1` FOREIGN KEY (`facebook_id`) "
    "     REFERENCES `users` (`facebook_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

"""SETUP"""

local_config =  tokens.local_config

if local_config:
    db_config = tokens.local_config
else:
    db_config = tokens.pythonanywhere_config


set_up_db(local_config)
