from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import (
    notification_event_resolver,
    package_resolver,
    review_resolver,
    state_resolver,
    support_inquiry_resolver,
)
from lib.graphql.types.error import Error
from lib.graphql.types.notification_event_page import NotificationEventPage
from lib.graphql.types.package_page import PackagePage
from lib.graphql.types.review_page import ReviewPage
from lib.graphql.types.state_page import StatePage
from lib.graphql.types.tag_page import TagPage


@strawberry.type
class AllQuery:
    notification_events: Annotated[
        Union[NotificationEventPage, Error],
        strawberry.union("NotificationEventPageResponse"),
    ] = strawberry.field(resolver=notification_event_resolver.read_notification_events)

    support_inquiry_types: Annotated[
        Union[TagPage, Error], strawberry.union("SupportInquiryTypeResponse")
    ] = strawberry.field(resolver=support_inquiry_resolver.read_support_inquiry_types)

    states: Annotated[
        Union[StatePage, Error], strawberry.union("StatePageResponse")
    ] = strawberry.field(resolver=state_resolver.read_states)

    reviews: Annotated[
        Union[ReviewPage, Error], strawberry.union("ReviewPageResponse")
    ] = strawberry.field(resolver=review_resolver.read_reviews)

    packages: Annotated[
        Union[PackagePage, Error], strawberry.union("PackagesPageResponse")
    ] = strawberry.field(resolver=package_resolver.read_packages)
