from typing import List

import strawberry

from lib.graphql.types.notification_event import NotificationEvent


@strawberry.type
class NotificationEventPage:
    items: List[NotificationEvent]
    page: int
    total: int
