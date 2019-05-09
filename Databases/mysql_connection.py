import re
import mysql.connector
from mysql.connector import errorcode
import logging
import os
import tokens
import sys

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
        logging.info("Connection succeeded")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(str(err))
    try:
        cursor.execute("CREATE DATABASE {} "
                       "DEFAULT CHARACTER SET utf8mb4".format(DB_NAME))
        logging.info("Database created")
    except mysql.connector.Error as err:
        logging.info("Failed creating database: {}".format(err))
    except UnboundLocalError:
        logging.info("No connection estabilished")
        sys.exit()
    try:
        cursor.execute("USE {}".format(DB_NAME))
        logging.info("Database chosen")
    except mysql.connector.Error as err:
        logging.error("Failed choosing database: {}".format(err))

    for table_name in db_tables:
        table_description = db_tables[table_name]
        try:
            logging.info("Creating table {0}".format(table_name))
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logging.info("Table already exists")
            else:
                logging.error(str(err.msg))
        else:
            logging.info("OK")
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
            if type(item).__name__ == 'OfferItem' or type(item).__name__ == 'OfferRoomItem':
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
                logging.error("Error: {}".format(err))
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


def create_user(user_obj = None, facebook_id = None, first_name = None, last_name = None, gender = None, business_type = None,
                price_limit = None, location_latitude = None, location_longitude = None, city = None,
                country = None, housing_type = None, features = None, confirmed_data = None, add_more = None,
                shown_input = None, update = False):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_add = 'facebook_id'
        if facebook_id:
            user_data = [facebook_id]
        else:
            user_data = [user_obj.facebook_id]
        if first_name or user_obj.first_name:
            if first_name:
                user_data.append(first_name)
            else:
                user_data.append(user_obj.first_name)
            fields_to_add = fields_to_add + ',first_name'
        if last_name or user_obj.last_name:
            if last_name:
                user_data.append(last_name)
            else:
                user_data.append(user_obj.last_name)
            fields_to_add = fields_to_add + ',last_name'
        if gender or user_obj.gender:
            if gender:
                user_data.append(gender)
            else:
                user_data.append(user_obj.gender)
            fields_to_add = fields_to_add + ',gender'
        if business_type or user_obj.business_type:
            if business_type:
                user_data.append(business_type)
            else:
                user_data.append(user_obj.business_type)
            fields_to_add = fields_to_add + ',business_type'
        if price_limit or user_obj.price_limit:
            if price_limit:
                user_data.append(price_limit)
            else:
                user_data.append(user_obj.price_limit)
            fields_to_add = fields_to_add + ',price_limit'
        if location_latitude or user_obj.location_latitude:
            if location_latitude:
                user_data.append(location_latitude)
            else:
                user_data.append(user_obj.location_latitude)
            fields_to_add = fields_to_add + ',location_latitude'
        if location_longitude or user_obj.location_longitude:
            if location_longitude:
                user_data.append(location_longitude)
            else:
                user_data.append(user_obj.location_longitude)
            fields_to_add = fields_to_add + ',location_longitude'
        if city or user_obj.city:
            if city:
                user_data.append(city)
            else:
                user_data.append(user_obj.city)
            fields_to_add = fields_to_add + ',city'
        if country or user_obj.country:
            if country:
                user_data.append(country)
            else:
                user_data.append(user_obj.country)
            fields_to_add = fields_to_add + ',country'
        if housing_type or user_obj.housing_type:
            if housing_type:
                user_data.append(housing_type)
            else:
                user_data.append(user_obj.housing_type)
            fields_to_add = fields_to_add + ',housing_type'
        if features or user_obj.features:
            if features:
                user_data.append(features)
            else:
                user_data.append(user_obj.features)
            fields_to_add = fields_to_add + ',features'
        if confirmed_data or user_obj.confirmed_data:
            if confirmed_data:
                user_data.append(confirmed_data)
            else:
                user_data.append(user_obj.confirmed_data)
            fields_to_add = fields_to_add + ',confirmed_data'
        if add_more or user_obj.add_more:
            if add_more:
                user_data.append(add_more)
            else:
                user_data.append(user_obj.add_more)
            fields_to_add = fields_to_add + ',add_more'
        if shown_input or user_obj.shown_input:
            if shown_input:
                user_data.append(shown_input)
            else:
                user_data.append(user_obj.shown_input)
            fields_to_add = fields_to_add + ',shown_input'

        placeholders = '%s,' * len(fields_to_add.split(','))
        placeholders = placeholders[:-1]

        if update:
            duplicate_condition = ''
            for field in fields_to_add.split(','):
                duplicate_condition = duplicate_condition + field + '=%s,'
            duplicate_condition = duplicate_condition[:-1]

            query = f"""
                        INSERT INTO users
                        ({fields_to_add})
                        VALUES ({placeholders})
                        ON DUPLICATE KEY UPDATE {duplicate_condition}
                     """
            cursor.execute(query, user_data*2)
        else:

            query = """INSERT INTO users
                    ({})
                    VALUES ({})""".format(fields_to_add,placeholders)
            cursor.execute(query, user_data)
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


def create_record(table_name, field_name, field_value, offer_url):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query = """
            INSERT INTO {0}
            (offer_url, {1})
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE {1}=%s
         """.format(table_name, field_name)
        # if if_null_required:
        #     query = query + 'AND ' + field_name + ' IS NULL'
        cursor.execute(query, (offer_url, field_value, field_value))
        cnx.commit()

def create_rating(rating):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields = list(rating.keys())
        values = list(rating.values())

        fields_to_insert = ','.join(fields)
        placeholders = ','.join(['%s']*len(values))

        duplicate_condition = ''
        for field in fields:
            duplicate_condition = duplicate_condition + field + '=%s,'
        duplicate_condition = duplicate_condition[:-1]

        query = f"""
                    INSERT INTO ratings
                    ({fields_to_insert})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {duplicate_condition}
                 """
        cursor.execute(query, values*2)
        cnx.commit()

"""DATA"""

DB_NAME = 'offers'
db_tables = {}
db_tables['offers'] = (
    "CREATE TABLE `offers` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `city` varchar(50) NOT NULL,"
    "  `offer_type` varchar(50) NOT NULL,"
    "  `offer_purpose` varchar(50)," 
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
    "  `type_of_room` varchar(50),"
    "  `preferred_locator` varchar(50),"
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

db_tables['ratings'] = (
    "CREATE TABLE `ratings` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `static_rating` float(6,2),"
    "  `offer_name` float(4,3),"
    "  `offer_thumbnail_url` float(4,3),"    
    "  `price` float(4,3),"
    "  `street` float(4,3),"
    "  `district` float(4,3),"
    "  `date_of_the_offer` float(4,3),"
    "  `offer_id` float(4,3),"
    "  `offer_text` float(4,3),"
    "  `offer_from` float(4,3),"
    "  `apartment_level` float(4,3),"
    "  `furniture` float(4,3),"
    "  `type_of_building` float(4,3),"
    "  `area` float(4,3),"
    "  `amount_of_rooms` float(4,3),"
    "  `additional_rent` float(4,3),"
    "  `price_per_m2` float(4,3),"
    "  `type_of_market` float(4,3),"
    "  `security_deposit` float(4,3),"
    "  `building_material` float(4,3),"
    "  `windows` float(4,3),"
    "  `heating` float(4,3),"
    "  `building_year` float(4,3),"
    "  `fit_out` float(4,3),"
    "  `ready_from` float(4,3),"
    "  `type_of_ownership` float(4,3),"
    "  `rental_for_students` float(4,3),"
    "  `location_latitude` float(4,3),"
    "  `location_longitude` float(4,3),"
    "  `type_of_room` float(4,3),"
    "  `preferred_locator` float(4,3),"
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

"""SETUP"""

db_config = tokens.sql_config

set_up_db(db_config)
