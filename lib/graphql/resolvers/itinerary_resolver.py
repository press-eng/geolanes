import re
from datetime import datetime, timezone

from beanie import PydanticObjectId
from beanie.operators import In
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_itinerary_input import CreateItineraryInput
from lib.graphql.inputs.create_itinerary_video_input import CreateItineraryVideoInput
from lib.graphql.inputs.customer_itinerary_input import CustomerItineraryInput
from lib.graphql.inputs.itinerary_preview_input import ItineraryPreviewInput
from lib.graphql.inputs.update_itinerary_append_input import UpdateItineraryAppendInput
from lib.graphql.inputs.update_itinerary_input import UpdateItineraryInput
from lib.graphql.types.cutomer_itinerary_page import CustomerItineraryPage
from lib.graphql.types.error import Error
from lib.graphql.types.itinerary_preview_page import ItineraryPreviewPage
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.itinerary_helper import (
    itinerary_model_to_customer_type,
    itinerary_model_to_preview_type,
)
from lib.models.dto.itinerary_story_item_dto import ItineraryStoryItemDto
from lib.models.itinerary_audio_model import ItineraryAudioModel
from lib.models.itinerary_model import ItineraryModel
from lib.models.itinerary_video_model import ItineraryVideoModel
from lib.models.tour_model import TourModel


async def read_itinerary_previews(itineraries: ItineraryPreviewInput):
    page = itineraries.page or 1

    try:
        filters = dict()
        aggregation_filters = dict()

        if itineraries.id:
            filters["_id"] = PydanticObjectId(itineraries.id)

        if itineraries.tour:
            filters["tour_id"] = itineraries.tour

        if itineraries.search:
            filters["title"] = {"$regex": re.compile(itineraries.search, re.IGNORECASE)}

        if itineraries.sightseeing:
            aggregation_filters["attraction.sightseeing_id"] = itineraries.sightseeing

        pipeline = [
            {
                "$addFields": {
                    "fk_attraction_id": {"$toObjectId": "$attraction_id"},
                },
            },
            {
                "$lookup": {
                    "from": "attractions",
                    "localField": "fk_attraction_id",
                    "foreignField": "_id",
                    "as": "attraction",
                },
            },
            {
                "$unwind": {
                    "path": "$attraction",
                    "preserveNullAndEmptyArrays": True,
                },
            },
        ]

        if len(filters.keys()) > 0:
            pipeline = [
                {
                    "$match": filters,
                },
                *pipeline,
            ]

        if len(aggregation_filters.keys()) > 0:
            pipeline = [
                *pipeline,
                {
                    "$match": aggregation_filters,
                },
            ]

        total = len(await ItineraryModel.aggregate(pipeline).to_list())

        pipeline = [
            *pipeline,
            {"$skip": (page - 1) * config.PAGE_SIZE},
            {"$limit": config.PAGE_SIZE},
        ]

        result = await ItineraryModel.aggregate(pipeline).to_list()
        record_ids = [r["_id"] for r in result]
        records = await ItineraryModel.find(In(ItineraryModel.id, record_ids)).to_list()

        return ItineraryPreviewPage(
            items=[await itinerary_model_to_preview_type(i) for i in records],
            page=page,
            total=total,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_customer_itineraries(itineraries: CustomerItineraryInput, info: Info):
    page = itineraries.page or 1
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        query = ItineraryModel.find()

        if itineraries.search:
            query = query.find(
                {ItineraryModel.title: re.compile(itineraries.search, re.IGNORECASE)}
            )

        if itineraries.id:
            query = query.find(ItineraryModel.id == PydanticObjectId(itineraries.id))

        total_records = await query.count()

        query = query.skip((page - 1) * config.PAGE_SIZE).limit(config.PAGE_SIZE)
        result = await query.to_list()

        return CustomerItineraryPage(
            items=[await itinerary_model_to_customer_type(i) for i in result],
            page=page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_itinerary(itinerary: CreateItineraryInput, info: Info) -> Error:
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_tour = await TourModel.find(
            TourModel.id == PydanticObjectId(itinerary.tour),
            TourModel.customer_id == str(verified_customer.id),
        ).first_or_none()
        if not searched_tour:
            return Error(status=400, message="Invalid tour ID!")

        if not itinerary.attraction in [
            v.attraction_id for v in (searched_tour.ventures or [])
        ]:
            return Error(status=400, message="Invalid attraction ID!")

        inserted_audios_rslt = None
        if itinerary.audios:
            inserted_audios_rslt = await ItineraryAudioModel.insert_many(
                [
                    ItineraryAudioModel(
                        title=a.title,
                        image_url=a.image_url,
                        audio_url=a.audio_url,
                    )
                    for a in itinerary.audios
                ]
            )

        inserted_videos_rslt = None
        if itinerary.videos:
            inserted_videos_rslt = await ItineraryVideoModel.insert_many(
                [
                    ItineraryVideoModel(
                        title=v.title,
                        video_url=v.video_url,
                    )
                    for v in itinerary.videos
                ]
            )

        await ItineraryModel.insert_one(
            ItineraryModel(
                attraction_id=itinerary.attraction,
                customer_id=str(verified_customer.id),
                tour_id=itinerary.tour,
                title=itinerary.title or None,
                thumbnail=itinerary.thumbnail_url or None,
                story=(
                    [
                        ItineraryStoryItemDto(
                            title=s.title,
                            body=s.body,
                            subtitle=s.subtitle or None,
                            image_url=s.image_url or None,
                        )
                        for s in itinerary.story
                    ]
                    if itinerary.story
                    else None
                ),
                summary=itinerary.summary or None,
                thumbnail_url=itinerary.thumbnail_url or None,
                image_urls=itinerary.images_urls or None,
                audio_ids=(
                    [str(v) for v in inserted_audios_rslt.inserted_ids]
                    if inserted_audios_rslt
                    else None
                ),
                video_ids=(
                    [str(v) for v in inserted_videos_rslt.inserted_ids]
                    if inserted_videos_rslt
                    else None
                ),
                attraction_rating=itinerary.attraction_rating or None,
                attraction_feedback=itinerary.attraction_feedback or None,
            )
        )
        return Error(status=201, message="Itinerary created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_itinerary(itinerary: UpdateItineraryInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_itinerary = await ItineraryModel.find(
            ItineraryModel.id == PydanticObjectId(itinerary.id),
            ItineraryModel.customer_id == str(verified_customer.id),
        ).first_or_none()
        if not searched_itinerary:
            return Error(status=404, message="Itinerary not found!")

        if itinerary.title:
            searched_itinerary.title = itinerary.title

        if itinerary.story:
            searched_itinerary.story = [
                ItineraryStoryItemDto(
                    title=s.title,
                    body=s.body,
                    subtitle=s.subtitle or None,
                    image_url=s.image_url or None,
                )
                for s in itinerary.story
            ]

        if itinerary.summary:
            searched_itinerary.summary = itinerary.summary

        if itinerary.images_urls:
            searched_itinerary.image_urls = itinerary.images_urls

        if itinerary.thumbnail_url:
            searched_itinerary.thumbnail_url = itinerary.thumbnail_url

        if itinerary.videos:
            await ItineraryVideoModel.find(
                In(
                    ItineraryVideoModel.id,
                    [PydanticObjectId(v) for v in searched_itinerary.video_ids or []],
                )
            ).delete()
            inserted_videos_reslt = await ItineraryVideoModel.insert_many(
                [
                    ItineraryVideoModel(
                        title=v.title,
                        video_url=v.video_url,
                    )
                    for v in itinerary.videos
                ]
            )
            searched_itinerary.video_ids = inserted_videos_reslt.inserted_ids

        if itinerary.audios:
            await ItineraryAudioModel.find(
                In(
                    ItineraryAudioModel.id,
                    [PydanticObjectId(a) for a in searched_itinerary.audio_ids or []],
                )
            ).delete()
            inserted_audios_rslt = await ItineraryAudioModel.insert_many(
                [
                    ItineraryAudioModel(
                        title=a.title,
                        image_url=a.image_url,
                        audio_url=a.audio_url,
                    )
                    for a in itinerary.audios
                ]
            )
            searched_itinerary.audio_ids = inserted_audios_rslt.inserted_ids

        if itinerary.attraction_rating:
            searched_itinerary.attraction_rating = itinerary.attraction_rating

        if itinerary.attraction_feedback:
            searched_itinerary.attraction_feedback = itinerary.attraction_feedback

        searched_itinerary.updated_at = datetime.now(timezone.utc)
        await searched_itinerary.save()

        return await itinerary_model_to_customer_type(searched_itinerary)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_itinerary_by_append(itinerary: UpdateItineraryAppendInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_itinerary = await ItineraryModel.find(
            ItineraryModel.id == PydanticObjectId(itinerary.id),
            ItineraryModel.customer_id == str(verified_customer.id),
        ).first_or_none()
        if not searched_itinerary:
            return Error(status=404, message="Itinerary not found!")

        if itinerary.story:
            searched_itinerary.story = [
                *(searched_itinerary.story or []),
                *[
                    ItineraryStoryItemDto(
                        title=s.title,
                        body=s.body,
                        subtitle=s.subtitle or None,
                        image_url=s.image_url or None,
                    )
                    for s in itinerary.story
                ],
            ]

        if itinerary.image_urls:
            searched_itinerary.image_urls = [
                *(searched_itinerary.image_urls or []),
                *itinerary.image_urls,
            ]

        if itinerary.videos:
            inserted_videos_reslt = await ItineraryVideoModel.insert_many(
                [
                    ItineraryVideoModel(
                        title=v.title,
                        video_url=v.video_url,
                    )
                    for v in itinerary.videos
                ]
            )
            searched_itinerary.video_ids = [
                *(searched_itinerary.video_ids or []),
                *[str(v) for v in inserted_videos_reslt.inserted_ids],
            ]

        if itinerary.audios:
            inserted_audios_rslt = await ItineraryAudioModel.insert_many(
                [
                    ItineraryAudioModel(
                        title=a.title,
                        image_url=a.image_url,
                        audio_url=a.audio_url,
                    )
                    for a in itinerary.audios
                ]
            )
            searched_itinerary.audio_ids = [
                *(searched_itinerary.audio_ids or []),
                *[str(a) for a in inserted_audios_rslt.inserted_ids],
            ]

        searched_itinerary.updated_at = datetime.now(timezone.utc)
        await searched_itinerary.save()

        return await itinerary_model_to_customer_type(searched_itinerary)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
