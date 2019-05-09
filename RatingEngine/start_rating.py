from Databases import mysql_connection as db
import rater as r
import logging
from Key import rating_weights

logging.basicConfig(level='DEBUG')

fields_to_ignore = ['creation_time', 'modification_time', 'city', 'offer_type']
offer_records = db.get_custom('select offers.*, offer_features.* from offers inner join offer_features on offers.offer_url=offer_features.offer_url;')

for offer_record in offer_records:
    offer_rating = {}
    offer_rating['offer_url'] = offer_record['offer_url']
    for column_name, value in offer_record.items():
        rating = None
        try:
            function_result = None
            for func in r.functions_to_apply[column_name]:
                if function_result:
                    logging.debug('Applying funtion ' + func.__name__ + ' on the field name ' + str(column_name) +
                                  ' with the value of ' + str(function_result))
                else:
                    logging.debug('Applying funtion ' + func.__name__ + ' on the field name ' + str(column_name) +
                                  ' with the value of ' + str(value))
                function_result = func(column_name, value, function_result, offer_record = offer_record)
            rating = function_result
        except KeyError:
            logging.debug('Functions to apply for the column: ' + column_name + ' not specified')

        if rating is not None and column_name not in fields_to_ignore:
            offer_rating[column_name] = rating
    static_rating = 0
    for rating_name, rating_value in offer_rating.items():
        try:
            static_rating = static_rating + rating_value * rating_weights[rating_name]
        except KeyError:
            pass
    offer_rating['static_rating'] = static_rating
    db.create_rating(offer_rating)
