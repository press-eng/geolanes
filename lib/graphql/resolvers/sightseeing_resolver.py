from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.delete_customer_sightseeing_input import (
    DeleteCustomerSightseeingInput,
)
from lib.graphql.inputs.sightseeing_input import SightseeingInput
from lib.graphql.types.error import Error
from lib.graphql.types.tag import Tag
from lib.graphql.types.tag_page import TagPage
from lib.helpers.customer_helper import get_verified_customer
from lib.models.sightseeing_model import SightseeingModel


async def read_signtseeing(sightseeing: Optional[SightseeingInput] = None):
    sightseeing = sightseeing or SightseeingInput(page=1)

    try:
        searched_sightseeing = (
            await SightseeingModel.find(
                {
                    "$or": [
                        {"source_customer_id": {"$exists": False}},
                        {"source_customer_id": []},
                    ]
                }
            )
            .skip((sightseeing.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = len(searched_sightseeing)

        return TagPage(
            items=[Tag(id=str(s.id), label=s.label) for s in searched_sightseeing],
            page=sightseeing.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_customer_sightseeing(
    info: Info, sightseeing: Optional[SightseeingInput] = None
):
    sightseeing = sightseeing or SightseeingInput(page=1)

    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        searched_sightseeing = (
            await SightseeingModel.find(
                {"source_customer_id": {"$in": [str(customer.id)]}}
            )
            .skip((sightseeing.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = len(searched_sightseeing)

        return TagPage(
            items=[Tag(id=str(s.id), label=s.label) for s in searched_sightseeing],
            page=sightseeing.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_customer_sightseeing(
    info: Info, sightseeing: DeleteCustomerSightseeingInput
):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        if sightseeing.sightseeing_id:
            searched_sightseeing = await SightseeingModel.get(
                PydanticObjectId(sightseeing.sightseeing_id)
            )
            if not searched_sightseeing:
                return Error(status=404, message="Sightseeing not found!")

            if str(customer.id) not in searched_sightseeing.source_customer_id:
                return Error(
                    status=404, message="Customer does not have this sightseeing!"
                )

            searched_sightseeing.source_customer_id.remove(str(customer.id))
            searched_sightseeing.updated_at = datetime.now()
            await searched_sightseeing.save()

        if not sightseeing.sightseeing_id:
            searched_sightseeings = await SightseeingModel.find(
                {"source_customer_id": str(customer.id)}
            ).to_list()
            for sight in searched_sightseeings:
                sight.source_customer_id.remove(str(customer.id))
                sight.updated_at = datetime.now()
                await sight.save()

        return Error(status=200, message="Sightseeing removed successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
