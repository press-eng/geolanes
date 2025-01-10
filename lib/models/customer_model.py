from datetime import datetime, timezone
from typing import Annotated, List, Optional

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class CustomerModel(Document):
    name: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email: Optional[str] = None
    password: Optional[bytes] = None
    phone: Optional[str] = None
    otp: Optional[str] = None
    otp_created_at: Optional[datetime] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    profession: Optional[str] = None
    hobbies: Optional[List[str]] = None
    sightseeing: Optional[List[str]] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    failed_login_attempts: Optional[int] = None
    latest_failed_login_attempt: Optional[datetime] = None
    facebook_id: Optional[str] = None
    fcm_token: Optional[str] = None
    fcm_token_updated_at: Optional[datetime] = None
    notification_event_ids: Optional[List[str]] = None
    permanently_deactivated: Optional[bool] = None
    deactivated: Optional[bool] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    contacts: Optional[List[str]] = None
    description: Optional[str] = None
    language_country_iso_code: Optional[str] = None
    currency_country_iso_code: Optional[str] = None
    travelling_unit_code: Optional[str] = None
    is_private: Optional[bool] = False

    class Settings:
        name = "customers"
