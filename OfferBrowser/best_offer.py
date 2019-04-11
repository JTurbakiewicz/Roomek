import PropertyScraper.PropertyScraper.PropertyScraper_mysql_connection as sql

def best_offer(user = None, nr = 3):
    offers = sql.get_custom('select * from offers limit 3;')
    return offers

