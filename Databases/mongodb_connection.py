from mongoengine import *
import datetime
from code import tokens
import logging
import os
log = logging.getLogger(os.path.basename(__file__))

def setup_database_connection():
    """The function sets up the MongoDB database connection. Due to the public Github page, at the moment the
    connection information is read from the file, not included in the repository"""
    # sets up the connection: http: // docs.mongoengine.org / guide / connecting.html
    connect(tokens.db_database_name, host=('mongodb://' + tokens.db_username + ':' + tokens.db_password +
                                     tokens.db_address + '/' + tokens.db_database_name))

    #connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True, connect=False, maxPoolsize=1
    log.info('[LOG-DB] Established connection to the database.')


class Conversation(EmbeddedDocument):
    """Template for what a conversation looks like in the database.
    Its going to be a list of lists of spoken lines, containing also some additional data
    The conversations list is always embedded in the Player document"""
    bot_said = StringField()  # what message has been sent by the bot
    user_said = StringField()  # what message has been sent by the user
    message_timestamp = DateTimeField(required=False)  # when a specific date was recorded
    message_intent = StringField()  # feelings and what not


class Player(Document):
    """Template for what a player document looks like in the database.
    Conversations are embedded to it"""
    facebook_id = StringField(primary_key=True, required=True)  # UNIQUE INDEX OF THE DB
    first_name = StringField()
    last_name = StringField()
    gender = StringField(choices=('Female', 'Male'))
    times_played = IntField(default=0)
    times_won = IntField(default=0)
    conversations = ListField(EmbeddedDocumentField(Conversation))  # a list of embeded conversations
    date_of_joining = DateTimeField(required=True, default=datetime.datetime.now)


def create_player(facebook_id, first_name=None, last_name=None, gender=None):
    """A function used to create a player, given a new, unique facebook_id is provided.
    Sidenote: if the provided facebook_id is already present in the DB, the record is going to be updated"""
    player = Player(
        facebook_id=facebook_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender
    )
    player.save()


def update_player(facebook_id, first_name=None, last_name=None, gender=None):
    """A function used to update player data."""
    query = Player.objects(facebook_id=facebook_id)  # finds the specific record via facebook_id
    if first_name is not None:
        query.update_one(set__first_name=first_name)
    if last_name is not None:
        query.update_one(set__last_name=last_name)
    if gender is not None:
        query.update_one(set__gender=gender)

def update_player_results(facebook_id, times_won=None):
    """A function used to update player results."""
    query = Player.objects(facebook_id=facebook_id)  # finds the specific record via facebook_id
    query.update_one(set__times_played=query[0].times_played + 1)
    if times_won == 1:
        query.update_one(set__times_won=query[0].times_won + 1)


def add_conversation(facebook_id, who_said_it, message_content, message_timestamp=None, message_intent=None):
    """A function used to add a conversation to the specific player. """
    if who_said_it == 'Bot':
        conversation = Conversation(
            bot_said=message_content,
            message_timestamp=message_timestamp,
            message_intent=message_intent
        )
    elif who_said_it == 'User':
        conversation = Conversation(
            user_said=message_content,
            message_timestamp=message_timestamp,
            message_intent=message_intent
        )
    else:
        raise Exception("""Function input data does not fit the assumptions. Please specify who_said_it field properly. Options are: 'Bot' or 'User'""")
    query = Player.objects(facebook_id=facebook_id)  # finds the specific record via facebook_id
    query.update_one(push__conversations=conversation)
    # adds the conversation to the player record (to the end of conversations list)


def find_player(facebook_id):
    """A function used to find the specific player and it returns the instance of Player object. """
    query = Player.objects(facebook_id=facebook_id)
    return (query.first())


setup_database_connection()
