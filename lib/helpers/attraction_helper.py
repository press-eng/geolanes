from beanie import PydanticObjectId
from beanie.operators import All, In

from lib import config
from lib.graphql.types.attraction import Attraction
from lib.graphql.types.city import City
from lib.graphql.types.review_page import ReviewPage
from lib.graphql.types.tag import Tag
from lib.helpers.review_helper import review_model_to_type
from lib.models.attraction_category_model import AttractionCategoryModel
from lib.models.attraction_model import AttractionModel
from lib.models.review_model import ReviewModel
from lib.models.sightseeing_model import SightseeingModel


async def attraction_model_to_type(model: AttractionModel) -> Attraction:
    review_query = ReviewModel.find(ReviewModel.attraction_id == str(model.id)).limit(
        config.PAGE_SIZE
    )
    review_models = await review_query.to_list()
    review_count = await review_query.count()
    sightseeing_data = []
    if model.sightseeing_ids:
        sightseeing_ids = [PydanticObjectId(id) for id in model.sightseeing_ids]
        sightseeing_data = await SightseeingModel.find(
            In(SightseeingModel.id, sightseeing_ids)
        ).to_list()
    searched_attraction_type = None
    if model.attraction_category_id:
        searched_attraction_type = await AttractionCategoryModel.find(
            AttractionCategoryModel.id == PydanticObjectId(model.attraction_category_id)
        ).first_or_none()

    return Attraction(
        id=str(model.id),
        title=model.title,
        images=model.images or [],
        reviews=ReviewPage(
            items=[await review_model_to_type(r) for r in review_models],
            page=1,
            total=review_count,
        ),
        city=(
            City(
                id="",
                label=model.city,
                country=Tag(
                    id="",
                    label=model.country,
                ),
            )
            if model.city and model.country
            else None
        ),
        always_open=model.always_open or False,
        address=model.address,
        zip_code=model.zip_code,
        attraction_type=(
            Tag(
                id=searched_attraction_type.id,
                label=searched_attraction_type.label,
            )
            if searched_attraction_type
            else None
        ),
        lat=model.lat,
        lng=model.lng,
        centre_offset=model.centre_offset,
        visit_count=model.visit_count,
        restaurant_count=model.restaurant_count,
        accomodation_count=model.accomodation_count,
        rating=model.rating,
        sightseeing=(
            [Tag(id=str(s.id), label=s.label) for s in sightseeing_data]
            if sightseeing_data
            else []
        ),
        description=model.description,
        opening_time=model.opening_time,
        closing_time=model.closing_time,
        contact_number=model.contact_number,
    )
