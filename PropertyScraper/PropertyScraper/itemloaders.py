from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
import re
import datetime

def remove_html_tags(input):
    yield re.sub(r'\t|\n|\r|<em>|<small>|</small>|</em>', '', input)

def just_numbers(input):
    yield re.sub(r'\D', '', input)

def integer_the_price(input):
    yield int(re.sub(r' zł| ', '', input))

def remove_unnecessary_spaces(input):
    yield re.sub(r' {2,}', '', input)

def swap_unnecessary_spaces(input):
    yield re.sub(r' {2,}', ' ', input)

def remove_border_spaces(input):
    yield input.strip()

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
    yield split_string[-1], split_string[-2], split_string[-3], split_string[1].split(':')[0], split_string[1].split(':')[1]

class OlxOfferLoader(ItemLoader):
    offer_name_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    price_in = MapCompose(integer_the_price)
    offer_location_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    date_of_the_offer_in = MapCompose(remove_html_tags,remove_unnecessary_spaces, datetime_it)
    offer_id_in = MapCompose(just_numbers)
    offer_text_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)