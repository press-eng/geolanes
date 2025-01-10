from datetime import datetime
from typing import Optional

import strawberry

from lib.graphql.types.customer_public import CustomerPublic
from lib.graphql.types.tag import Tag


@strawberry.type
class Review:
    id: str
    comment: str
    rating: int
    visit_time: datetime
    customer: CustomerPublic
    category: Optional[Tag] = None
