def abc(column_name, value, *args, **kwargs):
    print(str(*args))
    print('funkcja')
    return '1'

functions_to_apply = {
    'offer_url': [abc, abc],
    'price': [abc, abc]
}
