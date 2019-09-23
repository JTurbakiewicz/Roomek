import re
from schemas import regex_scheme as rs
from collections import namedtuple

ParsingResult = namedtuple('ParsingResult', ["field_name", "field_value"])


def parse_name(item):
    try:
        offer_name = item['offer_name'][0]
    except KeyError:
        offer_name = ''

    parsed_results = find_re(offer_name)

    if parsed_results is not None:
        for result in parsed_results:
            if result.field_name not in item:
                item[result.field_name] = [result.field_value]
                if 'parsed_fields' in item:
                    item['parsed_fields'] = item['parsed_fields'][0] + ', ' + result.field_name
                else:
                    item['parsed_fields'] = [result.field_name]
    return item


def find_re(text):
    list_of_results = []
    for field_name, re_dict in rs.items():
        for field_value, regexes in re_dict.items():
            for regex in regexes:
                pattern = re.compile(regex, re.I)
                if pattern.search(text) is not None:
                    parsing_result = ParsingResult(field_name=field_name, field_value=field_value)
                    list_of_results.append(parsing_result)
    if len(list_of_results) == 0:
        return None
    else:
        return list_of_results
