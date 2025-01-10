from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import (
    attraction_resolver,
    campaign_resolver,
    customer_resolver,
    enterprise_customer_resolver,
    hobby_resolver,
    itinerary_resolver,
    notification_resolver,
    profession_resolver,
    sightseeing_resolver,
    tour_resolver,
)
from lib.graphql.types.all_query import AllQuery
from lib.graphql.types.attraction_page import AttractionPage
from lib.graphql.types.campaign import (
    AllCampaignResponse,
    CampaignResponse,
    PaginatedCampaignList,
)
from lib.graphql.types.customer import Customer
from lib.graphql.types.customer_query import CustomerQuery
from lib.graphql.types.enterprise_customer import (
    AllCustomerResponse,
    BulkCustomerResponse,
    EnterpriseCustomerResponse,
    PaginatedEntCustomerList,
)
from lib.graphql.types.error import Error
from lib.graphql.types.gl_admin_query import GlAdminQuery
from lib.graphql.types.itinerary_preview_page import ItineraryPreviewPage
from lib.graphql.types.notification_page import NotificationPage
from lib.graphql.types.tag_page_response import TagPageResponse
from lib.graphql.types.tour_page import TourPage


@strawberry.type
class Query:
    customer: Annotated[
        Union[Customer, Error], strawberry.union("CustomerResponse")
    ] = strawberry.field(resolver=customer_resolver.read_customer)

    hobbies: TagPageResponse = strawberry.field(resolver=hobby_resolver.read_hobbies)

    professions: TagPageResponse = strawberry.field(
        resolver=profession_resolver.read_professions
    )

    sightseeing: TagPageResponse = strawberry.field(
        resolver=sightseeing_resolver.read_signtseeing
    )

    itinerary_previews: Annotated[
        Union[ItineraryPreviewPage, Error],
        strawberry.union("ItineraryPreviewPageResponse"),
    ] = strawberry.field(resolver=itinerary_resolver.read_itinerary_previews)

    attractions: Annotated[
        Union[AttractionPage, Error], strawberry.union("AttractionPageResponse")
    ] = strawberry.field(resolver=attraction_resolver.read_attractions)

    tours: Annotated[Union[TourPage, Error], strawberry.union("TourPageResponse")] = (
        strawberry.field(resolver=tour_resolver.read_tours)
    )

    customer_notifications: Annotated[
        Union[NotificationPage, Error], strawberry.union("NotificationPageResponse")
    ] = strawberry.field(resolver=notification_resolver.read_notifications)

    all_campaigns: Annotated[
        Union[CampaignResponse, Error, PaginatedCampaignList], AllCampaignResponse
    ] = strawberry.field(resolver=campaign_resolver.get_campaign)

    all_customers: Annotated[
        Union[EnterpriseCustomerResponse, Error, PaginatedEntCustomerList],
        AllCustomerResponse,
    ] = strawberry.field(resolver=enterprise_customer_resolver.get_enterprise_customers)

    customer_query: CustomerQuery = strawberry.field(resolver=lambda: CustomerQuery())

    all: AllQuery = strawberry.field(resolver=lambda: AllQuery())

    gl_admin: GlAdminQuery = strawberry.field(resolver=lambda: GlAdminQuery())
