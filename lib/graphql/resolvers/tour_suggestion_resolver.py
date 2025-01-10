from dateutil import parser

from lib.graphql.inputs.tour_suggestion_input import TourSuggestionInput
from lib.graphql.types.error import Error
from lib.graphql.types.tour_suggestion import TourSuggestion
from lib.graphql.types.venture import Venture
from lib.helpers.attraction_helper import attraction_model_to_type
from lib.models.attraction_model import AttractionModel
from lib.services import gemini_client
from lib.utils import validate_then_handle


async def read_tour_suggstion(tour: TourSuggestionInput):
    def read_tour_suggestion_by_tokens(tour):
        return _read_tour_suggestion_by_tokens(
            tour.area_name, tour.start_time, tour.end_time
        )

    async def read_tour_suggestion_by_prompt(tour):
        tokens = await gemini_client.get_create_tour_tokens(tour.ai_prompt)

        print("t", tokens)

        if (
            tokens
            and tokens["location"]
            and tokens["start_time"]
            and tokens["end_time"]
        ):
            return await _read_tour_suggestion_by_tokens(
                tokens["location"], tokens["start_time"], tokens["end_time"]
            )

        return Error(
            status=422, message="Please try again with a more relevant prompt!"
        )

    validator_config = [
        {
            "args": ["start_time", "end_time", "area_name"],
            "handler": read_tour_suggestion_by_tokens,
        },
        {
            "args": ["ai_prompt"],
            "handler": read_tour_suggestion_by_prompt,
        },
    ]

    try:
        return await validate_then_handle(validator_config, tour)

    except ValueError as e:
        print(e)
        return Error(status=400, message=str(e))

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def _read_tour_suggestion_by_tokens(
    area_name: str, start_time: str, end_time: str
):
    suggestions = await gemini_client.get_tour_suggestion(
        area_name, start_time, end_time
    )
    if suggestions:
        existing_records = []
        new_suggestions = []

        for s in suggestions:
            old_attraction = await AttractionModel.find(
                AttractionModel.city == s["city"], AttractionModel.title == s["name"]
            ).first_or_none()
            if old_attraction:
                existing_records.append(
                    (old_attraction, parser.parse(s.get("date_time")))
                )

            else:
                new_suggestions.append(s)

        await AttractionModel.insert_many(
            [
                AttractionModel(
                    title=s.get("name"),
                    city=s.get("city"),
                    country=s.get("country"),
                    lat=s.get("latitude"),
                    lng=s.get("longitude"),
                    centre_offset=s.get("distance_from_city_center"),
                    restaurant_count=s.get("nearby_restaurants"),
                    accomodation_count=s.get("nearby_accomodations"),
                )
                for s in new_suggestions
            ]
        )

        new_records = []
        for s in new_suggestions:
            existing_attraction = await AttractionModel.find(
                AttractionModel.city == s["city"], AttractionModel.title == s["name"]
            ).first_or_none()
            if existing_attraction:
                new_records.append(
                    (existing_attraction, parser.parse(s.get("date_time")))
                )

        records = [*existing_records, *new_records]

        return TourSuggestion(
            ventures=[
                Venture(
                    time=t,
                    attraction=await attraction_model_to_type(a),
                )
                for a, t in records
            ],
            start_date=start_time,
            end_date=end_time,
        )

    return Error(status=422, message="Please try again with a more relevant prompt!")
