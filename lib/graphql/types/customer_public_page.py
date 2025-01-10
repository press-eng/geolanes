from typing import List

import strawberry

from lib.graphql.types.customer_public import CustomerPublic


@strawberry.type
class CustomerPublicPage:
    items: List[CustomerPublic]
    page: int
    total: int
