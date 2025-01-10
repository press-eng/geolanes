from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import (
    campaign_resolver,
    enterprise_customer_resolver,
    gl_admin_resolver,
)
from lib.graphql.types.campaign import CampaignResponse
from lib.graphql.types.enterprise_customer import (
    BulkCustomerResponse,
    EnterpriseCustomerResponse,
    PaginatedEntCustomerList,
)
from lib.graphql.types.error import Error
from lib.graphql.types.gl_admin import GlAdmin


@strawberry.type
class GlAdminMutation:
    create_admin: Annotated[
        Union[GlAdmin, Error], strawberry.union("CreateGlAdminResponse")
    ] = strawberry.field(resolver=gl_admin_resolver.create_gl_admin)
    update_admin: Annotated[
        Union[GlAdmin, Error], strawberry.union("UpdateGlAdminResponse")
    ] = strawberry.field(resolver=gl_admin_resolver.update_gl_admin)
    delete_admin: Annotated[
        Union[GlAdmin, Error], strawberry.union("DeleteGlAdminResponse")
    ] = strawberry.field(resolver=gl_admin_resolver.delete_gl_admin)
    create_gl_admin_otp: Error = strawberry.field(
        resolver=gl_admin_resolver.create_gl_admin_otp
    )
    create_campaign: Union[CampaignResponse, Error] = strawberry.field(
        resolver=campaign_resolver.create_campaign
    )
    update_campaign: Union[CampaignResponse, Error] = strawberry.field(
        resolver=campaign_resolver.update_campaign
    )
    campaign_bulk_operation: Error = strawberry.field(
        resolver=campaign_resolver.bulk_operations
    )
    register_enterprise_customer: Union[EnterpriseCustomerResponse, Error] = (
        strawberry.field(
            resolver=enterprise_customer_resolver.create_enterprise_customer
        )
    )
    update_enterprise_customer: Annotated[
        Union[Error, PaginatedEntCustomerList],
        BulkCustomerResponse,
    ] = strawberry.field(
        resolver=enterprise_customer_resolver.update_enterprise_customer
    )

    enterprise_customer_bulk_operation: Error = strawberry.field(
        resolver=enterprise_customer_resolver.ent_customer_bulk_operations
    )
    update_ent_customer_password: Error = strawberry.field(
        resolver=enterprise_customer_resolver.update_enterprise_customer_password
    )
