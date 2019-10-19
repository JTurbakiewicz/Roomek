import logging
import json
import requests
from pprint import pprint


def recognize_location(location="", lat=0, long=0, city=""):
    """ Geocoding using https://nominatim.org/release-docs/develop/api/Search/ """

    if lat != 0 or long != 0:
        zoom = 10  # 3	country, 10	city, 14 suburb, 16	major streets, 17 major and minor streets, 18 building
        req = requests.get(
            url=f"https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={lat}&lon={long}&zoom={zoom}&limit=5")

    # TODO przypadek ze znanym miastem ale checią czegoś wewnątrz:
    # elif city != "":
    #     # using https://nominatim.org/release-docs/develop/api/Search/
    #     req = requests.get(url=f"https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={city}&limit=5")
    #     tloc = json.loads(req.text)
    #     if isinstance(tloc, list):
    #         tloc = loc[0]
    #     box = # x1, y1, x2, y2
    #     req = requests.get(url=f"https://nominatim.openstreetmap.org/?format=json&bounded=1&viewbox={box}&addressdetails=1&q={location}&limit=5")

    else:
        """ using https://nominatim.org/release-docs/develop/api/Search/ """
        req = requests.get(
            url=f"https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q={location}&limit=5")

    loc = json.loads(req.text)

    if not loc:
        logging.info(f"Couldn't find location: {location} {lat} {long}")
        return False
    elif lat == 0 and long == 0:
        for n in loc:
            if n['type'] == "city":
                loc = [n]
        loc = loc[0]

    if "lat" in loc:
        loca = {"name": "no_name", "lat": loc["lat"], "lon": "0.0", "street": "no_street", "city": "no_city",
                "county": "no_conty", "state": "no_state", "country": "no_country", "boundingbox": "", "place_id": "",
                "osm_id": ""}
    else:
        return False

    if "lon" in loc:
        loca["lon"] = loc["lon"]
    if "display_name" in loc:
        loca["name"] = loc["display_name"]
    if "place_id" in loc:
        loca["place_id"] = loc["place_id"]
    if "osm_id" in loc:
        loca["osm_id"] = loc["osm_id"]
    if "boundingbox" in loc:
        loca["boundingbox"] = loc["boundingbox"]
    if "address" in loc:
        if "road" in loc["address"]:
            loca["street"] = loc["address"]["road"]
        if "city" in loc["address"]:
            loca["city"] = loc["address"]["city"]
        if "county" in loc["address"]:
            loca["county"] = loc["address"]["county"]
        if "state" in loc["address"]:
            loca["state"] = loc["address"]["state"]
        if "country" in loc["address"]:
            loca["country"] = loc["address"]["country"]

    return loca


def child_locations(city):
    children = []
    try:
        place_id = recognize_location(location=city)["place_id"]
        places = requests.get(
            url=f"https://nominatim.openstreetmap.org/details.php?osmtype=W&place_id={place_id}&format=json&hierarchy=1&pretty=1&addressdetails=1&keywords=1&linkedplaces=1&group_hierarchy=1&polygon_geojson=0")
        for e in json.loads(places.text)["hierarchy"]["administrative"]:
            if e["admin_level"] == 9:
                place_id = e["place_id"]
                district = requests.get(
                    url=f"https://nominatim.openstreetmap.org/details.php?osmtype=W&place_id={place_id}&format=json&hierarchy=1&pretty=1&addressdetails=1&keywords=1&linkedplaces=1&group_hierarchy=1&polygon_geojson=0")
                if json.loads(district.text)["importance"] > 0.1:
                    children.append(json.loads(district.text)["localname"])
    except (KeyError, TypeError) as e:
        logging.info(f"Couldn't find locations children for: {city}")

    if children:
        return children
    else:
        return False


""" test indicators """
try:
    if recognize_location(lat=52.2319237, long=21.0067265)['city'] == "Warszawa" and \
            recognize_location(location="Warszawa")['city'] == "Warszawa":
        logging.info("Geolocation: OK :)")
    else:
        logging.warning("NOMINATIM NOT WORKING!")
except (KeyError, TypeError) as e:
    logging.warning(f"GEOLOCATION NOT WORKING! {e}")
