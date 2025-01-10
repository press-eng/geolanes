from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import Or
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.notification_input import NotificationInput
from lib.graphql.inputs.update_notification_input import UpdateNotificationInput
from lib.graphql.types.error import Error
from lib.graphql.types.notification_page import NotificationPage
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.notification_helper import notification_model_to_type
from lib.models.notification_model import NotificationModel


async def read_notifications(notifications: NotificationInput, info: Info):
    page = notifications.page or 1
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        query = (
            NotificationModel.find(NotificationModel.customer_id == str(customer.id))
            .limit(config.PAGE_SIZE)
            .skip((page - 1) * config.PAGE_SIZE)
        )

        if notifications.flagged:
            query = query.find(NotificationModel.flagged == True)

        if notifications.flagged == False:
            query = query.find(
                Or(
                    NotificationModel.flagged == False,
                    NotificationModel.flagged == None,
                )
            )

        if notifications.search:
            query = query.find({"$text": {"$search": notifications.search}})

        if notifications.read:
            query = query.find(NotificationModel.read == True)

        if notifications.read == False:
            query = query.find(
                Or(
                    NotificationModel.read == False,
                    NotificationModel.read == None,
                )
            )

        records = await query.to_list()
        total_records = await query.count()

        return NotificationPage(
            items=[await notification_model_to_type(n) for n in records],
            page=page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_notification(notification: UpdateNotificationInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        searched_notification = await NotificationModel.find(
            NotificationModel.id == PydanticObjectId(notification.id),
            NotificationModel.customer_id == str(customer.id),
        ).first_or_none()

        if not searched_notification:
            return Error(status=404, message="Invalid notification ID!")

        if notification.flagged:
            searched_notification.flagged = True

        if notification.read:
            searched_notification.read = True

        searched_notification.updated_at = datetime.utcnow()

        await searched_notification.save()
        return await notification_model_to_type(searched_notification)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
