import logging
from geopy.geocoders import Nominatim, GoogleV3, OpenCage, GeoNames
from geopy.point import Point
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderQuotaExceeded, GeocoderAuthenticationFailure
import json
import urllib.parse
import urllib.request
import requests
from pprint import pprint


def recognize_location(location="", lat=0, long=0, city=""):

    # TODO Reverse geocoding (mając lat i long zwróć adres) using https://nominatim.org/release-docs/develop/api/Search/
    if lat != 0 or long != 0:
        # https://nominatim.org/release-docs/develop/api/Reverse/
        zoom = 10       # 3	country, 10	city, 14 suburb, 16	major streets, 17 major and minor streets, 18 building
        req = requests.get(url=f"https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={lat}&lon={long}&zoom={zoom}&limit=5")

    # elif city != "":
    #     # using https://nominatim.org/release-docs/develop/api/Search/
    #     req = requests.get(url=f"https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={city}&limit=5")
    #     tloc = json.loads(req.text)
    #     if isinstance(tloc, list):
    #         tloc = loc[0]
    #     box = # x1, y1, x2, y2
    #     req = requests.get(url=f"https://nominatim.openstreetmap.org/?format=json&bounded=1&viewbox={box}&addressdetails=1&q={location}&limit=5")
    else:
        # using https://nominatim.org/release-docs/develop/api/Search/
        req = requests.get(url=f"https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={location}&limit=5")

    loc = json.loads(req.text)

    print(f"***** TEMP ****** {str(loc)}, of type {type(loc)}")

    if isinstance(loc, list):
        logging.info(f"loc object: {loc}")
        # TODO co jeśli szukane nie jest pierwsze na liście?
        # for n in loc:
        #     print(n["display_name"])
        # TODO co jesli loc jest pusty?
        try:
           loc = loc[0]
        except IndexError:
            logging.warning(f"Location object is probably empty or single object: {str(loc)}")

    loca = {
        "name": "no_name",
        "lat": "0.0",
        "lon": "0.0",
        "street": "no_street",
        "city": "no_city",
        "county": "no_conty",
        "state": "no_state",
        "country": "no_country",
        "boundingbox": "",
        "place_id": "",
        "osm_id": ""
    }

    if "display_name" in loc:
        loca["name"] = loc["display_name"]

    if "lat" in loc:
        loca["lat"] = loc["lat"]

    if "lon" in loc:
        loca["lon"] = loc["lon"]

    if "address" in loc:
        if "road" in loc["address"]:
            loca["street"] = loc["address"]["road"]

    if "address" in loc:
        if "city" in loc["address"]:
            loca["city"] = loc["address"]["city"]

    if "address" in loc:
        if "county" in loc["address"]:
            loca["county"] = loc["address"]["county"]

    if "address" in loc:
        if "state" in loc["address"]:
            loca["state"] = loc["address"]["state"]

    if "address" in loc:
        if "country" in loc["address"]:
            loca["country"] = loc["address"]["country"]

    if "address" in loc:
        if "boundingbox" in loc["address"]:
            loca["boundingbox"] = loc["address"]["boundingbox"]

    if "place_id" in loc:
        loca["place_id"] = loc["place_id"]

    if "osm_id" in loc:
        loca["osm_id"] = loc["osm_id"]

    return loca

""" TEST """

# pprint(recognize_location(lat=52.205691, long=21.036662))
# pprint(recognize_location(lat=51.154191, long=22.036662))
# pprint(recognize_location(lat=52.205691, long=19.836662))
# print()
# pprint(recognize_location(location="Warszawa"))
# pprint(recognize_location(location="Plewiska"))
# pprint(recognize_location(location="Płock"))
# print()
# pprint(recognize_location(location="Warszawie"))
# pprint(recognize_location(location="Poznaniu"))
# pprint(recognize_location(location="Krakowie"))


# TODO to dziala, wersja z Nominatim:
# https://nominatim.openstreetmap.org/details.php?osmtype=W&place_id=198731171&format=json&hierarchy=1&pretty=1&addressdetails=1&keywords=1&linkedplaces=1&group_hierarchy=1&polygon_geojson=0

def child_locations(city):
    place_id = recognize_location(location=city)["place_id"]
    dzieci_poznania = requests.get(url=f"https://nominatim.openstreetmap.org/details.php?osmtype=W&place_id={place_id}&format=json&hierarchy=1&pretty=1&addressdetails=1&keywords=1&linkedplaces=1&group_hierarchy=1&polygon_geojson=0")
    children=[]
    for e in json.loads(dzieci_poznania.text)["hierarchy"]["administrative"]:
        if e["admin_level"] == 9:
            place_id = e["place_id"]
            dzielnica = requests.get(url=f"https://nominatim.openstreetmap.org/details.php?osmtype=W&place_id={place_id}&format=json&hierarchy=1&pretty=1&addressdetails=1&keywords=1&linkedplaces=1&group_hierarchy=1&polygon_geojson=0")
            if json.loads(dzielnica.text)["importance"] > 0.1:
                children.append(json.loads(dzielnica.text)["localname"])
    return children

# test = child_locations("Kraków")
# print(test)
