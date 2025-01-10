import datetime
import json

import jsonpickle
from beanie import PydanticObjectId
from bidict import bidict
from strawberry.types import Info

from lib import config, utils
from lib.graphql.inputs.create_saved_item_input import CreateSavedItemInput
from lib.graphql.inputs.delete_saved_item_input import DeleteSavedItemInput
from lib.graphql.inputs.saved_item_input import SavedItemInput
from lib.graphql.types.error import Error
from lib.graphql.types.saved_item import SavedItem
from lib.graphql.types.saved_item_page import SavedItemPage
from lib.helpers.attraction_helper import attraction_model_to_type
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.itinerary_autio_helper import itinerary_audio_model_to_type
from lib.helpers.itinerary_helper import itinerary_model_to_preview_type
from lib.helpers.itinerary_video_helper import itinerary_video_model_to_type
from lib.helpers.tour_helper import tour_model_to_type
from lib.models.attraction_model import AttractionModel
from lib.models.itinerary_audio_model import ItineraryAudioModel
from lib.models.itinerary_model import ItineraryModel
from lib.models.itinerary_video_model import ItineraryVideoModel
from lib.models.saved_item_model import SavedItemModel
from lib.models.tour_model import TourModel

_types_entities = bidict(
    {
        "Tour": "tours",
        "Attraction": "attractions",
        "ItineraryPreview": "itineraries",
        "ItineraryVideo": "itinerary_videos",
        "ItineraryAudio": "itinerary_audios",
    }
)

_entities_model_classes = {
    "tours": TourModel,
    "attractions": AttractionModel,
    "itineraries": ItineraryModel,
    "itinerary_videos": ItineraryVideoModel,
    "itinerary_audios": ItineraryAudioModel,
}

_entities_types = {
    "tours": tour_model_to_type,
    "attractions": attraction_model_to_type,
    "itineraries": itinerary_model_to_preview_type,
    "itinerary_videos": itinerary_video_model_to_type,
    "itinerary_audios": itinerary_audio_model_to_type,
}


async def create_saved_item(saved_item: CreateSavedItemInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        if not saved_item.type in _types_entities.keys():
            return Error(status=400, message="Invalid item GraphQL type!")

        Model = _entities_model_classes[_types_entities[saved_item.type]]
        model = await Model.get(saved_item.item_id)
        if not model:
            return Error(status=400, message="Invalid item ID!")

        if await SavedItemModel.find_one(
            {
                "customer_id": str(customer.id),
                "entity": _types_entities[saved_item.type],
                "item_id": saved_item.item_id,
            }
        ):
            return Error(status=400, message="Item already saved!")

        await SavedItemModel.insert_one(
            SavedItemModel(
                item_id=saved_item.item_id,
                entity=_types_entities[saved_item.type],
                customer_id=str(customer.id),
            )
        )

        return Error(status=201, message="Saved item created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_saved_item_page(items: SavedItemInput, info: Info):
    page = items.page or 1

    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        if not items.type in _types_entities.keys():
            return Error(status=400, message="Invalid item GraphQL type!")

        query = (
            SavedItemModel.find(SavedItemModel.customer_id == str(customer.id))
            .skip(config.PAGE_SIZE * (page - 1))
            .limit(config.PAGE_SIZE)
        )

        if items.type:
            query = query.find(SavedItemModel.entity == _types_entities[items.type])

        searched_items = await query.to_list()

        models = [
            await _entities_model_classes[i.entity].get(PydanticObjectId(i.item_id))
            for i in searched_items
        ]

        return SavedItemPage(
            items=[
                SavedItem(
                    id=str(s.id),
                    item_json=jsonpickle.encode(
                        await _entities_types[s.entity](models[i]), unpicklable=False
                    ),
                    type=_types_entities.inverse[s.entity],
                    created_at=s.id.generation_time,
                )
                for i, s in enumerate(searched_items)
            ],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


def delete_saved_item(saved_item: DeleteSavedItemInput, info: Info):
    return utils.create_delete_resolver(
        id=saved_item.id,
        roles=["customer"],
        Model=SavedItemModel,
        success_message="Saved item deleted succesfully!",
        info=info,
    )
