from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
import re
import datetime

def remove_html_tags(input):
    string_wo_br = re.sub(r'<br>', ' ', input)
    yield re.sub(r'\t|\n|\r|<.*>', '', string_wo_br)

def just_numbers(input):
    yield re.sub(r'[^0123456789.,]', '', input)

def word_to_numbers(input):
    words = {
        'Parter': '0',
        'Suterena': '-1',
        'Kawalerka': '1',
        'Poddasze': '99'
    }

    if input in words:
        yield words[input]
    else:
        yield input

def integer_the_price(input):
    input = re.sub(r',', '.', input)
    try:
        yield int(round(float(input)))
    except:
        yield input

def remove_unnecessary_spaces(input):
    yield re.sub(r' {2,}', '', input)

def swap_unnecessary_spaces(input):
    yield re.sub(r' {2,}', ' ', input)

def remove_border_spaces(input):
    yield input.strip()

def response_to_string(input):
    yield re.sub(r'<200 |>', '', str(input))

def datetime_it(input):
    """Returns in a datetime prepared format."""
    months_dict = {
        'stycznia': '1',
        'lutego': '2',
        'marca': '3',
        'kwietnia': '4',
        'maja': '5',
        'czerwca': '6',
        'lipca': '7',
        'sierpnia': '8',
        'września': '9',
        'października': '10',
        'listopada': '11',
        'grudnia': '12',
    }
    try:
        split_string = input.split('</a>') #splits for mobile strings ['<i data-icon="mobile"></i><a href="https://www.olx.pl/mobilne/" target="_blank">Dodane z telefonu</a>o 22:27 20 stycznia 2019']
        split_string = split_string[1].split(',')
    except:
        split_string = input.split(',')
    joined_string = "".join(split_string[0:2])
    split_string = joined_string.split(' ')
    split_string[-2] = months_dict[split_string[-2]]
    l_dt = [split_string[-1], split_string[-2], split_string[-3], split_string[1].split(':')[0], split_string[1].split(':')[1]]
    yield datetime.datetime(int(l_dt[0]),int(l_dt[1]),int(l_dt[2]),int(l_dt[3]),int(l_dt[4]))

class OlxOfferLoader(ItemLoader):
    city_in = MapCompose()
    offer_type = MapCompose()
    offer_url_in = MapCompose(response_to_string)
    offer_name_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    price_in = MapCompose(just_numbers,integer_the_price)
    offer_location_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    date_of_the_offer_in = MapCompose(remove_html_tags,remove_unnecessary_spaces, datetime_it)
    offer_id_in = MapCompose(just_numbers)
    offer_text_in = MapCompose(remove_unnecessary_spaces, remove_html_tags, swap_unnecessary_spaces)
    offer_from_in = MapCompose(remove_html_tags)
    apartment_level_in = MapCompose(remove_html_tags,word_to_numbers,just_numbers,integer_the_price)
    furniture_in = MapCompose(remove_html_tags)
    type_of_building_in = MapCompose(remove_html_tags)
    area_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    amount_of_rooms_in = MapCompose(remove_html_tags,word_to_numbers,just_numbers,integer_the_price)
    additional_rent_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    price_per_m2_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    type_of_market_in = MapCompose(remove_html_tags)
