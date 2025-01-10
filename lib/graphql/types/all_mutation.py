from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import payment_resolver, support_inquiry_resolver
from lib.graphql.types.error import Error
from lib.graphql.types.payment import Payment


@strawberry.type
class AllMutation:
    create_support_inquiry: Error = strawberry.field(
        resolver=support_inquiry_resolver.create_support_inquiry
    )
    create_payment: Annotated[
        Union[Payment, Error], strawberry.union("CreatePaymentResponse")
    ] = strawberry.field(resolver=payment_resolver.create_payment)
