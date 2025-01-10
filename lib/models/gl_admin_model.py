from datetime import datetime, timezone
from typing import Annotated, List, Optional

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class GlAdminModel(Document):
    name: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email: Optional[str] = None
    password: Optional[bytes] = None
    phone: Optional[str] = None
    otp: Optional[str] = None
    otp_created_at: Optional[datetime] = None
    gender: Optional[str] = None
    notification_event_ids: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    failed_login_attempts: Optional[int] = None
    latest_failed_login_attempt: Optional[datetime] = None
    fcm_token: Optional[str] = None
    fcm_token_updated_at: Optional[datetime] = None
    permanently_deactivated: Optional[bool] = None
    deactivated: Optional[bool] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    source_id: Optional[str] = None

    class Settings:
        name = "gl_admins"
