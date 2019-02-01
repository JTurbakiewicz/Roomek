import mysql.connector
from mysql.connector import errorcode
# from code import tokens
# from signal import signal, SIGPIPE, SIG_DFL

"""Funtion definition"""

def create_database():
    cursor = cnx.cursor()
    DB_NAME = 'PropertyScraper$Offers'
    try:
        cursor.execute("CREATE DATABASE {} ".format(DB_NAME))
    except mysql.connector.Error as err:
        print("[LOG-DBSQL-ERROR] Failed creating database: {}".format(err))
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("[LOG-DBSQL-INFO] Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database()
            print("[LOG-DBSQL-INFO] Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print('LOG-DBSQL-ERROR ' + str(err))
    try:
        cursor.execute("""
        ALTER DATABASE
            PropertyScraper$Offers
            CHARACTER SET = utf8mb4
            COLLATE = utf8mb4_unicode_ci
        """)
        print ('[LOG-DBSQL-INFO] Changed UTF')
    except:
        print('[LOG-DBSQL-INFO] Failed to changed= UTF')


def connect_to_db(connection_config):
    global cursor
    try:
        cnx = mysql.connector.connect(**connection_config)
        cursor = cnx.cursor()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("[LOG-DBSQL-ERROR] Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("[LOG-DBSQL-ERROR] Database does not exist")
        else:
            print(err)
    else:
        return cnx

def create_tables():
    for table_name in db_tables:
        table_description = db_tables[table_name]
        try:
            print("[LOG-DBSQL-INFO] Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print('[LOG-DBSQL-DEBUG] ' + str(err.msg))
        else:
            print("OK")

def create_offer(item):
    try:
        fields_to_insert = str(list(item.keys()))
        fields_to_insert = fields_to_insert.replace('[',"")
        fields_to_insert = fields_to_insert.replace(']',"")
        fields_to_insert = fields_to_insert.replace("""'""","")
        s_to_insert = ('%s,' * len(item.keys()))[:-1]
        add_player = ("INSERT INTO offers "
                        "(%s) "
                        "VALUES (%s)" % (fields_to_insert,s_to_insert))
        values = []
        for val in item.values():
            values.append(val[0])
        cursor.execute(add_player, values)
        cnx.commit()
        # print ('[LOG-DBSQL-INFO] Added offer using the following data: {}, {}, {}, {}, {}, {}, {},{}, {}, {}, {}, '
        #        '{}, {}, {},{}, {}'.format(*data_player))
    except mysql.connector.IntegrityError as err:
        print("[LOG-DBSQL-ERROR] Error: {}".format(err))


def get_all(fields_to_get):
    query =  """SELECT %s
             FROM offers
             """ % (fields_to_get)
    cursor.execute(query)
    result = cursor.fetchall()
    return [item[0] for item in result]

"""DATA"""

DB_NAME = 'offers'
db_tables = {}
db_tables['offers'] = (
    "CREATE TABLE `offers` ("
    "  `offer_url` varchar(700) NOT NULL,"
    "  `city` varchar(50) NOT NULL,"
    "  `offer_type` varchar(50) NOT NULL,"
    "  `offer_name` varchar(500),"
    "  `price` int(1),"
    "  `offer_location` varchar(50),"
    "  `date_of_the_offer` DATETIME ,"
    "  `offer_id` int(1) NOT NULL,"
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
    "  `creation_time` datetime default current_timestamp,"
    "  `modification_time` datetime on update current_timestamp,"
    "  PRIMARY KEY (`offer_url`)"
    ") ENGINE=InnoDB")


"""SETUP"""

local_config = {
    'user': 'root',
    'password': """frytkiMySQL""",
    'host': 'localhost',
    'raise_on_warnings': True
}

#
# signal(SIGPIPE, SIG_DFL)
cnx = connect_to_db(local_config)
create_database()
create_tables()
