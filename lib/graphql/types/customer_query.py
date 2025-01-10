from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import (
    customer_resolver,
    friend_resolver,
    itinerary_resolver,
    post_resolver,
    review_resolver,
    saved_image_resolver,
    saved_item_resolver,
    sightseeing_resolver,
    tour_suggestion_resolver,
)
from lib.graphql.types.customer import Customer
from lib.graphql.types.customer_public_page import CustomerPublicPage
from lib.graphql.types.cutomer_itinerary_page import CustomerItineraryPage
from lib.graphql.types.error import Error
from lib.graphql.types.post_page import PostPage
from lib.graphql.types.review_page import ReviewPage
from lib.graphql.types.saved_image_page import SavedImagePage
from lib.graphql.types.saved_item_page import SavedItemPage
from lib.graphql.types.tag_page_response import TagPageResponse
from lib.graphql.types.tour_suggestion import TourSuggestion

CustomerPublicPageResponse = Annotated[
    Union[CustomerPublicPage, Error], strawberry.union("CustomerPublicPageResponse")
]


@strawberry.type
class CustomerQuery:
    reviews: Annotated[
        Union[ReviewPage, Error], strawberry.union("ReviewPageResponse")
    ] = strawberry.field(resolver=review_resolver.read_customer_reviews)
    review_catgories: TagPageResponse = strawberry.field(
        resolver=review_resolver.read_review_categories,
    )

    tour_suggestion: Annotated[
        Union[TourSuggestion, Error], strawberry.union("TourSuggestionResponse")
    ] = strawberry.field(resolver=tour_suggestion_resolver.read_tour_suggstion)

    posts: Annotated[Union[PostPage, Error], strawberry.union("PostPageResponse")] = (
        strawberry.field(resolver=post_resolver.read_posts)
    )

    saved_items: Annotated[
        Union[SavedItemPage, Error], strawberry.union("SavedItemPageResponse")
    ] = strawberry.field(resolver=saved_item_resolver.read_saved_item_page)

    saved_images: Annotated[
        Union[SavedImagePage, Error], strawberry.union("SavedImagePageResponse")
    ] = strawberry.field(resolver=saved_image_resolver.read_saved_image_page)

    followed_customers: CustomerPublicPageResponse = strawberry.field(
        resolver=friend_resolver.read_followed_customers
    )
    followers: CustomerPublicPageResponse = strawberry.field(
        resolver=friend_resolver.read_followers
    )
    friend_suggestions: CustomerPublicPageResponse = strawberry.field(
        resolver=friend_resolver.read_friend_suggestions
    )

    itineraries: Annotated[
        Union[CustomerItineraryPage, Error],
        strawberry.union("CustomerItineraryResponse"),
    ] = strawberry.field(resolver=itinerary_resolver.read_customer_itineraries)

    customer_sightseeing: TagPageResponse = strawberry.field(
        resolver=sightseeing_resolver.read_customer_sightseeing
    )
    customer: Annotated[
        Union[Customer, Error], strawberry.union("CustomerResponse")
    ] = strawberry.field(resolver=customer_resolver.read_customer_by_jwt)
