from typing import List, Optional

import strawberry

from lib.graphql.types.notification_event import NotificationEvent
from lib.graphql.types.tag import Tag


@strawberry.type
class Customer:
    id: str
    name: str
    jwt: str
    notification_events: List[NotificationEvent]
    hobbies: List[Tag]
    sightseeing: List[Tag]
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    profession: Optional[Tag] = None
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    language: Optional[Tag] = None
    currency: Optional[Tag] = None
    travelling_unit: Optional[Tag] = None
    is_private: Optional[bool] = None
