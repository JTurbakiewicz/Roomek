from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
import re

def remove_html_tags(input):
    yield re.sub(r'\t|\n|\r|', '', input)

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

class OlxOfferLoader(ItemLoader):
    offer_name_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    price_in = MapCompose(integer_the_price)
    offer_location_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    date_of_the_offer_in = MapCompose(remove_html_tags, remove_border_spaces, swap_unnecessary_spaces)
    offer_id_in = MapCompose(just_numbers)
    offer_text_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)