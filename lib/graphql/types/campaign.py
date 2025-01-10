from datetime import datetime
from typing import List, Optional

import strawberry

from lib.graphql.types.error import Error


@strawberry.type
class Campaign:
    id: strawberry.ID
    campaign_name: str
    target_audience: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    publish_status: Optional[bool] = False
    active_status: Optional[bool] = False
    impressions_count: Optional[int] = 0
    clicks_count: Optional[int] = 0
    earning: Optional[float] = 0.0
    campaign_type: str
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    image_urls: Optional[List[str]] = None
    video_urls: Optional[List[str]] = None
    audio_urls: Optional[List[str]] = None
    published_at: Optional[datetime] = None
    customer_ref: str


@strawberry.type
class PaginatedCampaignList:
    status: int
    message: str
    page: int
    total_count: int
    data: List[Campaign]


@strawberry.type
class CampaignResponse:
    status: int
    message: str
    campaign: Campaign


CampaignResponseWithError = strawberry.union(
    "CampaignResponse", (CampaignResponse, Error)
)

AllCampaignResponse = strawberry.union(
    "AllCampaignResponse", (CampaignResponse, PaginatedCampaignList, Error)
)
