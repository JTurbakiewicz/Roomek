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
        req = requests.get(url="https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={0}&lon={1}&zoom={2}&limit=5".format(lat, long, zoom))

    elif city != "":
        # using https://nominatim.org/release-docs/develop/api/Search/
        req = requests.get(url="https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={0}&limit=5".format(city))
        tloc = json.loads(req.text)
        if isinstance(tloc, list):
            tloc = loc[0]
        box = # x1, y1, x2, y2
        req = requests.get(url="https://nominatim.openstreetmap.org/?format=json&bounded=1&viewbox={0}&addressdetails=1&q={1}&limit=5".format(box, location))


    else:
        # using https://nominatim.org/release-docs/develop/api/Search/
        req = requests.get(url="https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={0}&limit=5".format(location))

    loc = json.loads(req.text)

    if isinstance(loc, list):
        # TODO co jeśli szukane nie jest pierwsze na liście?
        # for n in loc:
        #     print(n["display_name"])
        loc = loc[0]

    loca = {
        "name": "",
        "lat": "",
        "lon": "",
        "city": "",
        "county": "",
        "state": "",
        "country": "",
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

    if "city" in loc["address"]:
        loca["city"] = loc["address"]["city"]

    if "county" in loc["address"]:
        loca["county"] = loc["address"]["county"]

    if "state" in loc["address"]:
        loca["state"] = loc["address"]["state"]

    if "country" in loc["address"]:
        loca["country"] = loc["address"]["country"]

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













# TODO wariant z geopy:
# DEFAULT_SENTINEL = None
# geolocator = Nominatim(user_agent="Roomek", format_string=None, view_box=None, bounded=None, country_bias=None, timeout=DEFAULT_SENTINEL, proxies=DEFAULT_SENTINEL, domain='nominatim.openstreetmap.org', scheme=None, ssl_context=DEFAULT_SENTINEL)
# geolocator = GeoNames(country_bias=None, username='ar3i', timeout=3, proxies=None, user_agent='geopy/1.20.0', format_string=None, ssl_context=None, scheme='http')
# geolocator = OpenCage(api_key='9426f4964f6c416e924e3486879c1e49', domain='api.opencagedata.com', scheme='https', timeout=1, proxies=None)
# loc = geolocator.reverse(Point(lat, long), exactly_one=True, timeout=1, language=False, addressdetails=True)
# recognize the place by name:
# loc = geolocator.geocode(location, exactly_one=True, timeout=2, limit=None, addressdetails=False, language=False, geometry=None, extratags=False, country_codes=None, viewbox=None, bounded=None)


# Narrow search when city is known:
# elif city != "":
# loc = geolocator.geocode(location, exactly_one=True, timeout=3, country=None, country_bias=None)

# TODO get subregions (dzielnice żeby zasugerować) http://www.geonames.org/export/place-hierarchy.html#children
# def child_locations(location=""):
#     loc = recognize_location(location=location)
#     geoId = loc.raw['place_id']
#     user = "ar3i"
#     req = requests.get(url="http://api.geonames.org/children?format=JSON&username="+user+"&geonameId="+str(geoId))
#     return req  #json.loads(req.text)

# dzielnice Warszawy:
# print(child_locations(location="Warszawa"))

# # https://www.geonames.org/export/place-hierarchy.html
# username = "ar3i"
# placeID = "7531926"
# print("\n4) Miejsca podrzędne na podstawie ID:")
# geolocate = requests.get(url="http://api.geonames.org/children?format=JSON&username=ar3i&geonameId=7531926")
#
# g = json.loads(geolocate.text)
# print(g)

""" TEST """

# print("\n1) Miejsce na podstawie Lat i Long:")
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']))
# except KeyError:
#     print("keyerror")
#
# print("\n1) Miejsce na podstawie Lat i Long:")
# try:
#     print(" -->  "+str(recognize_location(location="Łódź").raw))
# except KeyError:
#     print("keyerror")

# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['road']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['suburb']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['hamlet']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['state']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['county']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(lat=52, long=19).raw['address']['country']))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(location="Mokotów").latitude))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(location="Mokotów").longitude))
# except KeyError:
#     print("keyerror")
#
# try:
#     print(" -->  "+str(recognize_location(location="Mokotów").address))
# except KeyError:
#     print("keyerror")

# print("\n2) Miejsce na podstawie nazwy:")
# print(" -->  "+str(recognize_location(location="Mokotów")))
#
# print("\n3) Miejsce na podstawie nazwy, odmienione:")
# print(" -->  "+str(recognize_location(location="Warszawie")))
#


# print("\n4) Miejsce na podstawie nazwy 2:")
# geolocate = requests.get(url = "http://api.geonames.org/search"+format+"?"+"q="+querry+"&fuzzy=0.7&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\n5) Neighbours na podstawie nazwy 3:")
# geoId = 764484
# geolocate = requests.get(url = "http://api.geonames.org/neighbours"+format+"?"+"q="+querry+"&geonameId="+str(geoId)+"&username="+username)
# print(geolocate.json())
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\n6) Neighbours na podstawie nazwy 4:")
# geolocate = requests.get(url = "http://api.geonames.org/containsJSON"+format+"?"+"q="+querry+"&username="+username)
# print(geolocate.json())
#
# print("\n7) Neighbours na podstawie nazwy 5:")
# geolocate = requests.get(url = "http://api.geonames.org/siblings"+format+"?"+"q="+querry+"&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\n8) Miejsca pokrewne:")
# geolocate = requests.get(url = "http://api.geonames.org/search"+format+"?"+"q="+querry+"&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\n9) Miejsca równorzędne (siblings):")
# siblings = requests.get(url="http://api.geonames.org/siblings"+format+"?"+"geonameId="+str(geoId)+"&username="+username)
# print(siblings.json())

