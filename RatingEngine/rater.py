from Databases import mysql_connection as db
from statistics import mean
import datetime

def if_empty(column_name, value, *args, **kwargs):
    if value == '' or value == None:
        return 0
    else:
        return 1

def price(column_name, value, *args, **kwargs):
    offer_record = kwargs['offer_record']
    city = offer_record['city']
    district = offer_record['district']
    housing_type = offer_record['housing_type']
    business_type = offer_record['business_type']

    if district is None:
        prices_dict = db.get_custom(f"select price from offers where city = '{city}' and housing_type = '{housing_type}' and business_type = '{business_type}';")
    else:
        prices_dict = db.get_custom(f"select price from offers where city = '{city}' and district = '{district}' and housing_type = '{housing_type}' and business_type = '{business_type}';")

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

def area(column_name, value, *args, **kwargs):
    offer_record = kwargs['offer_record']
    city = offer_record['city']
    district = offer_record['district']
    housing_type = offer_record['housing_type']
    business_type = offer_record['business_type']

    if district is None:
        db_dict = db.get_custom(f"select price, area from offers where city = '{city}' and housing_type = '{housing_type}' and business_type = '{business_type}';")
    else:
        db_dict = db.get_custom(f"select price, area from offers where city = '{city}' and district = '{district}' and housing_type = '{housing_type}' and business_type = '{business_type}';")

    prices = [dictionary['price'] for dictionary in db_dict]
    areas = [dictionary['area'] for dictionary in db_dict]

    try:
        average_price_per_m2 = mean(prices) / mean(areas)
    except TypeError:
        average_price_per_m2 = None
    try:
        offer_price_per_m2 = offer_record['price'] / offer_record['area']
    except TypeError:
        offer_price_per_m2 = None
    if average_price_per_m2 and offer_price_per_m2:
        if offer_price_per_m2 < 0.5 * average_price_per_m2:
            return 1
        elif offer_price_per_m2 < 0.75 * average_price_per_m2:
            return 0.75
        elif offer_price_per_m2 < 1 * average_price_per_m2:
            return 0.5
        elif offer_price_per_m2 < 1.5 * average_price_per_m2:
            return 0.25
        else:
            return 0
    else:
        return None

def price_per_m2(column_name, value, *args, **kwargs):
    offer_record = kwargs['offer_record']
    city = offer_record['city']
    district = offer_record['district']
    housing_type = offer_record['housing_type']
    business_type = offer_record['business_type']

    if district is None:
        db_dict = db.get_custom(f"select price_per_m2 from offers where city = '{city}' and housing_type = '{housing_type}' and business_type = '{business_type}';")
    else:
        db_dict = db.get_custom(f"select price_per_m2 from offers where city = '{city}' and district = '{district}' and housing_type = '{housing_type}' and business_type = '{business_type}';")

    prices = [dictionary['price_per_m2'] for dictionary in db_dict]

    try:
        mean_of_prices = mean(prices)
    except TypeError:
        mean_of_prices = None

    if mean_of_prices:
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
    else:
        return None

def security_deposit(column_name, value, *args, **kwargs):
    if value == '' or value == None:
        return 1
    elif value < 500:
        return 0.75
    elif value < 1000:
        return 0.5
    elif value < 1500:
        return 0.25
    else:
        return 0

def heating(column_name, value, *args, **kwargs):
    if value == 'miejskie':
        return 1
    elif value == 'gazowe':
        return 0
    else:
        return 0

def building_year(column_name, value, *args, **kwargs):
    if value is None:
        return None
    else:
        if value > 2010:
            return 1
        elif value > 2000:
            return 0.75
        elif value > 1950:
            return 0.5
        elif value > 1900:
            return 0.25

def fit_out(column_name, value, *args, **kwargs):
    if value == 'do zamieszkania':
        return 1
    elif value == 'do remontu':
        return 0
    else:
        return None

def bool(column_name, value, *args, **kwargs):
    if value == 1:
        return 1
    elif value == 0:
        return 0

functions_to_apply = {
    'offer_name': [if_empty],
    'offer_thumbnail_url': [if_empty],
    'price': [price],
    'street': [if_empty],
    'district': [if_empty],
    'date_of_the_offer': [date_of_the_offer],
    'offer_id': [if_empty],
    'furniture': [if_empty],
    'area': [area],
    'price_per_m2': [price_per_m2],
    'security_deposit': [security_deposit],
    'heating': [heating],
    'building_year': [building_year],
    'fit_out': [fit_out],

    'internet': [bool],
    'cable_tv': [bool],
    'closed_terrain': [bool],
    'monitoring_or_security': [bool],
    'entry_phone': [bool],
    'antibulglar_doors_windows': [bool],
    'alarm_system': [bool],
    'antibulglar_blinds': [bool],
    'dishwasher': [bool],
    'cooker': [bool],
    'fridge': [bool],
    'oven': [bool],
    'washing_machine': [bool],
    'tv': [bool],
    'elevator': [bool],
    'phone': [bool],
    'AC': [bool],
    'garden': [bool],
    'utility_room': [bool],
    'parking_space': [bool],
    'terrace': [bool],
    'balcony': [bool],
    'non_smokers_only': [bool],
    'separate_kitchen': [bool],
    'basement': [bool],
    'virtual_walk': [bool],
    'two_level_apartment': [bool],
}
