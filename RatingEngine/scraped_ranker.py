scraped_rating_rules = {
    'offer_url' : -100,
    'city': -100,
    'housing_type': -100,
    'business_type': -100,
    'offer_name': -100,
    'offer_thumbnail_url': -100,
    'price': -100,
    'street': -1,
    'district': -1,
    'date_of_the_offer': -1,
    'offer_id': -1,
    'offer_text': -100,
    'offer_from': -1,
    'apartment_level': -1,
    'furniture': -1,
    'type_of_building': -1,
    'area': -1,
    'amount_of_rooms': -1,
    'additional_rent': -1,
    'price_per_m2': -1,
    'type_of_market': -1,
    'security_deposit': -1,
    'building_material': -1,
    'windows': -1,
    'heating': -1,
    'building_year': -1,
    'fit_out': -1,
    'ready_from': -1,
    'type_of_ownership': -1,
    'rental_for_students': -1,
    'location_latitude': -1,
    'location_longitude': -1,
    'type_of_room': -1,
    'preferred_locator': -1,
    'creation_time': 0,
    'modification_time': 0,
}  #an initial check whether specific data was scraped

def initial_rating(item):
    scraped_ranking = 0
    if len(item) > 2:

        for rule, weight in scraped_rating_rules.items():
            try:
                if item[rule][0] is None: scraped_ranking += weight
            except KeyError:
                scraped_ranking += weight

        item['scraped_ranking'] = [scraped_ranking]
    return item