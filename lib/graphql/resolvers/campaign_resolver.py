from datetime import datetime, timezone

import strawberry
from beanie import PydanticObjectId
from starlette.requests import Request
from strawberry.types import Info

from lib import config
from lib.graphql.inputs import campaign_input
from lib.graphql.types.campaign import CampaignResponse, PaginatedCampaignList
from lib.graphql.types.error import Error
from lib.helpers.campaign_helper import (
    campaign_model_to_type,
    export_campaigns_to_csv,
    export_campaigns_to_pdf,
)
from lib.helpers.general_helper import validate_dates
from lib.helpers.gl_admin_helper import get_verified_gl_admin
from lib.models.campaign_model import CampaignModel


async def create_campaign(self, input: campaign_input.CreateCampaignInput, info: Info):
    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    searched_campaign = await CampaignModel.find_one(
        {"campaign_name": input.campaign_name, "is_deleted": False}
    )
    if searched_campaign:
        return Error(status=400, message="Campaign name already exist!")

    check_date = validate_dates(str(input.start_date), str(input.end_date))
    if check_date == False:
        return Error(status=400, message="End date in not valid!")

    campaign = CampaignModel(
        campaign_name=input.campaign_name,
        target_audience=input.target_audience,
        description=input.description,
        start_date=input.start_date,
        end_date=input.end_date,
        publish_status=input.publish_status,
        active_statsu=input.active_status,
        campaign_type=input.campaign_type,
        image_urls=input.image_urls or [],
        video_urls=input.video_urls or [],
        audio_urls=input.audio_urls or [],
        customer_ref=input.customer_ref or "Admin",
    )
    new_campaign = await campaign.insert()

    return CampaignResponse(
        status=201,
        message="Campaign created successfully!",
        campaign=await campaign_model_to_type(new_campaign),
    )


async def get_campaign(self, input: campaign_input.campaignPaginationInput, info: Info):

    # Access the Request object from the context
    request: Request = info.context["request"]

    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    print("all campaigns with filters")

    page = input.page

    page_size = config.PAGE_SIZE

    filter = {}

    if input.id and input.share:
        if input.share == True:
            campaign_data = await CampaignModel.find(
                CampaignModel.id == PydanticObjectId(input.id),
                CampaignModel.is_deleted == False,
            ).first_or_none()
            if not campaign_data:
                return Error(status=404, message="Campaign not found!")

        base_url = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}/"
        url = f"{base_url}campaign/detail/{input.id}"

        return Error(
            status=200,
            message=url,
        )
    elif input.id:
        campaign_data = await CampaignModel.find_one(
            {"_id": PydanticObjectId(input.id)}
        )
        if not campaign_data:
            return Error(status=400, message="Campaign not exist!")
        else:
            return CampaignResponse(
                status=200,
                message="Campaign found!",
                campaign=await campaign_model_to_type(campaign_data),
            )

    else:
        if input.search_text:
            # filter["campaign_name"] = {"$regex": input.search_text, "$options": "i"}
            filter = {
                "$or": [
                    {"campaign_name": {"$regex": input.search_text, "$options": "i"}},
                    {"description": {"$regex": input.search_text, "$options": "i"}},
                    {"target_audience": {"$regex": input.search_text, "$options": "i"}},
                ]
            }

        if input.campaign_type:
            filter["campaign_type"] = {"$regex": input.campaign_type, "$options": "i"}

        if input.campaign_status is not None:
            filter["publish_status"] = input.campaign_status

        if input.date:
            given_datetime = datetime.strptime(input.date, "%Y-%m-%d")

            start_date = given_datetime.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            end_date = given_datetime.replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
            )
            filter["created_at"] = {"$gte": start_date, "$lte": end_date}

        filter["is_deleted"] = False

        print("filters : ", filter)

        campaigns = (
            await CampaignModel.find(filter)
            .skip((page - 1) * page_size)
            .limit(page_size)
            .to_list()
        )

        total_count = await CampaignModel.find(filter).count()

        current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if input.export_type == "pdf":
            export_campaigns = await CampaignModel.find(filter).to_list()
            # export pdf
            pdf_file_name = "campaign_" + current_datetime + ".pdf"
            export_campaigns_to_pdf(export_campaigns, pdf_file_name)
            print(f"Campaign data exported to {pdf_file_name} successfully!")
            pdf_download_path = f"/exports/pdf/{pdf_file_name}"
            return Error(status=200, message=pdf_download_path)

        if input.export_type == "csv":
            export_campaigns = await CampaignModel.find(filter).to_list()
            # csv export
            csv_file_name = "campaign_" + current_datetime + ".csv"
            export_campaigns_to_csv(export_campaigns, csv_file_name)
            print(f"Campaign data exported to {csv_file_name} successfully!")
            csv_download_path = f"/exports/csv/{csv_file_name}"
            return Error(status=200, message=csv_download_path)

        return PaginatedCampaignList(
            status=200,
            message="Success",
            page=page,
            total_count=total_count,
            data=campaigns,
        )


async def update_campaign(input: campaign_input.campaignUpdateInput, info: Info):
    try:
        # Verify admin
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        if input.id is None:
            return Error(status=400, message="Invalid campaign ID!")

        # Find campaign
        campaign_data = await CampaignModel.find(
            CampaignModel.id == PydanticObjectId(input.id),
            CampaignModel.is_deleted == False,
        ).first_or_none()

        if not campaign_data:
            return Error(status=404, message="Campaign not found!")

        # Only update fields if they are not UNSET
        if input.campaign_name is not None:
            campaign_data.campaign_name = input.campaign_name

        if input.campaign_type is not None:
            campaign_data.campaign_type = input.campaign_type

        if input.target_audience is not None:
            campaign_data.target_audience = input.target_audience

        if input.description is not None:
            campaign_data.description = input.description

        if input.start_date is not strawberry.UNSET:
            campaign_data.start_date = input.start_date or campaign_data.start_date

        if input.end_date is not strawberry.UNSET:
            campaign_data.end_date = input.end_date or campaign_data.end_date

        if input.publish_status is not strawberry.UNSET:
            campaign_data.publish_status = input.publish_status

        if input.active_status is not strawberry.UNSET:
            campaign_data.active_status = input.active_status

        if input.image_urls is not strawberry.UNSET:
            campaign_data.image_urls = input.image_urls or campaign_data.image_urls

        if input.video_urls is not strawberry.UNSET:
            campaign_data.video_urls = input.video_urls or campaign_data.video_urls

        if input.audio_urls is not strawberry.UNSET:
            campaign_data.audio_urls = input.audio_urls or campaign_data.audio_urls

        if input.is_deleted is not strawberry.UNSET:
            campaign_data.is_deleted = input.is_deleted
            campaign_data.deleted_at = datetime.now(timezone.utc)

        if input.customer_ref is not None:
            campaign_data.customer_ref = input.customer_ref

        campaign_data.updated_at = datetime.now(timezone.utc)

        # Validate start_date and end_date if both are provided
        if input.start_date and input.end_date:
            check_date = validate_dates(str(input.start_date), str(input.end_date))
            if not check_date:
                return Error(status=400, message="End date is not valid!")
        elif input.start_date:
            end_date = campaign_data.end_date
            check_date = validate_dates(str(input.start_date), str(end_date))
            if not check_date:
                return Error(status=400, message="End date is not valid!")
        elif input.end_date:
            start_date = campaign_data.start_date
            check_date = validate_dates(str(start_date), str(input.end_date))
            if not check_date:
                return Error(status=400, message="End date is not valid!")

        # Save the updated campaign data
        await campaign_data.save()

        # Return the updated campaign response
        return CampaignResponse(
            status=200,
            message="Campaign updated successfully!",
            campaign=await campaign_model_to_type(campaign_data),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message=f"Something went wrong! {e}")


async def bulk_operations(
    self, input: campaign_input.campaignBulkOperationInput, info: Info
):

    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    if input.ids and input.operation:
        if input.operation == "delete":
            print("bulk operation : delete")
            for campaign_id in input.ids:
                campaign_data = await CampaignModel.find_one(
                    CampaignModel.id == PydanticObjectId(campaign_id)
                )
                campaign_data.is_deleted = True
                campaign_data.deleted_at = datetime.now(timezone.utc)
                campaign_data.updated_at = datetime.now(timezone.utc)
                await campaign_data.save()

            return Error(status=200, message="Deleted successfully")

        elif input.operation == "publish":
            print("bulk operation : publish")
            for campaign_id in input.ids:
                campaign_data = await CampaignModel.find_one(
                    CampaignModel.id == PydanticObjectId(campaign_id)
                )
                campaign_data.publish_status = True
                campaign_data.active_status = True
                campaign_data.published_at = datetime.now(timezone.utc)
                campaign_data.updated_at = datetime.now(timezone.utc)
                await campaign_data.save()

            return Error(status=200, message="Published successfully")

        elif input.operation == "unpublish":
            print("bulk operation : unpublish")
            for campaign_id in input.ids:
                campaign_data = await CampaignModel.find_one(
                    CampaignModel.id == PydanticObjectId(campaign_id)
                )
                campaign_data.active_status = False
                campaign_data.updated_at = datetime.now(timezone.utc)
                await campaign_data.save()

            return Error(status=200, message="Unpublished successfully")

        else:
            return Error(status=500, message="Something went wrong!")

    return Error(status=400, message="missing required fileds")
