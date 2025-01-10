from datetime import datetime, timedelta

from beanie import PydanticObjectId

from lib.helpers import notification_helper
from lib.models.customer_model import CustomerModel
from lib.models.notification_model import NotificationModel
from lib.models.tour_model import TourModel
from lib.services import myfcm


async def reset_auth_locks():
    datetime_24h_ago = datetime.utcnow() - timedelta(hours=24)
    await CustomerModel.find(
        {"latest_failed_login_attempt": {"$lt": datetime_24h_ago}}
    ).set(
        {
            CustomerModel.failed_login_attempts: 0,
        }
    )


async def send_confirm_tour_notifications():
    try:
        tours = await TourModel.find(
            TourModel.start_date < (datetime.utcnow() + timedelta(hours=6)),
            TourModel.start_date > datetime.utcnow(),
        ).to_list()
        for t in tours:
            if not t.notified_confirm_tour_at:
                customer = await CustomerModel.get(PydanticObjectId(t.customer_id))
                if customer.fcm_token:
                    model = await NotificationModel.find(
                        NotificationModel.tour_id == str(t.id),
                        NotificationModel.type == "TOUR_CONFIRMATION",
                    ).first_or_none()

                    if not model:
                        model = await NotificationModel.insert_one(
                            NotificationModel(
                                type="TOUR_CONFIRMATION",
                                title_html=f"Are you proceesing with your planned tour <b>{t.title}?</b>",
                                customer_id=t.customer_id,
                                tour_id=str(t.id),
                            )
                        )

                    await myfcm.send_notification(
                        notification_helper.notification_model_to_notification(model),
                        customer.fcm_token,
                    )

                    t.notified_confirm_tour_at = model.id.generation_time
                    await t.save()

    except Exception as e:
        print(e)
