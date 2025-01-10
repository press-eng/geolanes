from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import customer_resolver, post_resolver, tour_resolver
from lib.graphql.types.all_mutation import AllMutation
from lib.graphql.types.customer import Customer
from lib.graphql.types.customer_mutation import CustomerMutation
from lib.graphql.types.error import Error
from lib.graphql.types.gl_admin_mutation import GlAdminMutation
from lib.graphql.types.post import Post
from lib.graphql.types.tour import Tour


@strawberry.type
class Mutation:
    create_customer: Annotated[
        Union[Customer, Error], strawberry.union("CreateCustomerResponse")
    ] = strawberry.field(resolver=customer_resolver.create_customer)
    update_customer: Annotated[
        Union[Customer, Error], strawberry.union("UpdateCustomerResponse")
    ] = strawberry.field(resolver=customer_resolver.update_customer)

    create_customer_otp: Error = strawberry.field(
        resolver=customer_resolver.create_customer_otp
    )

    create_tour: Error = strawberry.field(resolver=tour_resolver.create_tour)
    update_tour: Annotated[
        Union[Tour, Error], strawberry.union("UpdateTourResponse")
    ] = strawberry.field(resolver=tour_resolver.update_tour)
    delete_tour: Error = strawberry.field(resolver=tour_resolver.delete_tour)

    create_post: Annotated[
        Union[Post, Error], strawberry.union("CreatePostResponse")
    ] = strawberry.field(resolver=post_resolver.create_post)

    all: AllMutation = strawberry.field(resolver=lambda: AllMutation())
    customer: CustomerMutation = strawberry.field(resolver=lambda: CustomerMutation())
    gl_admin: GlAdminMutation = strawberry.field(resolver=lambda: GlAdminMutation())
