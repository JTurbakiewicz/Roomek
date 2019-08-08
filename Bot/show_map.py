import requests
import logging
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap


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
