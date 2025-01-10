from datetime import datetime
from typing import List, Optional

import strawberry


@strawberry.input
class CreateCampaignInput:
    campaign_name: str
    target_audience: str
    description: Optional[str] = ""
    customer_ref: Optional[str] = "Admin"
    start_date: datetime
    end_date: datetime
    publish_status: Optional[bool] = False
    active_status: Optional[bool] = False
    campaign_type: str
    image_urls: Optional[List[str]] = strawberry.UNSET
    video_urls: Optional[List[str]] = strawberry.UNSET
    audio_urls: Optional[List[str]] = strawberry.UNSET


@strawberry.input
class campaignPaginationInput:
    page: int = 1
    campaign_type: Optional[str] = None
    campaign_status: Optional[bool] = None
    date: Optional[str] = None
    search_text: Optional[str] = None
    export_type: Optional[str] = None
    id: Optional[str] = None
    share: Optional[bool] = None


@strawberry.input
class campaignUpdateInput:
    id: str
    campaign_name: Optional[str] = None
    target_audience: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = strawberry.UNSET
    end_date: Optional[datetime] = strawberry.UNSET
    publish_status: Optional[bool] = strawberry.UNSET
    active_status: Optional[bool] = strawberry.UNSET
    is_deleted: Optional[bool] = strawberry.UNSET
    campaign_type: Optional[str] = None
    image_urls: Optional[List[str]] = strawberry.UNSET
    video_urls: Optional[List[str]] = strawberry.UNSET
    audio_urls: Optional[List[str]] = strawberry.UNSET
    customer_ref: Optional[str] = None


@strawberry.input
class campaignCsvImport:
    file_path: str
    email: str


@strawberry.input
class getCampaignInput:
    id: str


@strawberry.input
class campaignBulkOperationInput:
    ids: List[str]
    operation: str
