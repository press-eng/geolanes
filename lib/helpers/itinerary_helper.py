from beanie import PydanticObjectId
from beanie.operators import In

from lib.graphql.types.customer_itinerary import CustomerItinerary
from lib.graphql.types.itinerary_audio import ItineraryAudio
from lib.graphql.types.itinerary_preview import ItineraryPreview
from lib.graphql.types.itinerary_story_item import ItineraryStoryItem
from lib.graphql.types.itinerary_video import ItineraryVideo
from lib.helpers.attraction_helper import attraction_model_to_type
from lib.helpers.customer_helper import customer_model_to_public_type
from lib.models.attraction_model import AttractionModel
from lib.models.customer_model import CustomerModel
from lib.models.itinerary_audio_model import ItineraryAudioModel
from lib.models.itinerary_model import ItineraryModel
from lib.models.itinerary_video_model import ItineraryVideoModel


async def itinerary_model_to_preview_type(model: ItineraryModel) -> ItineraryPreview:
    attraction_model = await AttractionModel.get(PydanticObjectId(model.attraction_id))
    attraction = await attraction_model_to_type(attraction_model)

    return ItineraryPreview(
        id=str(model.id),
        attraction=attraction,
        story=[
            ItineraryStoryItem(
                title=i.title,
                body=i.body,
                subtitle=i.subtitle,
                image_url=i.image_url,
            )
            for i in (model.story or [])
        ],
        title=model.title,
        thumbnail=model.thumbnail_url,
        description=model.summary,
        attraction_rating=model.attraction_rating,
        attraction_feedback=model.attraction_feedback,
    )


async def itinerary_model_to_customer_type(model: ItineraryModel) -> CustomerItinerary:
    attraction = await AttractionModel.get(PydanticObjectId(model.attraction_id))
    customer = await CustomerModel.get(PydanticObjectId(model.customer_id))
    audios = await ItineraryAudioModel.find(
        In(ItineraryAudioModel.id, [PydanticObjectId(a) for a in model.audio_ids or []])
    ).to_list()

    videos = await ItineraryVideoModel.find(
        In(ItineraryVideoModel.id, [PydanticObjectId(v) for v in model.video_ids or []])
    ).to_list()

    return CustomerItinerary(
        id=str(model.id),
        attraction=await attraction_model_to_type(attraction),
        story=[
            ItineraryStoryItem(
                title=i.title,
                body=i.body,
                subtitle=i.subtitle,
                image_url=i.image_url,
            )
            for i in (model.story or [])
        ],
        image_urls=model.image_urls or [],
        videos=[
            ItineraryVideo(
                id=str(v.id),
                title=v.title,
                video_url=v.video_url,
            )
            for v in videos
        ],
        audios=[
            ItineraryAudio(
                id=str(a.id),
                title=a.title,
                image_url=a.image_url,
                audio_url=a.audio_url,
            )
            for a in audios
        ],
        customer=customer_model_to_public_type(customer),
        likes=model.likes or 0,
        view_count=model.view_count or 0,
        title=model.title,
        summary=model.summary,
        thumbnail_url=model.thumbnail_url,
        attraction_rating=model.attraction_rating,
        attraction_feedback=model.attraction_feedback,
    )
