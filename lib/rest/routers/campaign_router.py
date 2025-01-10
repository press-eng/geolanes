from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import HTTPException, Request
from fastapi.routing import APIRouter

from lib.graphql.types.error import Error
from lib.models.campaign_model import CampaignModel

router = APIRouter()


@router.get("/detail/{campaign_id}", response_model=CampaignModel)
async def get_campaign(campaign_id: str):
    campaign_object_id = PydanticObjectId(campaign_id)
    campaign = await CampaignModel.find_one({"_id": campaign_object_id})

    if campaign:
        return campaign

    raise HTTPException(status_code=404, detail="Campaign not found")
