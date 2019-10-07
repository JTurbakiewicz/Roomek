from Databases import mysql_connection as db
from schemas import query_scheme


def best_offer(user_obj=None, count=1, return_amount=False):
    queries = db.get_all_queries(facebook_id=user_obj.facebook_id)
    try:
        queries = db.get_all_queries(facebook_id=user_obj.facebook_id)
        # queries = db.get_all_queries(facebook_id="1")
    except AttributeError:
        print('SUCH A USER HAS NOT BEEN FOUND')

    print(queries)
    query = 'select * from offers where True'

    for field in queries:
        comparator = query_scheme[field[0]]['comparator']
        if 'int' in query_scheme[field[0]]['db'].lower():
            field_type = 'int'
        elif 'char' in query_scheme[field[0]]['db'].lower():
            field_type = 'string'
        elif 'bool' in query_scheme[field[0]]['db'].lower():
            field_type = 'bool'
        elif 'date' in query_scheme[field[0]]['db'].lower():
            field_type = 'datetime'
        else:
            print('TODO')
            print(query_scheme[field[0]]['db'])

        if field_type == 'int':
            query = query + f' and {field[0]} {comparator} {field[1]}'
        elif field_type == 'string':
            query = query + f" and {field[0]} {comparator} '{field[1]}'"
        elif field_type == 'bool':
            query = query + f' and {field[0]} {comparator} {field[1]}'
        elif field_type == 'datetime':
            query = query + f' and {field[0]} {comparator} {field[1]}'

    print(query)
    # if user_obj.city:
    #     if type(user_obj.city) is list:
    #         query = query + ' and ( '
    #         for preference in user_obj.city:
    #             query = query + f"city = '{preference}' or "
    #         query = query[:-4] + ' )'
    #     else:
    #         query = query + f" and city = '{user_obj.city}'"
    #
    # if user_obj.housing_type:
    #     if type(user_obj.housing_type) is list:
    #         query = query + ' and ( '
    #         for preference in user_obj.housing_type:
    #             query = query + f"housing_type = '{preference}' or "
    #         query = query[:-4] + ' )'
    #     else:
    #         query = query + f" and housing_type = '{user_obj.housing_type}'"
    #
    # if user_obj.business_type:
    #     if type(user_obj.business_type) is list:
    #         query = query + ' and ( '
    #         for preference in user_obj.business_type:
    #             query = query + f"business_type = '{preference}' or "
    #         query = query[:-4] + ' )'
    #     else:
    #         query = query + f" and business_type = '{user_obj.business_type}'"
    #
    # if user_obj.price_limit:
    #     if type(user_obj.price_limit) is list:
    #         query = query + ' and ( '
    #         for preference in user_obj.price_limit:
    #             query = query + f'price <= {preference} or '
    #         query = query[:-4] + ' )'
    #     else:
    #         query = query + f' and price <= {user_obj.price_limit}'
    #
    # # if user_obj.district:
    # #     if type(user_obj.district) is list:
    # #         query = query + ' and ( '
    # #         for preference in user_obj.district:
    # #             query = query + f"district = '{preference}' or "
    # #         query = query[:-4] + ' )'
    # #     else:
    # #         query = query + f" and district = '{user_obj.district}'"
    #
    # if user_obj.gender:
    #     query = query + f" and (preferred_locator like '{user_obj.gender[0]}%' or preferred_locator is Null)"
    #
    # query = query + f" and scraped_ranking > -50 ORDER BY date_of_the_offer DESC, scraped_ranking DESC, creation_time DESC"

    offers = db.get_custom(query)
    if return_amount is False:
        return offers[0:count]
    elif return_amount is True:
        return len(offers)
