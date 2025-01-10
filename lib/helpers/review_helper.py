from beanie import PydanticObjectId

from lib.graphql.types.customer_public import CustomerPublic
from lib.graphql.types.review import Review
from lib.graphql.types.tag import Tag
from lib.models.customer_model import CustomerModel
from lib.models.review_category_model import ReviewCategoryModel
from lib.models.review_model import ReviewModel


async def review_model_to_type(model: ReviewModel) -> Review:
    customer_model = await CustomerModel.get(PydanticObjectId(model.customer_id))
    if model.category_id:
        searched_category = await ReviewCategoryModel.get(PydanticObjectId(model.category_id))
    return Review(
        id=str(model.id),
        rating=model.rating,
        comment=model.comment,
        visit_time=model.visit_time,
        customer=CustomerPublic(
            id=customer_model.id,
            name=customer_model.name,
            avatar_url=customer_model.avatar_url,
        ),
        category=(
            Tag(id=str(searched_category.id), label=searched_category.label)
            if model.category_id
            else None
        ),
    )


async def review_category_model_to_type(model: ReviewCategoryModel) -> Tag:
    return Tag(
        id=str(model.id),
        label=model.label,
    )
