import strawberry


@strawberry.type
class NotificationEvent:
    id: strawberry.ID
    label: str
    description: str
