from Databases import mysql_connection as db
from statistics import mean
import datetime

def if_empty(column_name, value, *args, **kwargs):
    if value == '' or None:
        return 0
    else:
        return 1

def price(column_name, value, *args, **kwargs):
    offer_record = kwargs['offer_record']
    city = offer_record['city']
    district = offer_record['district']
    offer_type = offer_record['offer_type']
    offer_purpose = offer_record['offer_purpose']

    if district is None:
        prices_dict = db.get_custom(f"select price from offers where city = '{city}' and offer_type = '{offer_type}' and offer_purpose = '{offer_purpose}';")
    else:
        prices_dict = db.get_custom(f"select price from offers where city = '{city}' and district = '{district}' and offer_type = '{offer_type}' and offer_purpose = '{offer_purpose}';")

    prices = [dictionary['price'] for dictionary in prices_dict]
    mean_of_prices = mean(prices)

    if value < 0.5 * mean_of_prices:
        return 1
    elif value < 0.75 * mean_of_prices:
        return 0.75
    elif value < 1 * mean_of_prices:
        return 0.5
    elif value < 1.5 * mean_of_prices:
        return 0.25
    else:
        return 0

def date_of_the_offer(column_name, value, *args, **kwargs):
    current_time = datetime.datetime.now()
    offer_age = current_time-value
    if offer_age < datetime.timedelta(hours=1):
        return 1
    elif offer_age < datetime.timedelta(hours=4):
        return 0.75
    elif offer_age < datetime.timedelta(days=1):
        return 0.5
    elif offer_age < datetime.timedelta(days=3):
        return 0.25
    else:
        return 0

functions_to_apply = {
    # 'offer_name': [if_empty],
    # 'offer_thumbnail_url': [if_empty],
    # 'price': [price],
    # 'street': [if_empty],
    # 'district': [if_empty],
    'date_of_the_offer': [date_of_the_offer],
}

