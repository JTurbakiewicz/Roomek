import mysql.connector
from mysql.connector import errorcode
from Responder_app import local_tokens, database, witai
if local_tokens: from code import tokens_local as tokens
else: from code import tokens
import logging
import os
log = logging.getLogger(os.path.basename(__file__))


"""Funtion definition"""

class DB_Connection():

    def __init__(self, db_config, DB_NAME):
        self.db_config = db_config
        self.db_name = DB_NAME

    def __enter__(self):
        self.cnx = mysql.connector.connect(**self.db_config)
        self.cursor = self.cnx.cursor()
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

def create_player(facebook_id, first_name=None, last_name=None, gender=None):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        try:
            add_player = ("INSERT INTO players "
                            "(facebook_id, first_name, last_name, gender, times_played, times_won, times_drew, times_lost) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
            times_played = 0
            times_won = 0
            times_drew = 0
            times_lost = 0
            data_player = (facebook_id, first_name, last_name, gender,times_played, times_won, times_drew, times_lost)
            cursor.execute(add_player, data_player)
            cnx.commit()
            log.info('Added user {} using the following data: {}, {}, {}, {}, {}, {}, {}'.format(*data_player))
        except mysql.connector.IntegrityError as err:
            log.error(str(err))

def add_conversation(facebook_id, who_said_it, message_content, message_timestamp=None, message_intent=None):
    """A function used to add a conversation to the specific player. """
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        try:
            add_conversation = ("INSERT INTO conversations "
                              "(facebook_id, message_content, who_said_it, message_timestamp, message_intent) "
                              "VALUES (%s, %s, %s, %s, %s)")
            data_conversation = (facebook_id, message_content, who_said_it, message_timestamp, message_intent)
            cursor.execute(add_conversation, data_conversation)
            cnx.commit()
            log.info('[LOG-DBSQL-INFO] Added conversation using the following data: {}, {}, {}, {}, {}'.format(*data_conversation))
        except:  #TODO -> FIX THIS EMOJI PROBLEM
            try:
                add_conversation = ("INSERT INTO conversations "
                                  "(facebook_id, message_content, who_said_it, message_timestamp, message_intent) "
                                  "VALUES (%s, %s, %s, %s, %s)")
                data_conversation = (facebook_id, 'unhandled emoji', who_said_it, message_timestamp, message_intent)
                cursor.execute(add_conversation, data_conversation)
                cnx.commit()
                log.info('[LOG-DBSQL-INFO] Added conversation emoji using the following data: {}, {}, {}, {}, {}'.format(*data_conversation))
            except:
                raise Exception("""[LOG-DB] Function input data does not fit the assumptions. Please specify who_said_it field properly. Options are: 'Bot' or 'User'""")

def update_player_results(facebook_id, times_won=None):
    """A function used to update player results."""
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        if times_won == 1:  # winner player -> 1
            cursor.execute("""
               UPDATE players
               SET times_played=times_played+1, times_won=times_won+1
               WHERE facebook_id=%s
            """, (facebook_id,))
        elif times_won == 0: # winner bot -> 0
            cursor.execute("""
               UPDATE players
               SET times_played=times_played+1, times_lost=times_lost+1
               WHERE facebook_id=%s
            """, (facebook_id,))
        elif times_won == -1:  # draw -> -1
            cursor.execute("""
                   UPDATE players
                   SET times_played=times_played+1, times_drew=times_drew+1
                   WHERE facebook_id=%s
                """, (facebook_id,))
        cnx.commit()

def update_player(facebook_id, first_name=None, last_name=None, gender=None):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        """A function used to update player data."""
        if first_name is not None:
            cursor.execute("""
               UPDATE players
               SET first_name=%s
               WHERE facebook_id=%s
            """, (first_name,facebook_id))
        elif last_name is not None:
            cursor.execute("""
               UPDATE players
               SET last_name=%s
               WHERE facebook_id=%s
            """, (last_name,facebook_id))
        elif gender is not None:
            cursor.execute("""
               UPDATE players
               SET gender=%s
               WHERE facebook_id=%s
            """, (gender,facebook_id))
        cnx.commit()

def query(facebook_id, fields_to_query):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        str_facebook_id = "'" + facebook_id + "'"
        str_fields_to_query = ','.join(fields_to_query)
        query =  """SELECT %s
                 FROM players
                 WHERE facebook_id = %s""" % (str_fields_to_query, str_facebook_id)
        cursor.execute(query)
        result = cursor.fetchone()
        return result

def get_all(fields_to_get):
    with DB_Connection(db_config, DB_NAME) as (cnx, cursor):
        query =  """SELECT %s
                 FROM players
                 """ % (fields_to_get)
        cursor.execute(query)
        result = cursor.fetchall()
        return [item[0] for item in result]

"""DATA"""

DB_NAME = 'RockPaperScissor$Players'
db_tables = {}
db_tables['players'] = (
    "CREATE TABLE `players` ("
    "  `facebook_id` char(25) NOT NULL,"
    "  `first_name` varchar(25),"
    "  `last_name` varchar(25),"
    "  `gender` enum('Female','Male'),"
    "  `times_played` smallint(1) NOT NULL,"
    "  `times_won` smallint(1) NOT NULL,"
    "  `times_drew` smallint(1) NOT NULL,"
    "  `times_lost` smallint(1) NOT NULL,"
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`facebook_id`)"
    ") ENGINE=InnoDB")

db_tables['conversations'] = (
    "CREATE TABLE `conversations` ("
    "  `conversation_no` int(1) NOT NULL AUTO_INCREMENT,"
    "  `facebook_id` char(25) NOT NULL,"
    "  `message_content` varchar(999),"
    "  `who_said_it` enum('Bot','User'),"
    "  `message_timestamp` date,"
    "  `message_intent` varchar(255),"
    "  PRIMARY KEY (`facebook_id`,`conversation_no`), KEY `conversation_no` (`conversation_no`),"
    "  CONSTRAINT `conversation_ibfk_1` FOREIGN KEY (`facebook_id`) "
    "     REFERENCES `players` (`facebook_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

local_config =  tokens.local_config


if local_config:
    db_config = tokens.local_config
else:
    db_config = tokens.pythonanywhere_config

"""SETUP"""
set_up_db(db_config)