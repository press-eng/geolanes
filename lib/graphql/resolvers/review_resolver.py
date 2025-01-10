from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_review_input import CreateReviewInput
from lib.graphql.inputs.customer_review_input import CustomerReviewInput
from lib.graphql.inputs.delete_review_input import DeleteReviewInput
from lib.graphql.inputs.review_category_input import ReviewCategoryInput
from lib.graphql.inputs.review_input import ReviewInput
from lib.graphql.types.error import Error
from lib.graphql.types.review_page import ReviewPage
from lib.graphql.types.tag_page import TagPage
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.review_helper import (
    review_category_model_to_type,
    review_model_to_type,
)
from lib.models.attraction_model import AttractionModel
from lib.models.review_category_model import ReviewCategoryModel
from lib.models.review_model import ReviewModel


async def create_review(review: CreateReviewInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        if review.rating > 5 or review.rating < 1:
            return Error(status=400, message="Rating must be between 1 and 5!")

        attraction = await AttractionModel.get(PydanticObjectId(review.attraction))
        if not attraction:
            return Error(status=400, message="Invalid attraction ID!")

        existing_review = await ReviewModel.find_one(
            {
                ReviewModel.attraction_id: review.attraction,
                ReviewModel.customer_id: str(verified_customer.id),
            }
        )
        if existing_review:
            return Error(status=400, message="Your review already exists!")

        review_category = (
            await ReviewCategoryModel.get(PydanticObjectId(review.category))
            if review.category
            else None
        )
        if review.category and not review_category:
            return Error(status=400, message="Invalid review category!")

        await ReviewModel.create(
            ReviewModel(
                rating=review.rating,
                comment=review.comment,
                visit_time=review.visit_time,
                attraction_id=review.attraction,
                customer_id=str(verified_customer.id),
                category_id=review.category or None,
                images=review.images or None,
                accessibility=review.accessibility or None,
                popularity=review.popularity or None,
                safety=review.safety or None,
                entertainment=review.entertainment or None,
                organisation=review.organisation or None,
                recommended=review.recommended or None,
            )
        )

        attraction.rating = await ReviewModel.find(
            ReviewModel.attraction_id == review.attraction
        ).avg(ReviewModel.rating)
        await attraction.save()

        return Error(status=201, message="Review created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_reviews(review: ReviewInput):
    page = review.page or 1

    try:
        reviews = (
            await ReviewModel.find(ReviewModel.attraction_id == review.attraction)
            .skip((page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = await ReviewModel.find_all().count()

        return ReviewPage(
            items=[await review_model_to_type(r) for r in reviews],
            page=page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_customer_reviews(reviews: CustomerReviewInput, info: Info):
    page = reviews.page or 1

    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        query = (
            ReviewModel.find()
            .skip(config.PAGE_SIZE * (page - 1))
            .limit(config.PAGE_SIZE)
        )
        searched_reviews = await query.to_list()

        return ReviewPage(
            items=[await review_model_to_type(r) for r in searched_reviews],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_review(review: DeleteReviewInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_review = await ReviewModel.get(PydanticObjectId(review.id))
        if not searched_review:
            return Error(status=404, message="Invalid review ID!")

        await searched_review.delete()

        return Error(status=200, message="Review deleted successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_review_categories(categories: ReviewCategoryInput):
    page = categories.page or 1

    try:
        query = (
            ReviewCategoryModel.find_all()
            .skip(config.PAGE_SIZE * (page - 1))
            .limit(config.PAGE_SIZE)
        )
        searched_categories = await query.to_list()

        return TagPage(
            items=[await review_category_model_to_type(c) for c in searched_categories],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
