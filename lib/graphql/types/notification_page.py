from typing import List

import strawberry

from lib.graphql.types.notification import Notification


@strawberry.type
class NotificationPage:
    items: List[Notification]
    page: int
    total: int
