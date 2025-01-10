import asyncio

import googlemaps

from lib import config

_gmaps = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)


def _find_place_sync(address):
    try:
        result = _gmaps.find_place(address, input_type="textquery", fields=["place_id", "geometry"])
        if len(result["candidates"]):
            location = result["candidates"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])

    except Exception as e:
        print(e)

    return None


def find_place_coordinates(address):
    return asyncio.to_thread(_find_place_sync, address)
