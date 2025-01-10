import re
from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId
from beanie.operators import In
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.attraction_input import AttractionInput
from lib.graphql.inputs.create_attraction_input import CreateAttractionInput
from lib.graphql.inputs.update_attraction_input import UpdateAttractionInput
from lib.graphql.types.attraction_page import AttractionPage
from lib.graphql.types.error import Error
from lib.helpers.attraction_helper import attraction_model_to_type
from lib.helpers.customer_helper import get_verified_customer
from lib.models.attraction_category_model import AttractionCategoryModel
from lib.models.attraction_model import AttractionModel
from lib.models.sightseeing_model import SightseeingModel
from lib.services import gemini_client


async def read_attractions(attractions: AttractionInput, info: Info):
    try:
        unique_filters = [
            attractions.just_alphabetical,
            attractions.just_downtown_first,
            attractions.just_recommended,
        ]
        if len([f for f in unique_filters if f]) > 1:
            return Error(
                status=400,
                message="Only one unique (just_*) filter can be used at a time!",
            )

        sightseeing = []
        if attractions.sightseeing:
            if len(attractions.sightseeing) > 3:
                return Error(
                    status=400, message="Cannot add more than 3 sightseeing categories!"
                )

            sightseeing_ids = [PydanticObjectId(id) for id in attractions.sightseeing]
            sightseeing = (
                await SightseeingModel.find(
                    In(SightseeingModel.id, (sightseeing_ids))
                ).to_list()
                if attractions.sightseeing
                else []
            )
            if attractions.sightseeing and not sightseeing:
                return Error(status=400, message="Invalid sightseeing ID!")
        else:
            attractions.sightseeing = []

        if attractions.custom_sightseeing:

            customer = await get_verified_customer(info)
            if not customer:
                return Error(status=403, message="Forbidden!")

            searched_sightseeing = await SightseeingModel.find(
                {"source_customer_id": {"$in": [str(customer.id)]}}
            ).to_list()
            if len(searched_sightseeing) > 5:
                return Error(
                    status=400, message="Cannot add more than 5 custom categories!"
                )

            existing_custom_sightseeing = await SightseeingModel.find_one(
                SightseeingModel.label == attractions.custom_sightseeing
            )

            if not existing_custom_sightseeing:
                custom_sightseeing = SightseeingModel(
                    label=attractions.custom_sightseeing,
                    source_customer_id=[str(customer.id)],
                    updated_at=datetime.now(),
                )
                await custom_sightseeing.insert()

                if sightseeing:
                    sightseeing.append(custom_sightseeing)
                    attractions.sightseeing.append(str(custom_sightseeing.id))

                if not sightseeing:
                    sightseeing = [custom_sightseeing]

            if (
                existing_custom_sightseeing
                and str(customer.id) in existing_custom_sightseeing.source_customer_id
            ):
                return Error(status=400, message="Custom sightseeing already exists!")

            if (
                existing_custom_sightseeing
                and str(customer.id)
                not in existing_custom_sightseeing.source_customer_id
            ):
                if sightseeing:
                    sightseeing.append(existing_custom_sightseeing)
                    attractions.sightseeing.append(str(existing_custom_sightseeing.id))
                    existing_custom_sightseeing.updated_at = datetime.now()
                    existing_custom_sightseeing.source_customer_id.append(
                        str(customer.id)
                    )
                    await existing_custom_sightseeing.save()

                if not sightseeing:
                    sightseeing = [existing_custom_sightseeing]
                    attractions.sightseeing = [existing_custom_sightseeing.id]
                    existing_custom_sightseeing.updated_at = datetime.now()
                    existing_custom_sightseeing.source_customer_id.append(
                        str(customer.id)
                    )
                    await existing_custom_sightseeing.save()

        attraction_data = await _get_attraction_page_from_db(attractions)

        if attraction_data.total < 10 and not attractions.id:

            await _fetch_attractions_from_ai(attractions, sightseeing)
            attraction_data = await _get_attraction_page_from_db(attractions)

        return attraction_data

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_attraction(attraction: CreateAttractionInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        if attraction.sightseeing_id:
            sightseeing = await SightseeingModel.find(
                SightseeingModel.id == PydanticObjectId(attraction.sightseeing_id)
            ).first_or_none()
            if not sightseeing:
                return Error(status=400, message="Invalid sightseeing ID!")

        if attraction.attraction_category:
            attraction_type = await AttractionModel.find(
                AttractionCategoryModel.id
                == PydanticObjectId(attraction.attraction_category)
            ).first_or_none()
            if not attraction_type:
                return Error(status=400, message="Invalid attraction type ID!")

        if attraction.always_open:
            if attraction.closing_time:
                return Error(status=400, message="Invalid timing input combination!")
            if attraction.opening_time:
                return Error(status=400, message="Invalid timing input combination!")

        elif attraction.opening_time and attraction.closing_time:
            pattern = r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$"

            if re.match(pattern, attraction.opening_time) and re.match(
                pattern, attraction.closing_time
            ):
                if attraction.opening_time > attraction.closing_time:
                    return Error(
                        status=400,
                        message="Invalid timing input opening time cannot be after closing time!",
                    )

            else:
                return Error(
                    status=400,
                    message="Invalid timing input! Please use the format: HH:MM:SS",
                )
        else:
            return Error(
                status=400, message="You have to select both opening and closing time!"
            )

        await AttractionModel.insert_one(
            AttractionModel(
                title=attraction.title,
                address=attraction.address or None,
                city=attraction.city or None,
                country=attraction.country or None,
                zip_code=attraction.zip_code or None,
                images=attraction.images or None,
                sightseeing_id=attraction.sightseeing_id or None,
                attraction_category_id=attraction.attraction_category or None,
                lat=attraction.lat or None,
                lng=attraction.lng or None,
                centre_offset=attraction.centre_offset or None,
                restaurant_count=attraction.restaurant_count or None,
                accomodation_count=attraction.accomodation_count or None,
                description=attraction.description or None,
                always_open=attraction.always_open or None,
                opening_time=attraction.opening_time or None,
                closing_time=attraction.closing_time or None,
                contact_number=attraction.contact_number or None,
                source_customer_id=str(customer.id),
                is_source_representative=attraction.is_source_representative or False,
            )
        )
        return Error(status=201, message="Attraction created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_attraction(attraction: UpdateAttractionInput, info: Info):
    try:
        customer = await get_verified_customer(info)

        if not customer:
            return Error(status=403, message="Forbidden!")

        if attraction.id is None:
            return Error(status=400, message="Invalid attraction ID!")

        searched_attraction = await AttractionModel.find(
            AttractionModel.id == PydanticObjectId(attraction.id),
            AttractionModel.source_customer_id == str(customer.id),
        ).first_or_none()

        if not searched_attraction:
            return Error(status=404, message="Attraction not found!")

        if attraction.title:
            searched_attraction.title = attraction.title

        if attraction.address:
            searched_attraction.address = attraction.address

        if attraction.city:
            searched_attraction.city = attraction.city

        if attraction.country:
            searched_attraction.country = attraction.country

        if attraction.zip_code:
            searched_attraction.zip_code = attraction.zip_code

        if attraction.images:
            searched_attraction.images = attraction.images

        if attraction.sightseeing_id:
            sightseeing = await SightseeingModel.find(
                SightseeingModel.id == PydanticObjectId(attraction.sightseeing_id)
            ).first_or_none()

            if not sightseeing:
                return Error(status=400, message="Invalid sightseeing ID!")

            searched_attraction.sightseeing_id = attraction.sightseeing_id

        if attraction.attraction_category:
            attraction_type = await AttractionCategoryModel.find(
                AttractionCategoryModel.id
                == PydanticObjectId(attraction.attraction_category)
            ).first_or_none()
            if not attraction_type:
                return Error(status=400, message="Invalid attraction type ID!")

            searched_attraction.attraction_category_id = attraction.attraction_category

        if attraction.lat:
            searched_attraction.lat = attraction.lat

        if attraction.lng:
            searched_attraction.lng = attraction.lng

        if attraction.centre_offset:
            searched_attraction.centre_offset = attraction.centre_offset

        if attraction.restaurant_count:
            searched_attraction.restaurant_count = attraction.restaurant_count

        if attraction.accomodation_count:
            searched_attraction.accomodation_count = attraction.accomodation_count

        if attraction.description:
            searched_attraction.description = attraction.description

        if attraction.always_open:
            if attraction.closing_time:
                return Error(status=400, message="Invalid timing input combination!")
            if attraction.opening_time:
                return Error(status=400, message="Invalid timing input combination!")
            searched_attraction.always_open = attraction.always_open
            searched_attraction.opening_time = None
            searched_attraction.closing_time = None

        elif attraction.opening_time and attraction.closing_time:
            pattern_with_seconds = r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$"

            if re.match(pattern_with_seconds, attraction.opening_time) and re.match(
                pattern_with_seconds, attraction.closing_time
            ):
                if attraction.opening_time > attraction.closing_time:
                    return Error(
                        status=400,
                        message="Invalid timing input opening time cannot be after closing time!",
                    )

                searched_attraction.always_open = False
                searched_attraction.opening_time = attraction.opening_time
                searched_attraction.closing_time = attraction.closing_time
            else:
                return Error(
                    status=400,
                    message="Invalid timing input! Please use the format: HH:MM:SS",
                )
        elif attraction.opening_time or attraction.closing_time:
            return Error(
                status=400, message="You have to select both opening and closing time!"
            )

        if attraction.contact_number:
            searched_attraction.contact_number = attraction.contact_number

        if attraction.is_source_representative:
            searched_attraction.is_source_representative = (
                attraction.is_source_representative
            )

        searched_attraction.updated_at = datetime.now(timezone.utc)

        await searched_attraction.save()

        return await attraction_model_to_type(searched_attraction)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def _fetch_attractions_from_ai(
    attractions: AttractionInput, sightseeing: Optional[list[SightseeingModel]]
):

    ai_result = await gemini_client.get_popular_attractions(
        attractions.area_name,
        [s.label for s in sightseeing] if sightseeing else None,
        attractions.max_centre_offset,
        child_friendly=attractions.child_friendly,
        pet_friendly=attractions.pet_friendly,
        lgbtq_friendly=attractions.lgbtq_friendly,
    )

    if not ai_result:
        return Error(status=500, message="AI did not respond with any results")

    new_ai_results = []
    for a in ai_result:
        existing_attraction = await AttractionModel.find(
            AttractionModel.title == a.get("name"),
            AttractionModel.city == a.get("city"),
        ).first_or_none()

        if not existing_attraction:
            new_ai_results.append(a)

        if existing_attraction:
            await existing_attraction.delete()
            new_ai_results.append(a)

    await AttractionModel.insert_many(
        [
            AttractionModel(
                title=a.get("name"),
                address=a.get("address") or attractions.area_name,
                city=a.get("city"),
                country=a.get("country"),
                lat=a.get("latitude"),
                lng=a.get("longitude"),
                centre_offset=a.get("distance_from_city_center"),
                restaurant_count=a.get("nearby_restaurants"),
                accomodation_count=a.get("nearby_accomodations"),
                sightseeing_ids=[str(s) for s in attractions.sightseeing] or None,
                description=a.get("description"),
                opening_time=_valid_iso_time(a.get("opening_time")),
                closing_time=_valid_iso_time(a.get("closing_time")),
                source="ai",
                lgbtq_friendly=attractions.lgbtq_friendly or None,
                pet_friendly=attractions.pet_friendly or None,
                child_friendly=attractions.child_friendly or None,
            )
            for a in new_ai_results
        ]
    )


async def _get_attraction_page_from_db(attractions: AttractionInput):
    page = attractions.page or 1

    query = (
        AttractionModel.find()
        .limit(config.PAGE_SIZE)
        .skip((page - 1) * config.PAGE_SIZE)
    )

    if attractions.rating:
        if attractions.rating < 5:
            query = query.find(
                AttractionModel.rating >= attractions.rating,
                AttractionModel.rating < attractions.rating + 1,
            )

        else:
            query = query.find(AttractionModel.rating == 5)

    if attractions.sightseeing:
        query = query.find(
            In(AttractionModel.sightseeing_ids, (attractions.sightseeing))
        )

    if attractions.max_centre_offset:
        query = query.find(
            AttractionModel.centre_offset <= attractions.max_centre_offset
        )

    if attractions.id:
        query = query.find(AttractionModel.id == PydanticObjectId(attractions.id))

    if attractions.search:
        query = query.find({"$text": {"$search": attractions.search}})

    if attractions.coordinates:
        query = query.find(
            AttractionModel.lat < attractions.coordinates.lat + 2,
            AttractionModel.lat > attractions.coordinates.lat - 2,
            AttractionModel.lng < attractions.coordinates.lng + 2,
            AttractionModel.lng > attractions.coordinates.lng - 2,
        )

    if attractions.just_alphabetical:
        query = query.sort(AttractionModel.title)

    if attractions.just_downtown_first:
        query = query.sort(AttractionModel.centre_offset)

    if attractions.just_recommended:
        query = query.find(AttractionModel.rating != None).sort(-AttractionModel.rating)

    if attractions.area_name:
        pattern = attractions.area_name
        query_filter = {
            "$or": [
                {"address": {"$regex": pattern, "$options": "i"}},
                {"city": {"$regex": pattern, "$options": "i"}},
                {"country": {"$regex": pattern, "$options": "i"}},
                {"description": {"$regex": pattern, "$options": "i"}},
            ]
        }
        query = query.find(query_filter)

    if attractions.child_friendly:
        query = query.find(AttractionModel.child_friendly == attractions.child_friendly)

    if attractions.pet_friendly:
        query = query.find(AttractionModel.pet_friendly == attractions.pet_friendly)

    if attractions.lgbtq_friendly:
        query = query.find(AttractionModel.lgbtq_friendly == attractions.lgbtq_friendly)

    total_records = await query.count()
    result = await query.to_list()

    return AttractionPage(
        items=[await attraction_model_to_type(a) for a in result],
        page=page,
        total=total_records,
    )


def _valid_iso_time(string: str):
    try:
        match = re.match("^[0-9]{2}:[0-9]{2}:[0-9]{2}$", string)
        if match:
            return string

    except Exception as e:
        return None
