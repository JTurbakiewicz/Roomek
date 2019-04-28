from Databases import mysql_connection as db
import rater as r
import logging
logging.basicConfig(level='INFO')

fields_to_ignore = ['offer_url', 'creation_time', 'modification_time', 'city', 'offer_type']
offer_records = db.get_custom('SELECT * from offers;')
offer_features_records = db.get_custom('SELECT * from offer_features;')

for offer_record, features_record in zip(offer_records, offer_features_records):
    for column_name, value in {**offer_record, **features_record}.items():
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
            db.create_record(table_name = 'ratings', field_name = column_name, field_value = rating, offer_url = offer_record['offer_url'])
            pass
