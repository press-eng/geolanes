from lib import config
from lib.graphql.inputs.notification_event_input import NotificationEventInput
from lib.graphql.types.error import Error
from lib.graphql.types.notification_event_page import NotificationEventPage
from lib.helpers.notification_event_helper import notification_event_model_to_type
from lib.models.notification_event_model import NotificationEventModel


async def read_notification_events(notifications: NotificationEventInput = None):
    if notifications.page is None:
        notifications.page = 1
    try:
        query = (
            await NotificationEventModel.find_all()
            .skip((notifications.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = await NotificationEventModel.find_all().count()

        return NotificationEventPage(
            items=[await notification_event_model_to_type(n) for n in query],
            page=notifications.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
