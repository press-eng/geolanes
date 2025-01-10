import json
import re
from datetime import datetime
from typing import List, Optional

import google.generativeai as genai
from dateutil import parser

from lib import config

genai.configure(api_key=config.GOOGLE_GENAI_API_KEY)

_model = genai.GenerativeModel("gemini-pro")


async def get_popular_attractions(
    area: Optional[str],
    sightseeing: Optional[list[str]],
    max_centre_offset: Optional[int],
    child_friendly: Optional[bool],
    pet_friendly: Optional[bool],
    lgbtq_friendly: Optional[bool],
):
    try:
        prompt = (
            f"List 8 popular {', '.join(sightseeing) if sightseeing else ''} places in {area or 'the world'}. "
            f"Provide name, address, city, country, latitude, longitude, distance from city center (in meters), "
            f"number of nearby restaurants, number of nearby accommodations, opening time (ISO format), "
            f"closing_time (ISO format), description as well(mention the {area or 'the world'} in it). Provide in JSON format in snake_case without any special characters. "
            f"The top-level object should be an array."
        )
        if max_centre_offset:
            prompt += f" Distance from the center of the city should not be more than {max_centre_offset} meters."
        if child_friendly:
            prompt += " Make sure the places are child friendly."
        if pet_friendly:
            prompt += " Make sure the places are pet friendly."
        if lgbtq_friendly:
            prompt += " Make sure the places are LGBTQ friendly."

        response = await _model.generate_content_async(prompt)

        candidate = response.candidates[0]
        generated_text = "".join([part.text for part in candidate.content.parts])

        match = re.search(r"```json\s*([\s\S]*?)\s*```", generated_text)
        if match:
            json_content = match.group(1)
            return json.loads(json_content.strip())

        match = re.search(r"\[.*\]", generated_text, re.DOTALL)
        if match:
            json_content = match.group(0)
            return json.loads(json_content.strip())

        try:
            return json.loads(generated_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")

    except Exception as e:
        print(f"Error in get_popular_attractions: {e}")

    return []


async def get_tour_suggestion(area: str, start_time: datetime, end_time: datetime):
    response = await _model.generate_content_async(
        f"List 10 popular places in {area} for a tour between {start_time} and {end_time}. Provide name, city, country, latitude, longitude, distance from city center (in meters), number of nearby restaurants, number of nearby accommodations, date time (in ISO format), opening time (in ISO format), closing time (in ISO format), description as well. Provide in json format in snake casing. Top level object should be a list."
    )

    match = re.search("```json([\S\s]*)```", response.text)
    if match:
        return json.loads(match.group(1))

    match2 = re.search("```json([\S\s]*}),", response.text)
    if match2:
        return json.loads(match2.group(1) + "\n]")

    return []


async def get_create_tour_tokens(prompt: str):
    response = await _model.generate_content_async(
        f"Extract location, start_time (in ISO format), end_time (in ISO format) from: {prompt}. Provide in json format."
    )

    try:
        data = json.loads(response.text)
        return {
            "location": data.get("location"),
            "start_time": (parser.parse(data["start_time"]) if data.get("start_time") else None),
            "end_time": (parser.parse(data["end_time"]) if data.get("end_time") else None),
        }

    except Exception as e:
        print(e)
        return None


async def get_popular_states(country: str):
    response = await _model.generate_content_async(
        f"List all states/provinces in {country}. Provide name. Provide in json format in snake casing. Top level object should be a list."
    )

    match = re.search("```json([\S\s]*)```", response.text)
    if match:
        return json.loads(match.group(1))

    match2 = re.search("```json([\S\s]*}),", response.text)
    if match2:
        return json.loads(match2.group(1) + "\n]")

    return []


def _mock():
    return json.loads(
        """
[
  {
    "name": "Colosseum",
    "city": "Rome",
    "country": "Italy",
    "latitude": 41.890213,
    "longitude": 12.492495,
    "distance_from_city_center": 900,
    "nearby_restaurants": 150,
    "nearby_accommodations": 200,
    "opening_time": "08:30:00",
    "closing_time": "19:00:00",
    "description": "The Colosseum is an iconic ancient amphitheater in the center of the city of Rome, Italy. Built in the 1st century AD, it is the largest ancient amphitheater ever built, and is still the largest standing amphitheater in the world today. The Colosseum was used for gladiatorial contests and other public spectacles. It is one of the most popular tourist attractions in Rome, and is a UNESCO World Heritage Site."
  },
  {
    "name": "Vatican City",
    "city": "Rome",
    "country": "Vatican City",
    "latitude": 41.901957,
    "longitude": 12.455121,
    "distance_from_city_center": 2000,
    "nearby_restaurants": 50,
    "nearby_accommodations": 100,
    "opening_time": "09:00:00",
    "closing_time": "18:00:00",
    "description": "Vatican City is a city-state, microstate, and enclave within Rome, Italy. It is the smallest country in the world by both area and population. Vatican City is the seat of the Roman Catholic Church, and is the residence of the Pope. The Vatican Museums are one of the most popular tourist attractions in Rome, and are home to a vast collection of art and artifacts."
  }
]
"""
    )
