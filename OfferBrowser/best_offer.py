from Databases import mysql_connection as sql

def best_offer(user_obj = None, count = 1, return_amount = False):

    query = 'select * from offers where True'

    if user_obj.city:
        if type(user_obj.city) is list:
            query = query + ' and ( '
            for preference in user_obj.city:
                query = query + f"city = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and city = '{user_obj.city}'"

    if user_obj.housing_type:
        if type(user_obj.housing_type) is list:
            query = query + ' and ( '
            for preference in user_obj.housing_type:
                query = query + f"housing_type = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and housing_type = '{user_obj.housing_type}'"

    if user_obj.business_type:
        if type(user_obj.business_type) is list:
            query = query + ' and ( '
            for preference in user_obj.business_type:
                query = query + f"business_type = '{preference}' or "
            query = query[:-4] + ' )'
        else:
            query = query + f" and business_type = '{user_obj.business_type}'"

    if user_obj.price_limit:
        if type(user_obj.price_limit) is list:
            query = query + ' and ( '
            for preference in user_obj.price_limit:
                query = query + f'price <= {preference} or '
            query = query[:-4] + ' )'
        else:
            query = query + f' and price <= {user_obj.price_limit}'

    # if user_obj.district:
    #     if type(user_obj.district) is list:
    #         query = query + ' and ( '
    #         for preference in user_obj.district:
    #             query = query + f"district = '{preference}' or "
    #         query = query[:-4] + ' )'
    #     else:
    #         query = query + f" and district = '{user_obj.district}'"

    if user_obj.gender:
        query = query + f" and (preferred_locator like '{user_obj.gender[0]}%' or preferred_locator is Null)"

    query = query + f" and scraped_ranking > -50 ORDER BY date_of_the_offer DESC, scraped_ranking DESC, creation_time DESC"

    print(query)
    offers = sql.get_custom(query)

    if return_amount is False:
        return offers[0:count]
    elif return_amount is True:
        return len(offers)

