from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import re
import datetime

def remove_html_tags(input):
    string_wo_br = re.sub(r'<br>', ' ', input)
    yield re.sub(r'\t|\n|\r|<.*?>', '', string_wo_br)

def just_numbers(input):
    yield re.sub(r'[^0123456789.,]', '', input)

def find_image_url(input):
    yield input.split('<img src="')[1].split('"')[0]

def word_to_numbers(input):
    words = {
        'Parter': '0',
        'parter': '0',
        'Suterena': '-1',
        'suterena': '-1',
        'Kawalerka': '1',
        'kawalerka': '1',
        'Poddasze': '99',
        'poddasze': '99'

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
    line = re.sub(r' {2,}', ' ', input)
    yield re.sub(r' , ', ', ', line).strip()

def remove_border_spaces(input):
    yield input.strip()

def response_to_string(input):
    yield re.sub(r'<200 |>', '', str(input))

def delist_string(input):
    yield re.sub("""[[']|]""", '', input)

def datetime_it_OLX(input):
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
    input = re.sub(r' z telefonuo', 'o', input)
    split_string = input.split(',')
    joined_string = "".join(split_string[0:2])
    split_string = joined_string.split(' ')
    split_string[-2] = months_dict[split_string[-2]]
    l_dt = [split_string[-1], split_string[-2], split_string[-3], split_string[1].split(':')[0], split_string[1].split(':')[1]]
    yield datetime.datetime(int(l_dt[0]),int(l_dt[1]),int(l_dt[2]),int(l_dt[3]),int(l_dt[4]))

def datetime_it_Otodom(input):
    """Returns in a datetime prepared format."""
    months_dict = {
        'Stycznia': '1',
        'Lutego': '2',
        'Marca': '3',
        'Kwietnia': '4',
        'Maja': '5',
        'Czerwca': '6',
        'Lipca': '7',
        'Sierpnia': '8',
        'Września': '9',
        'Października': '10',
        'Listopada': '11',
        'Grudnia': '12',
    }
    just_date = re.sub(r'Data aktualizacji: ', '', input)
    normalized_date = re.sub(r' ', '.', just_date)
    split_string = normalized_date.split('.')
    try:
        split_string[1] = months_dict[split_string[1]]
    except:
        pass
    try:
        l_dt = [split_string[-1], split_string[-2], split_string[-3]]
        yield datetime.datetime(int(l_dt[0]),int(l_dt[1]),int(l_dt[2]))
    except:
        yield datetime.datetime(1970,1,1) #too old of an offer

def get_inside_tags(input):

    string_wo_br = re.sub(r'<br>', ' ', input)
    pattern = re.compile(r'(>.*<)')
    inside_tags = pattern.findall(string_wo_br)
    # yield ''.join(inside_tags)
    yield re.sub(r'<.*?>', '', string_wo_br)

class OlxOfferLoader(ItemLoader):
    city_in = MapCompose()
    offer_type = MapCompose()
    offer_url_in = MapCompose(response_to_string)
    offer_thumbnail_url_in = MapCompose(find_image_url)
    offer_name_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    price_in = MapCompose(just_numbers,integer_the_price)
    offer_location_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    date_of_the_offer_in = MapCompose(remove_html_tags,remove_unnecessary_spaces, datetime_it_OLX)
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

class OtodomOfferLoader(OlxOfferLoader):
    offer_location_in = Join()
    offer_location_out = MapCompose(lambda input: ', '.join(input.split(' ')[4:]))
    date_of_the_offer_in = MapCompose(datetime_it_Otodom)
    security_deposit_in = MapCompose(just_numbers,integer_the_price)
    building_material_in = MapCompose()
    windows_in = MapCompose()
    heating_in = MapCompose()
    building_year_in = MapCompose(just_numbers,integer_the_price)
    fit_out_in = MapCompose()
    ready_from_in = MapCompose(datetime_it_Otodom)
    type_of_ownership_in = MapCompose()
    rental_for_students_in = MapCompose()
    media_in = MapCompose(delist_string, swap_unnecessary_spaces)
    security_measures_in = MapCompose(delist_string, swap_unnecessary_spaces)
    additonal_equipment_in = MapCompose(delist_string, swap_unnecessary_spaces)
    additional_information_in = MapCompose(delist_string, swap_unnecessary_spaces)