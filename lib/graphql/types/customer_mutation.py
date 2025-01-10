from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import (
    attraction_resolver,
    customer_resolver,
    friend_resolver,
    itinerary_resolver,
    notification_resolver,
    payment_resolver,
    post_resolver,
    review_resolver,
    saved_image_resolver,
    saved_item_resolver,
    sightseeing_resolver,
)
from lib.graphql.types.attraction import Attraction
from lib.graphql.types.customer_itinerary import CustomerItinerary
from lib.graphql.types.error import Error
from lib.graphql.types.notification import Notification
from lib.graphql.types.post import Post

UpdateItineraryResponse = Annotated[
    Union[CustomerItinerary, Error], strawberry.union("UpdateItineraryResponse")
]


@strawberry.type
class CustomerMutation:
    create_review: Error = strawberry.field(resolver=review_resolver.create_review)
    delete_review: Error = strawberry.field(resolver=review_resolver.delete_review)

    create_itinerary: Error = strawberry.field(
        resolver=itinerary_resolver.create_itinerary
    )
    update_itinerary: UpdateItineraryResponse = strawberry.field(
        resolver=itinerary_resolver.update_itinerary
    )
    update_itinerary_by_append: UpdateItineraryResponse = strawberry.field(
        resolver=itinerary_resolver.update_itinerary_by_append
    )

    update_notification: Annotated[
        Union[Notification, Error], strawberry.union("UpdateNotificationResponse")
    ] = strawberry.field(resolver=notification_resolver.update_notification)

    create_saved_item: Error = strawberry.field(
        resolver=saved_item_resolver.create_saved_item
    )
    delete_saved_item: Error = strawberry.field(
        resolver=saved_item_resolver.delete_saved_item
    )

    create_saved_image: Error = strawberry.field(
        resolver=saved_image_resolver.create_saved_image
    )
    delete_saved_image: Error = strawberry.field(
        resolver=saved_image_resolver.delete_saved_image
    )

    delete_customer: Error = strawberry.field(
        resolver=customer_resolver.delete_customer
    )

    create_attraction: Error = strawberry.field(
        resolver=attraction_resolver.create_attraction
    )
    update_attraction: Annotated[
        Union[Attraction, Error], strawberry.union("UpdateAttractionResponse")
    ] = strawberry.field(resolver=attraction_resolver.update_attraction)

    create_followed_customer: Error = strawberry.field(
        resolver=friend_resolver.create_followed_customer
    )
    delete_followed_customer: Error = strawberry.field(
        resolver=friend_resolver.delete_followed_customer
    )
    delete_follower: Error = strawberry.field(resolver=friend_resolver.delete_follower)

    update_post: Annotated[
        Union[Post, Error], strawberry.union("UpdatePostResponse")
    ] = strawberry.field(resolver=post_resolver.update_post)

    delete_customer_sightseeing: Error = strawberry.field(
        resolver=sightseeing_resolver.delete_customer_sightseeing
    )
