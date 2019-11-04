import re

def to_nominative(input):
    if input[-3:] == 'iej':
        output = input[:-3] + 'a'
    elif input[-2:] == 'ej':
        output = input[:-2] + 'a'
    else:
        output = input
    return output

def to_int(input):
    only_numbers = re.sub(r'[^0123456789,.]', '', input)
    if '.' in only_numbers or ',' in only_numbers:
        only_numbers = only_numbers.split('.')
        if len(only_numbers[-1]) == 2:
            only_numbers = ''.join(only_numbers[:-1])
        else:
            only_numbers = ''.join(only_numbers)
        only_numbers = only_numbers.split(',')
        if len(only_numbers[-1]) == 2:
            only_numbers = ''.join(only_numbers[:-1])
        else:
            only_numbers = ''.join(only_numbers)
    return only_numbers