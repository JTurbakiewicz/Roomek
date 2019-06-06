import Databases.mysql_connection as sql
# from Bot.user import User


def best_offer(user_obj = None, count = 1):

    query = 'select * from offers where True'

    if user_obj.price_limit:
        if type(user_obj.price_limit) is list:
            query = query + ' and ( '
            for preference in user_obj.price_limit:
                query = query + f'price <= {preference} or '
            query = query[:-4] + ' )'
        else:
            query = query + f' and price <= {user_obj.price_limit}'

    if user_obj.city:
        if type(user_obj.city) is list:
            query = query + ' and ( '
            for preference in user_obj.city:
                query = query + f"city = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and city = '{user_obj.city}'"

    if user_obj.business_type:
        if type(user_obj.business_type) is list:
            query = query + ' and ( '
            for preference in user_obj.business_type:
                query = query + f"business_type = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and business_type = '{user_obj.business_type}'"

    if user_obj.housing_type:
        if type(user_obj.housing_type) is list:
            query = query + ' and ( '
            for preference in user_obj.housing_type:
                query = query + f"housing_type = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and housing_type = '{user_obj.housing_type}'"

    if user_obj.gender:
        query = query + f" and (preferred_locator like '{user_obj.gender[0]}%' or preferred_locator is Null)"

    offers = sql.get_custom(query)

    relatable_urls = [x['offer_url'] for x in offers]

    return relatable_urls

# uzy = User('1')
# uzy.price_limit = [5100]
# uzy.city = ['warszawa', 'poznan']
#
# a = best_offer(user_obj=uzy)
# print(a)
# a = best_offer(user_obj=uzy)
#
# # if user_obj.location_latitude:
# #
# # if location_longitude or user_obj.location_longitude:
# #
#
# #
# # if features or user_obj.features:
# #
