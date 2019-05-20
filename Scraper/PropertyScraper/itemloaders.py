from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import re
import datetime
from OfferParser.translator import translate

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
    yield re.sub("""[[]|]""", '', input)

def street_it(input):
    yield re.sub(r'ul. ', '', str(input)).title()

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
    pattern = re.compile(r'"dateModified":".*?"')
    try:
        date_unprocessed = pattern.findall(str(input))[0]
        only_date_string = re.sub(r'dateModified":', '', date_unprocessed)
        only_date_string = re.sub(r'"', '', only_date_string)
        date, hour = only_date_string.split(' ')
        year, month, day = date.split('-')
        hour, minute, second = hour.split(':')
        yield datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    except:
        print('failed' + str(input))

def ready_from_Otodom(input):
    """Returns in a datetime prepared format."""
    year, month, day = input.split('-')
    yield datetime.datetime(int(year), int(month), int(day))


def get_inside_tags(input):
    string_wo_br = re.sub(r'<br>', ' ', input)
    pattern = re.compile(r'(>.*<)')
    yield re.sub(r'<.*?>', '', string_wo_br)

def district(input):
    split_input = input.title().split(',')
    if len(split_input) > 2:
        yield split_input[2].strip()
    else:
        yield None

def district_otodom(input):
    split_input = input.title().split(',')
    if len(split_input) == 2:
        yield split_input[1].strip()

def furniture(input):
    if input == 'Tak':
        return True
    elif input == 'Nie':
        return False
    else:
        return None

def location_latitude_otodom(input):
    print(input)
    pattern = re.compile(r'"geo":{"@type":"GeoCoordinates","latitude":.*?,"')
    try:
        latidude_unprocessed = pattern.findall(str(input))
        unprocessed_latitude = max(latidude_unprocessed,key=len)
        print(unprocessed_latitude)
        yield float(re.sub(r'[^0123456789.]', '', unprocessed_latitude))

    except:
        print('failed' + str(input))

def location_latitude_otodom(input):
    pattern = re.compile(r'"geo":{"@type":"GeoCoordinates","latitude":.*?,"')
    try:
        latidude_unprocessed = pattern.findall(str(input))
        unprocessed_latitude = max(latidude_unprocessed,key=len)
        yield float(re.sub(r'[^0123456789.]', '', unprocessed_latitude))

    except Exception as e:
        print(e)
        print('failed' + str(input))

def location_longitude_otodom(input):
    pattern = re.compile(r'"longitude":.*?},')
    try:
        longitude_unprocessed = pattern.findall(str(input))
        unprocessed_longitude = max(longitude_unprocessed,key=len)
        unprocessed_longitude = unprocessed_longitude.split(',')[0]
        yield float(re.sub(r'[^0123456789.]', '', unprocessed_longitude))

    except Exception as e:
        print('failed' + str(input))
        print (e)


class OlxOfferLoader(ItemLoader):
    city_in = MapCompose()
    housing_type_in = MapCompose(translate)
    business_type_in = MapCompose(translate)
    offer_url_in = MapCompose(response_to_string)
    offer_thumbnail_url_in = MapCompose(find_image_url)
    offer_name_in = MapCompose(remove_html_tags, remove_unnecessary_spaces)
    price_in = MapCompose(just_numbers,integer_the_price)
    street_in = MapCompose(street_it)
    district_in = MapCompose(district)
    date_of_the_offer_in = MapCompose(remove_html_tags,remove_unnecessary_spaces, datetime_it_OLX)
    offer_id_in = MapCompose(just_numbers)
    offer_text_in = MapCompose(remove_unnecessary_spaces, remove_html_tags, swap_unnecessary_spaces)
    offer_from_in = MapCompose(remove_html_tags,translate)
    apartment_level_in = MapCompose(remove_html_tags,word_to_numbers,just_numbers,integer_the_price)
    furniture_in = MapCompose(remove_html_tags, furniture)
    type_of_building_in = MapCompose(remove_html_tags,translate)
    area_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    amount_of_rooms_in = MapCompose(remove_html_tags,word_to_numbers,just_numbers,integer_the_price)
    additional_rent_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    price_per_m2_in = MapCompose(remove_html_tags,just_numbers,integer_the_price)
    type_of_market_in = MapCompose(remove_html_tags, translate)

class OtodomOfferLoader(OlxOfferLoader):
    district_in = MapCompose(district_otodom)
    date_of_the_offer_in = MapCompose(datetime_it_Otodom)
    security_deposit_in = MapCompose(just_numbers,integer_the_price)
    building_material_in = MapCompose(translate)
    windows_in = MapCompose(translate)
    heating_in = MapCompose(translate)
    building_year_in = MapCompose(just_numbers,integer_the_price)
    fit_out_in = MapCompose(translate)
    ready_from_in = MapCompose(ready_from_Otodom)
    type_of_ownership_in = MapCompose(translate)
    rental_for_students_in = MapCompose(translate)
    location_latitude_in = MapCompose(location_latitude_otodom)
    location_longitude_in = MapCompose(location_longitude_otodom)

class OlxRoomLoader(OlxOfferLoader):
    type_of_room_in = MapCompose(remove_html_tags, translate)
    preferred_locator_in = MapCompose(remove_html_tags, translate)