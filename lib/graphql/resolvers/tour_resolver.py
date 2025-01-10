from datetime import datetime, timedelta
from typing import List

from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_tour_input import CreateTourInput
from lib.graphql.inputs.delete_tour_input import DeleteTourInput
from lib.graphql.inputs.tour_input import TourInput
from lib.graphql.inputs.update_tour_input import UpdateTourInput
from lib.graphql.inputs.venture_input import VentureInput
from lib.graphql.types.error import Error
from lib.graphql.types.tour_page import TourPage
from lib.helpers import notification_helper
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.tour_helper import tour_model_to_type
from lib.models.attraction_model import AttractionModel
from lib.models.dto.tour_venture_dto import TourVentureDto
from lib.models.notification_model import NotificationModel
from lib.models.tour_model import TourModel
from lib.services import myfcm


async def create_tour(tour: CreateTourInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        is_valid_attractions = all(
            [
                await AttractionModel.get(PydanticObjectId(v.attraction))
                for v in (tour.ventures or [])
            ]
        )
        if not is_valid_attractions:
            return Error(status=400, message="Invalid attraction ID!")

        if _has_duplicate_times(tour.ventures):
            return Error(
                status=400, message="Multiple ventures cannot have the same time!"
            )

        if _has_rogue_time(tour.ventures, tour.start_date, tour.end_date):
            return Error(
                status=400,
                message="Ventures cannot have time out of bounds of the tour start & end time.",
            )

        await TourModel.insert_one(
            TourModel(
                title=tour.title,
                customer_id=str(verified_customer.id),
                start_date=tour.start_date or None,
                end_date=tour.end_date or None,
                ventures=(
                    [
                        TourVentureDto(time=v.time, attraction_id=v.attraction)
                        for v in tour.ventures
                    ]
                    if type(tour.ventures) == list
                    else None
                ),
                adult_count=tour.adult_count or None,
                child_count=tour.child_count or None,
            )
        )
        return Error(status=201, message="Tour created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_tours(tour: TourInput, info: Info):
    page = tour.page or 1

    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        total_records = await TourModel.find(
            TourModel.customer_id == str(verified_customer.id)
        ).count()
        query = (
            TourModel.find(TourModel.customer_id == str(verified_customer.id))
            .skip((page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
        )

        if tour.status:
            query = query.find(TourModel.status == tour.status)

        searched_tours = await query.to_list()

        return TourPage(
            items=[await tour_model_to_type(t) for t in searched_tours],
            page=page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_tour(tour: UpdateTourInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_tour = await TourModel.find(
            TourModel.id == PydanticObjectId(tour.id),
            TourModel.customer_id == str(verified_customer.id),
        ).first_or_none()

        if not searched_tour:
            return Error(status=404, message="Invalid tour ID!")

        is_valid_attractions = all(
            [
                await AttractionModel.get(PydanticObjectId(v.attraction))
                for v in tour.ventures or []
            ]
        )
        if not is_valid_attractions:
            return Error(status=400, message="Invalid attraction ID!")

        if _has_duplicate_times(tour.ventures):
            return Error(
                status=400, message="Multiple places cannot have the same time!"
            )

        start_date = tour.start_date or searched_tour.start_date
        end_date = tour.end_date or searched_tour.end_date
        if tour.ventures and not (start_date and end_date):
            return Error(
                status=400,
                message="You cannot insert ventures without defining tour start date & end date.",
            )

        if _has_rogue_time(tour.ventures, start_date, end_date):
            return Error(
                status=400,
                message="Ventures cannot have time out of bounds of the tour start & end time.",
            )

        if tour.title:
            searched_tour.title = tour.title

        if tour.picture_url:
            searched_tour.picture_url = tour.picture_url

        if tour.ventures:
            searched_tour.ventures = [
                TourVentureDto(time=v.time, attraction_id=v.attraction)
                for v in tour.ventures
            ]
        elif tour.ventures == []:
            searched_tour.ventures = None

        if tour.status:
            if not tour.status in ["new", "ongoing", "completed"]:
                return Error(
                    status=400, message="Tour status must be new, ongoing or completed!"
                )

            searched_tour.status = tour.status

        if tour.adult_count:
            searched_tour.adult_count = tour.adult_count

        if tour.child_count:
            searched_tour.child_count = tour.child_count

        if (
            (searched_tour.start_date and searched_tour.end_date)
            and searched_tour.ventures
            and (tour.start_date or tour.end_date)
            and not tour.ventures
        ):
            searched_tour.ventures = _adjust_venture_time_acc_to_tour_time(
                tour, searched_tour
            )

        if tour.start_date:
            searched_tour.start_date = tour.start_date

        if tour.end_date:
            searched_tour.end_date = tour.end_date

        if tour.confirmed:
            inserted_notif = await NotificationModel.insert(
                NotificationModel(
                    type="START_TOUR",
                    title_html=f"Ready to embark on <b>{searched_tour.title}?</b>",
                    customer_id=str(verified_customer.id),
                    message="Start your personalised tour now to unlock exciting attractions.",
                    tour_id=str(searched_tour.id),
                    download_url="",
                )
            )
            await myfcm.send_notification(
                notification_helper.notification_model_to_notification(
                    inserted_notif),
                verified_customer.fcm_token,
            )

            searched_tour.confirmed = tour.confirmed

        searched_tour.updated_at = datetime.utcnow()
        await searched_tour.save()

        return await tour_model_to_type(searched_tour)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


def _has_duplicate_times(ventures):
    counts = {}
    for v in ventures or []:
        if counts.get(str(v.time), 0) > 0:
            return True

        counts[str(v.time)] = 1

    return False


def _has_rogue_time(
    ventures: List[VentureInput], start_time: datetime, end_time: datetime
):
    return any(start_time > v.time or end_time < v.time for v in (ventures or []))


def _adjust_venture_time_acc_to_tour_time(tour: UpdateTourInput, db_tour: TourModel):
    adjusted_ventures = db_tour.ventures
    if tour.start_date > db_tour.start_date:
        earliest_time = min([v.time for v in db_tour.ventures])
        offset = tour.start_date - earliest_time
        adjusted_ventures = [
            TourVentureDto(
                attraction_id=v.attraction_id,
                time=v.time + timedelta(days=offset.days),
            )
            for v in db_tour.ventures
        ]

    end_date = tour.end_date or db_tour.end_date
    return [v for v in adjusted_ventures if v.time < end_date]


async def delete_tour(tour: DeleteTourInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        searched_tour = await TourModel.find(
            TourModel.id == PydanticObjectId(tour.id),
            TourModel.customer_id == str(verified_customer.id),
        ).first_or_none()
        if not searched_tour:
            return Error(status=404, message="Tour not found!")

        await searched_tour.delete()

        return Error(status=200, message="Tour deleted successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
