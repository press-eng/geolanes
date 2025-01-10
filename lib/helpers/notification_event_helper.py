from lib.graphql.types.notification_event import NotificationEvent
from lib.models.notification_event_model import NotificationEventModel


async def notification_event_model_to_type(
    model: NotificationEventModel,
) -> NotificationEvent:
    return NotificationEvent(
        id=str(model.id),
        label=model.label,
        description=model.description,
    )
