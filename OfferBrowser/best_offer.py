from Databases import mysql_connection as db
from schemas import query_scheme
from datetime import timedelta

def best_offer(user_obj=None, count=1, return_amount=False):

    try:
        queries = db.get_all_queries(facebook_id=user_obj.facebook_id)
    except AttributeError:
        print('SUCH A USER HAS NOT BEEN FOUND')

    print(queries)

    query = 'select * from offers where True'

    for field in queries:
        comparator = query_scheme[field[0]]['comparator']
        if 'int' in query_scheme[field[0]]['db'].lower():
            query = query + f' and {field[0]} {comparator} {field[1]}'
        elif 'char' in query_scheme[field[0]]['db'].lower():
            query = query + f" and {field[0]} {comparator} '{field[1]}'"
        elif 'bool' in query_scheme[field[0]]['db'].lower():
            query = query + f' and {field[0]} {comparator} {field[1]}'
        elif 'date' in query_scheme[field[0]]['db'].lower():
            query = query + f' and {field[0]} {comparator} "{field[1] + timedelta(days=5)}"'
        else:
            print('TODO')
            print(query_scheme[field[0]]['db'])


    print(query)

    offers = db.get_custom(query)
    if return_amount is False:
        return offers[0:count]
    elif return_amount is True:
        return len(offers)
