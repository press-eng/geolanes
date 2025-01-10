from typing import List

import strawberry

from lib.graphql.types.payment import Payment


@strawberry.type
class AllPaymentRecordsPage:
    items: List[Payment]
    page: int
    total: int
