import re
from schemas import regex_scheme as rs
from collections import namedtuple
from streets_list import streets_10000 as streets
import unicodedata

ParsingResult = namedtuple('ParsingResult', ["field_name", "field_value"])



def parse_offer(item):
    try:
        offer_name = item['offer_name'][0]
        offer_text = item['offer_text'][0]
        parsing_input = offer_name + ' ' + offer_text
    except KeyError:
        parsing_input = ''

    parsed_results = find_dict_key_regex(parsing_input)

    if parsed_results is not None:
        for result in parsed_results:
            if result.field_name not in item:
                item[result.field_name] = [result.field_value]
                if 'parsed_fields' in item:
                    item['parsed_fields'][0] = item['parsed_fields'][0] + ', ' + result.field_name
                else:
                    item['parsed_fields'] = [result.field_name]
    return item


def find_dict_key_regex(text):
    list_of_results = []
    for field_name, re_dict in rs.items():
        for field_value, regexes in re_dict.items():
            for regex in regexes:
                try:
                    pattern = re.compile(regex, re.I)
                except re.error:
                    print(regex)
                if pattern.search(text) is not None:
                    parsing_result = ParsingResult(field_name=field_name, field_value=field_value)
                    if field_name == 'area' and field_value == 'm2':
                        parsing_result = ParsingResult(field_name=field_name,
                                                       field_value=str(pattern.search(text).group(1)))
                    elif field_name == 'security_deposit' and field_value == 'zł':
                        found_value = pattern.search(text).group(2)
                        if found_value:
                            try:
                                parsing_result = ParsingResult(field_name=field_name,
                                                               field_value=found_value)
                                # print(parsing_result)
                            except:
                                pass
                        else:
                            parsing_result = ParsingResult(field_name=field_name, field_value=None)

                    elif field_name == 'street' and field_value == 'street':
                        parsing_result = ParsingResult(field_name=field_name,
                                                       field_value=str(pattern.search(text).group(2)))
                        street_found = False
                        for street in streets:

                            street = unicodedata.normalize('NFKD', street.lower()).replace(u'ł', 'l').encode('ascii',
                                                                                                             'ignore').decode(
                                "utf-8")
                            parsing_result_stem = unicodedata.normalize('NFKD', parsing_result.field_value).replace(
                                u'ł', 'l').encode('ascii', 'ignore').decode("utf-8")
                            if parsing_result_stem.lower().startswith(street):
                                parsing_result = ParsingResult(field_name=field_name,
                                                               field_value=street.capitalize())
                                street_found = True
                                break
                            elif parsing_result_stem.lower().startswith(street[:-1] + 'ej'):
                                parsing_result = ParsingResult(field_name=field_name,
                                                               field_value=street.capitalize())
                                street_found = True
                                break
                            elif parsing_result_stem.lower().startswith(street[:-1] + 'iej'):
                                parsing_result = ParsingResult(field_name=field_name,
                                                               field_value=street.capitalize())
                                street_found = True
                        if not street_found:
                            parsing_result = ParsingResult(field_name=field_name,
                                                           field_value=None)
                    list_of_results.append(parsing_result)
    if len(list_of_results) == 0:
        return None
    else:
        return list_of_results
