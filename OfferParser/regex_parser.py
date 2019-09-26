import re
from schemas import regex_scheme as rs
from collections import namedtuple

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
                    list_of_results.append(parsing_result)
    if len(list_of_results) == 0:
        return None
    else:
        return list_of_results
