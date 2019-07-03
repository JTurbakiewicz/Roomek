import requests
import logging
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim, GoogleV3, OpenCage, GeoNames
from geopy.point import Point
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderQuotaExceeded, GeocoderAuthenticationFailure

APP_ID = "1e14e921"
API_key = "b609a1ae5aec948dacb0dc8da2c8ee43"

# https://docs.traveltimeplatform.com/reference/time-filter/

r_headers = {
    'X-Application-Id': APP_ID,
    'X-Api-Key': API_key,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

# TODO sample data for now
payload_for_map = """
{
  "departure_searches": [
    {
      "id": "public transport from Trafalgar Square",
      "coords": {
        "lat": 51.507609,
        "lng": -0.128315
      },
      "transportation": {
        "type": "public_transport"
      },
      "departure_time": "2019-05-19T08:00:00Z",
      "travel_time": 900
    }
  ],
  "arrival_searches": [
    {
      "id": "public transport to Trafalgar Square",
      "coords": {
        "lat": 51.507609,
        "lng": -0.128315
      },
      "transportation": {
        "type": "public_transport"
      },
      "arrival_time": "2019-05-19T08:00:00Z",
      "travel_time": 900,
      "range": {
        "enabled": true,
        "width": 3600
      }
    }
  ]
}
"""

# TODO sample data for now
payload_for_time_filter = """{
  "locations": [
    {
      "id": "London center",
      "coords": {
        "lat": 51.508930,
        "lng": -0.131387
      }
    },
    {
      "id": "Hyde Park",
      "coords": {
        "lat": 51.508824,
        "lng": -0.167093
      }
    },
    {
      "id": "ZSL London Zoo",
      "coords": {
        "lat": 51.536067,
        "lng": -0.153596
      }
    }
  ],
  "departure_searches": [
    {
      "id": "forward search example",
      "departure_location_id": "London center",
      "arrival_location_ids": [
        "Hyde Park",
        "ZSL London Zoo"
      ],
      "transportation": {
        "type": "bus"
      },
      "departure_time": "2019-05-19T08:00:00Z",
      "travel_time": 1800,
      "properties": [
        "travel_time"
      ],
      "range": {
        "enabled": true,
        "max_results": 3,
        "width": 600
      }
    }
  ],
  "arrival_searches": [
    {
      "id": "backward search example",
      "departure_location_ids": [
        "Hyde Park",
        "ZSL London Zoo"
      ],
      "arrival_location_id": "London center",
      "transportation": {
        "type": "public_transport"
      },
      "arrival_time": "2019-05-19T08:00:00Z",
      "travel_time": 1900,
      "properties": [
        "travel_time",
        "distance",
        "distance_breakdown",
        "fares"
      ]
    }
  ]
}
"""


def create_map(headers=r_headers, payload=payload_for_map):
    rsp = requests.request(
        'POST',
        'https://api.traveltimeapp.com/v4/time-map',
        headers=headers,
        data=payload
    )
    # pprint(rsp.json())


def create_time_filter(headers=r_headers, payload=payload_for_time_filter):
    """ Given origin and destination points filter out points that cannot be reached within specified time limit.
    Find out properties of connections between origin and destination points """

    rsp = requests.request(
        'POST',
        'https://api.traveltimeapp.com/v4/time-filter',
        headers=headers,
        data=payload
    )
    # pprint(rsp.json())


# create_map(r_headers, payload_for_map)
# create_time_filter(r_headers, payload_for_time_filter)
#
# fig = plt.figure(figsize=(8, 8))


def recognize_location(location="", lat=0, long=0):
    try:
        geolocator = GeoNames(country_bias=None, username='ar3i', timeout=3, proxies=None, user_agent='geopy/1.20.0',
                              format_string=None, ssl_context=None, scheme='http')
        # geolocator = Nominatim(user_agent="Roomek")
        # geolocator = OpenCage(api_key='9426f4964f6c416e924e3486879c1e49', domain='api.opencagedata.com', scheme='https', timeout=1, proxies=None)

        if lat != 0 or long != 0:
            # reverse geocoding - mając lat i long zwróć adres:
            loc = geolocator.reverse(Point(lat, long), exactly_one=True, timeout=1, feature_code=None, lang=None, find_nearby_type='findNearbyPlaceName')
        # Narrow search when city is known:
        # elif city != "":
        # known city so narrow search area (box = "40, 10, 60, 30"):
        # loc = geolocator.geocode(location, exactly_one=True, timeout=3, country=None, country_bias=None)

        else:
            # recognize the place:
            loc = geolocator.geocode(location, exactly_one=True, timeout=3, country=None, country_bias=None)

        if loc:
            return loc
        else:
            print("error! " + str(loc))

        # TODO get subregions (dzielnice żeby zasugerować) http://www.geonames.org/export/place-hierarchy.html#children

    except GeocoderTimedOut as e:
        print("Error: geocode failed on input %s with message %s" % ("XYZ", str(e)))
    except GeocoderUnavailable as e:
        print("Error: geocode failed on input %s with message %s" % ("XYZ", str(e)))
    except GeocoderQuotaExceeded as e:
        print("Error: geocode failed on input %s with message %s" % ("XYZ", str(e)))
    except GeocoderAuthenticationFailure as e:
        print("Error: geocode failed on input %s with message %s" % ("XYZ", str(e)))
    except:
        print("GeoCoder unknown error.")

format = "JSON"
querry = "Mokotów"
username = "ar3i"

# print("\nMiejsce na podstawie Lat i Long:")
# print(" -->  "+str(recognize_location(lat=51, long=19)))
#
# print("\nMiejsce na podstawie nazwy:")
# print(" -->  "+str(recognize_location(location="Mokotów")))
#
# print("\nMiejsce na podstawie nazwy, odmienione:")
# print(" -->  "+str(recognize_location(location="Mokotowie")))
#
# print("\nMiejsce na podstawie nazwy 2:")
# geolocate = requests.get(url = "http://api.geonames.org/search"+format+"?"+"q="+querry+"&fuzzy=0.9&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\nNeighbours na podstawie nazwy 3:")
# geolocate = requests.get(url = "http://api.geonames.org/neighbours"+format+"?"+"q="+querry+"&username="+username)
# print(geolocate.json())
# # for n in geolocate.json()['geonames']:
# #     print(" -->  "+n["name"])
#
# print("\nNeighbours na podstawie nazwy 4:")
# geolocate = requests.get(url = "http://api.geonames.org/containsJSON"+format+"?"+"q="+querry+"&username="+username)
# print(geolocate.json())
#
# print("\nNeighbours na podstawie nazwy 5:")
# geolocate = requests.get(url = "http://api.geonames.org/siblings"+format+"?"+"q="+querry+"&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\nMiejsca pokrewne:")
# geolocate = requests.get(url = "http://api.geonames.org/search"+format+"?"+"q="+querry+"&username="+username)
# for n in geolocate.json()['geonames']:
#     print(" -->  "+n["name"])
#
# print("\nMiejsca równorzędne (siblings):")
# geoId = 764484
# siblings = requests.get(url="http://api.geonames.org/siblings"+format+"?"+"geonameId="+str(geoId)+"&username="+username)
# print(siblings.json())