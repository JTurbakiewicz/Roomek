import re
import mysql.connector
from mysql.connector import errorcode
import logging
import os
import tokens
import sys
from Bot.user import User
from Bot.message import Message

# logging.basicConfig(level='DEBUG')
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
        cursor.execute(query, (field_value, facebook_id))
        cnx.commit()


def user_exists(facebook_id):

    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query =  """SELECT *
                 FROM users
                 WHERE facebook_id = %s
                 """ % ("'"+facebook_id+"'") #TODO change

        cursor.execute(query)
        data = cursor.fetchone()

        if data:
            return True
        else:
            return False


def get_user(facebook_id):

    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query =  """SELECT *
                 FROM users
                 WHERE facebook_id = %s
                 """ % ("'"+facebook_id+"'") #TODO change

        cursor.execute(query)
        data = cursor.fetchone()

        if data:
            if len(data) != 0:
                created_user = User(data['facebook_id'])

                created_user.first_name = data['first_name']
                created_user.last_name = data['last_name']
                created_user.gender = data['gender']
                created_user.language = data['language']
                created_user.business_type = data['business_type']
                created_user.housing_type = data['housing_type']
                created_user.price_limit = data['price_limit']
                created_user.features = data['features']

                created_user.country = data['country']
                created_user.city = data['city']
                created_user.street = data['street']
                created_user.latitude = data['latitude']
                created_user.longitude = data['longitude']

                created_user.context = data['context']
                created_user.interactions = data['interactions']
                created_user.shown_input = data['shown_input']
                created_user.wants_more_features = data['wants_more_features']
                created_user.wants_more_locations = data['wants_more_locations']
                created_user.confirmed_data = data['confirmed_data']
                created_user.add_more = data['add_more']

                return created_user
            else:
                return False
        else:
            return False


def push_user(user_obj = None, update = False):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_add = 'facebook_id'
        user_data = [user_obj.facebook_id]

        if user_obj.first_name:
            user_data.append(user_obj.first_name)
            fields_to_add = fields_to_add + ',first_name'

        if user_obj.last_name:
            user_data.append(user_obj.last_name)
            fields_to_add = fields_to_add + ',last_name'

        if user_obj.gender:
            user_data.append(user_obj.gender)
            fields_to_add = fields_to_add + ',gender'

        if user_obj.business_type:
            user_data.append(user_obj.business_type)
            fields_to_add = fields_to_add + ',business_type'

        if user_obj.price_limit:
            user_data.append(user_obj.price_limit)
            fields_to_add = fields_to_add + ',price_limit'

        if user_obj.latitude:
            user_data.append(user_obj.latitude)
            fields_to_add = fields_to_add + ',location_latitude'

        if user_obj.longitude:
            user_data.append(user_obj.longitude)
            fields_to_add = fields_to_add + ',location_longitude'

        if user_obj.city:
            user_data.append(user_obj.city)
            fields_to_add = fields_to_add + ',city'

        if user_obj.country:
            user_data.append(user_obj.country)
            fields_to_add = fields_to_add + ',country'

        if user_obj.housing_type:
            user_data.append(user_obj.housing_type)
            fields_to_add = fields_to_add + ',housing_type'

        if user_obj.features:
            if isinstance(user_obj.features, list):
                user_data.append(",".join(user_obj.features))
            else:
                user_data.append(user_obj.features)
            fields_to_add = fields_to_add + ',features'

        if user_obj.confirmed_data:
            user_data.append(user_obj.confirmed_data)
            fields_to_add = fields_to_add + ',confirmed_data'

        if user_obj.add_more:
            user_data.append(user_obj.add_more)
            fields_to_add = fields_to_add + ',add_more'

        if user_obj.shown_input:
            user_data.append(user_obj.shown_input)
            fields_to_add = fields_to_add + ',shown_input'

        if user_obj.wants_more_features:
            user_data.append(user_obj.wants_more_features)
            fields_to_add = fields_to_add + ',wants_more_features'

        if user_obj.wants_more_locations:
            user_data.append(user_obj.wants_more_locations)
            fields_to_add = fields_to_add + ',wants_more_locations'

        if user_obj.interactions:
            user_data.append(user_obj.interactions)
            fields_to_add = fields_to_add + ',interactions'

        if user_obj.language:
            user_data.append(user_obj.language)
            fields_to_add = fields_to_add + ',language'

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

def create_message(msg_obj = None, update = False):

    if msg_obj is None:
        msg_obj = Message('default')

    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        fields_to_add = 'messaging'
        msg_data = [str(msg_obj.messaging)]

        if msg_obj.is_echo:
            msg_data.append(msg_obj.is_echo)
            fields_to_add = fields_to_add + ',is_echo'
        if msg_obj.time:
            msg_data.append(msg_obj.time)
            fields_to_add = fields_to_add + ',time'
        if msg_obj.timestamp:
            msg_data.append(msg_obj.timestamp)
            fields_to_add = fields_to_add + ',timestamp'
        if msg_obj.facebook_id:
            msg_data.append(str(msg_obj.facebook_id))
            fields_to_add = fields_to_add + ',facebook_id'
        if msg_obj.type:
            msg_data.append(str(msg_obj.type))
            fields_to_add = fields_to_add + ',type'
        if msg_obj.mid:
            msg_data.append(msg_obj.mid)
            fields_to_add = fields_to_add + ',mid'
        if msg_obj.NLP:
            msg_data.append(msg_obj.NLP)
            fields_to_add = fields_to_add + ',NLP'
        if msg_obj.stickerID:
            msg_data.append(str(msg_obj.stickerID))
            fields_to_add = fields_to_add + ',stickerID'
        if msg_obj.sticker_name:
            msg_data.append(str(msg_obj.sticker_name))
            fields_to_add = fields_to_add + ',sticker_name'
        if msg_obj.latitude:
            msg_data.append(msg_obj.latitude)
            fields_to_add = fields_to_add + ',latitude'
        if msg_obj.longitude:
            msg_data.append(msg_obj.longitude)
            fields_to_add = fields_to_add + ',longitude'
        if msg_obj.url:
            msg_data.append(str(msg_obj.url))
            fields_to_add = fields_to_add + ',url'
        if msg_obj.text:
            msg_data.append(str(msg_obj.text))
            fields_to_add = fields_to_add + ',text'
        if msg_obj.NLP_entities:
            msg_data.append(str(msg_obj.NLP_entities))
            fields_to_add = fields_to_add + ',NLP_entities'
        if msg_obj.NLP_language:
            msg_data.append(str(msg_obj.NLP_language))
            fields_to_add = fields_to_add + ',NLP_language'
        if msg_obj.NLP_intent:
            msg_data.append(str(msg_obj.NLP_intent))
            fields_to_add = fields_to_add + ',NLP_intent'

        placeholders = '%s,' * len(fields_to_add.split(','))
        placeholders = placeholders[:-1]

        if update:
            duplicate_condition = ''
            for field in fields_to_add.split(','):
                duplicate_condition = duplicate_condition + field + '=%s,'
            duplicate_condition = duplicate_condition[:-1]

            query = f"""
                        INSERT INTO conversations
                        ({fields_to_add})
                        VALUES ({placeholders})
                        ON DUPLICATE KEY UPDATE {duplicate_condition}
                     """
            cursor.execute(query, msg_data*2)
        else:

            query = """INSERT INTO conversations
                    ({})
                    VALUES ({})""".format(fields_to_add, placeholders)

            cursor.execute(query, msg_data)
        cnx.commit()


def get_messages(facebook_id):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query =  """SELECT *
                 FROM conversations
                 WHERE facebook_id = %s
                 """ % (facebook_id)
        cursor.execute(query)
        data = cursor.fetchall()

        fake_json = {'entry': [{
            'id': '1368143226655403',
            'messaging': [{
                'message': {
                    'mid': 'GZ1aEkkMhti8WBa22tk5lXWJoZXN9QKZWH8NjK5DYEFKf7dFmM-QZEUThzNoJk73q2QSR5AD_aEDnRjNS6XHbw',
                    'nlp': {
                        'entities': {
                            'bye': [{
                                '_entity': 'bye',
                                'confidence': 0.29891659254789,
                                'value': 'true'}],
                            'thanks': [{
                                '_entity': 'thanks',
                                'confidence': 0.056984366913182,
                                'value': 'true'}]}},
                    'seq': 671186,
                    'text': 'hello'},
                'recipient': {'id': '1368143226655403'},
                'sender': {'id': '2231584683532589'},
                'timestamp': 1550245454526}],
            'time': 1550245455532}],
            'object': 'page'}   #TODO -> delete json in msg init

        created_messages = []

        for message in data:
            created_message = Message(fake_json)
            created_message.is_echo = message['is_echo']
            created_message.messaging = message['messaging']
            created_message.time = message['time']
            created_message.timestamp = message['timestamp']
            created_message.user = message['facebook_id']
            created_message.type = message['type']
            created_message.mid = message['mid']
            created_message.NLP = message['NLP']
            created_message.stickerID = message['stickerID']
            created_message.sticker_name = message['sticker_name']
            created_message.latitude = message['latitude']
            created_message.longitude = message['longitude']
            created_message.url = message['url']
            created_message.text = message['text']
            created_message.NLP_entities = message['NLP_entities']
            created_message.NLP_language = message['NLP_language']
            created_message.NLP_intent = message['NLP_intent']


            created_messages.append(created_message)

        return created_messages

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


def drop_user(facebook_id = None):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):

        try:
            query = f"""Delete from users where facebook_id = {facebook_id}"""
            cursor.execute(query)
            cnx.commit()
            logging.info(f"User {facebook_id} has just been removed from the database.")

        except mysql.connector.Error as error:
            logging.warning("Failed to delete record from table: {}".format(error))

        # finally:
        #     if (connection.is_connected()):
        #         cursor.close()
        #         connection.close()
        #         print("MySQL connection is closed")


"""DATA"""

DB_NAME = 'RoomekBot$offers'
db_tables = {}
db_tables['offers'] = (
    "CREATE TABLE `offers` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `city` varchar(50) NOT NULL,"
    "  `housing_type` varchar(50) NOT NULL,"
    "  `business_type` varchar(50)," 
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
    "  `furniture` BOOLEAN,"
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

db_tables['utility'] = (
    "CREATE TABLE `utility` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `offer_name` varchar(200),"
    "  `offer_text` LONGTEXT,"
    "  `street` varchar(50),"
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

db_tables['users'] = (
    "CREATE TABLE `users` ("
    "  `facebook_id` char(100) NOT NULL,"
    "  `first_name` varchar(100),"
    "  `last_name` varchar(100),"
    "  `gender` enum('Female','Male'),"
    "  `language` varchar(100),"
    "  `business_type` varchar(100),"
    "  `housing_type` varchar(100),"
    "  `price_limit` int(1),"
    "  `features` varchar(1000),"
    "  `country` varchar(100),"  
    "  `city` varchar(100),"  
    "  `street` varchar(100),"  
    "  `latitude` FLOAT,"
    "  `longitude` FLOAT,"
    "  `context` varchar(100),"  
    "  `interactions` int(1),"
    "  `shown_input` BOOLEAN,"
    "  `wants_more_features` BOOLEAN,"
    "  `wants_more_locations` BOOLEAN,"
    "  `confirmed_data` BOOLEAN,"
    "  `add_more` BOOLEAN,"
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`facebook_id`)"
    ") ENGINE=InnoDB")

db_tables['conversations'] = (
    "CREATE TABLE `conversations` ("
    "  `conversation_no` int(1) NOT NULL AUTO_INCREMENT,"
    "  `is_echo` BOOLEAN,"
    "  `messaging` varchar(5000),"   
    "  `time` date,"
    "  `timestamp` date," 
    "  `facebook_id` char(100),"
    "  `type` char(100),"
    "  `mid` varchar(1000),"
    "  `NLP` BOOLEAN,"
    "  `stickerID` varchar(999),"
    "  `sticker_name` varchar(999),"
    "  `latitude` FLOAT,"
    "  `longitude` FLOAT,"
    "  `url` BLOB,"
    "  `text` varchar(999),"
    "  `NLP_entities` varchar(999),"
    "  `NLP_language` varchar(999),"
    "  `NLP_intent` varchar(999),"
    "  PRIMARY KEY (`conversation_no`)"
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

