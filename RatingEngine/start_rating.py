from Databases import mysql_connection as db
import rater as r
import logging
logging.basicConfig(level='DEBUG')

offer_records = db.get_custom('SELECT * from offers;')
offer_features_records = db.get_custom('SELECT * from offer_features;')

for offer_record, features_record in zip(offer_records, offer_features_records):
    for column_name, value in {**offer_record, **features_record}.items():
        rating = None
        try:
            for func in r.functions_to_apply[column_name]:
                rating = func(column_name, value)
        except KeyError:
            logging.debug('Functions to apply for the column: ' + column_name + ' not specified')

        if rating is not None and column_name not in ['offer_url', 'creation_time', 'modification_time']:
            db.create_record(table_name = 'ratings', field_name = column_name, field_value = rating, offer_url = offer_record['offer_url'])

