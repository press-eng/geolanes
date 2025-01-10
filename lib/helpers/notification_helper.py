from lib.graphql.types.notification import Notification
from lib.models.notification_model import NotificationModel


async def notification_model_to_type(model: NotificationModel) -> Notification:
    return Notification(
        id=str(model.id),
        type=model.type,
        title_html=model.title_html,
        read=model.read,
        message=model.message,
        flagged=model.flagged or False,
        time=model.id.generation_time,
        download_url=model.download_url,
        tour_id=model.tour_id,
    )


def notification_model_to_notification(model: NotificationModel) -> dict:
    return {
        "id": str(model.id),
        "type": model.type,
        "title_html": model.title_html,
        "read": model.read,
        "time": model.id.generation_time.isoformat(),
        "message": model.message,
        "flagged": model.flagged or False,
        "tour_id": model.tour_id,
        "download_url": model.download_url,
    }
