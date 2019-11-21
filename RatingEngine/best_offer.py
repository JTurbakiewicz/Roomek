from Databases import mysql_connection as db
from schemas import query_scheme
from datetime import timedelta


def best_offer(user_obj=None, count=1):
    try:
        queries = db.get_all_queries(facebook_id=user_obj.facebook_id)
    except AttributeError:
        print('SUCH A USER HAS NOT BEEN FOUND')

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
            query = query + f' and ({field[0]} {comparator} "{field[1] + timedelta(days=5)}" or {field[0]} is null)'
        else:
            print('TODO')
            print(query_scheme[field[0]]['db'])

        if field[0] == 'city':
            city = field[1]

    print(query)

    offers = db.get_custom(query)

    offers_count_city = db.get_custom(f"SELECT COUNT(IF(city = '{city}', 1, NULL)) '{city}' FROM offers;")
    offers_count_city = offers_count_city[0][city]

    return {'offers': offers[0:count], 'offers_count': len(offers), 'offers_count_city': offers_count_city}
